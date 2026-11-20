#!/usr/bin/env python3
"""Record a PaveWatch camera/LiDAR run on Linux with sensor-native timing.

Pi example (activate a UV environment with system Picamera2 and libcamera):
  uv run --no-project python collect_v2.py --out /media/survey --seconds 30
  Add --profile imx708-bench --listen 192.168.0.100 --lidar-source 192.168.0.1

Use imx219-bench for Camera Module 2 and imx708-flight for full-resolution
Camera Module 3 at 3 fps. The LiDAR must already be streaming Compact UDP.

Hardware-free example:
  uv run --no-project python collect_v2.py --out /tmp/pavewatch --seconds 2 --simulate
"""
import argparse
import base64
from collections import Counter, deque
from contextlib import ExitStack, closing
from datetime import datetime, timezone
import hashlib
import io
from importlib.metadata import PackageNotFoundError, version
import json
import math
import multiprocessing
import os
from pathlib import Path
import platform
from queue import Empty, Full, Queue
import re
import select
import shutil
import signal
import socket
import struct
import subprocess
import sys
from threading import Event, Thread
import time
import traceback
import zlib

import lidar_telemetry as telemetry
from recorder_watchdog import StreamProgress


NS = 1_000_000_000
RAW_HEADER = struct.Struct("<QI")
COMPACT_HEADER = struct.Struct("<IIQQII")
MOD_HEADER = struct.Struct("<QQIIII")
# Linux asm-generic socket option IDs, used by both Pi 4 and x86-64 Linux.
SO_TIMESTAMPNS_NEW = 64
SO_TIMESTAMPNS_OLD = 35
SO_RXQ_OVFL = getattr(socket, "SO_RXQ_OVFL", 40)
PROFILES = {
    "imx708-bench": ("imx708", (2304, 1296), 10, 12.0),
    "imx219-bench": ("imx219", (1640, 1232), 10, 10.0),
    "imx219-full": ("imx219", (3280, 2464), 10, 5.0),
    "imx708-flight": ("imx708", (4608, 2592), 10, 3.0),
}
FRAME_METADATA = {
    "SensorTimestamp": "SensorTimestamp_ns",
    "ExposureTime": "ExposureTime_us",
    "FrameDuration": "FrameDuration_us",
}


def write_jsonl(stream, record):
    stream.write(json.dumps(record, separators=(",", ":"), allow_nan=False) + "\n")


def sync_file(stream):
    stream.flush()
    os.fsync(stream.fileno())


def sync_directory(path):
    directory = os.open(path, os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def file_sha256(stream):
    digest = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(block)
    return digest.hexdigest()


def write_json(path, data):
    temporary = path.with_suffix(".partial")
    with temporary.open("w") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")
        sync_file(stream)
    temporary.replace(path)
    sync_directory(path.parent)


def json_values(value):
    """Convert libcamera values without changing integer timestamps."""
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, dict):
        return {str(k): json_values(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_values(v) for v in value]
    if all(hasattr(value, field) for field in ("x", "y", "width", "height")):
        return {field: getattr(value, field) for field in ("x", "y", "width", "height")}
    return str(value)


def parse_compact(payload):
    """Index acquisition endpoints and counters. Keep all bytes in raw.bin."""
    if len(payload) < COMPACT_HEADER.size + 4:
        raise ValueError("short header")
    magic, command, counter, tx_us, version_, size = COMPACT_HEADER.unpack_from(payload)
    if (magic, command) != (0x02020202, 1) or version_ not in (3, 4):
        raise ValueError("unsupported Compact Type 1 header")
    payload_end = len(payload) - 4
    if zlib.crc32(memoryview(payload)[:payload_end]) != struct.unpack_from("<I", payload, payload_end)[0]:
        raise ValueError("CRC32 mismatch")

    offset = COMPACT_HEADER.size
    modules = []
    while size:
        end = offset + size
        trailer_size = 12 if version_ == 4 else 8
        if end > payload_end or size < MOD_HEADER.size + trailer_size:
            raise ValueError("invalid module size")
        segment, frame, sender, lines, beams, echoes = MOD_HEADER.unpack_from(payload, offset)
        o = offset + MOD_HEADER.size
        if o + 28 * lines + trailer_size > end:
            raise ValueError("invalid module line count")
        endpoints = struct.unpack_from(f"<{2 * lines}Q", payload, o)
        module = {
            "segment_counter": segment, "frame_number": frame, "sender_id": sender,
            "line_count": lines, "beams_per_line": beams, "echoes_per_beam": echoes,
            "timestamp_start_us": endpoints[:lines], "timestamp_stop_us": endpoints[lines:],
        }
        if lines == 1:
            module["scan_geometry"] = telemetry.scan_geometry(
                payload, o, o + 28 * lines + trailer_size, end, beams, echoes
            )
        modules.append(module)
        size = struct.unpack_from("<I", payload, o + 28 * lines + (4 if version_ == 4 else 0))[0]
        offset = end
    if offset != payload_end or not modules:
        raise ValueError("missing or incomplete modules")
    return {"telegram_counter": counter, "transmit_timestamp_us": tx_us,
            "telegram_version": version_, "modules": modules}


def udp_receiver(listen, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)
        configured = {}
        for name, options in (("kernel_realtime_timestamp", (SO_TIMESTAMPNS_NEW, SO_TIMESTAMPNS_OLD)),
                              ("kernel_rxq_overflow", (SO_RXQ_OVFL,))):
            configured[name] = None
            for option in options:
                try:
                    sock.setsockopt(socket.SOL_SOCKET, option, 1)
                    configured[name] = option
                    break
                except OSError:
                    continue
        sock.bind((listen, port))
        sock.settimeout(0.05)
        configured["bound_address"] = sock.getsockname()
        configured["receive_buffer_bytes"] = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        return sock, configured
    except BaseException:
        sock.close()
        raise


def udp_ancillary(messages, flags):
    wall_ns = overflow = None
    if flags & socket.MSG_CTRUNC:
        return wall_ns, overflow
    for level, kind, data in messages:
        if level != socket.SOL_SOCKET:
            continue
        if kind in (SO_TIMESTAMPNS_NEW, SO_TIMESTAMPNS_OLD):
            layout = struct.Struct("=qq" if kind == SO_TIMESTAMPNS_NEW else "@ll")
            if len(data) >= layout.size:
                seconds, ns = layout.unpack_from(data)
                wall_ns = seconds * NS + ns
        elif kind == SO_RXQ_OVFL and len(data) >= 4:
            overflow = struct.unpack_from("=I", data)[0]
    return wall_ns, overflow


def simulated_datagrams(stop):
    """Produce 50 Hz scans of a flat surface and 100 Hz stationary IMU samples."""
    beam = struct.Struct("<6HBH")
    segments = []
    for segment in range(5):
        first_angle_deg = -138 + 60 * segment
        last_slot = min(239, int((138 - first_angle_deg) / 0.25))
        beams = []
        for slot in range(240):
            angle_deg = first_angle_deg + 0.25 * slot
            angle_rad = math.radians(angle_deg)
            in_range = abs(angle_deg) <= 60
            distance_mm = round(3000 / math.cos(angle_rad)) if in_range else 0
            azimuth = round(16384 + 5215 * angle_rad)
            beams.append(beam.pack(distance_mm, 100 if in_range else 0, 0, 0, 0, 0,
                                   int(in_range), azimuth))
        segments.append((last_slot, math.radians(first_angle_deg),
                         math.radians(first_angle_deg + 0.25 * last_slot), b"".join(beams)))

    first_tx_us = time.time_ns() // 1000
    telegram = 0
    first_due = time.monotonic_ns()
    imu_index = 0
    while True:
        scan_us, imu_us = 4000 * telegram, 10_000 * imu_index
        due = first_due + 1000 * min(scan_us, imu_us)
        if stop.wait(max(0, (due - time.monotonic_ns()) / NS)):
            return
        if imu_us <= scan_us:
            packet = telemetry.IMU_PACKET.pack(
                telemetry.MAGIC, 2, 1, 0., 0., 9.80665, 0., 0., 0., 1., 0., 0., 0.,
                first_tx_us + imu_us, 0,
            )[:-4]
            yield packet + struct.pack("<I", zlib.crc32(packet)), [], 0, ("127.0.0.1", 0)
            imu_index += 1
            continue
        frame, segment = divmod(telegram, len(segments))
        last_slot, theta_start, theta_stop, beams = segments[segment]
        tx_us = first_tx_us + scan_us
        start_us = tx_us - 3800
        stop_us = start_us + 15 * last_slot
        module = (MOD_HEADER.pack(segment, frame, 1, 1, 240, 3)
                  + struct.pack("<QQffffI4B", start_us, stop_us, 0., theta_start, theta_stop, 1., 0, 0, 3, 3, 0)
                  + beams)
        packet = COMPACT_HEADER.pack(0x02020202, 1, telegram + 1, tx_us, 4, len(module)) + module
        yield packet + struct.pack("<I", zlib.crc32(packet)), [], 0, ("127.0.0.1", 0)
        telegram += 1


def publish_loopback(stop, port, imu_port, bound, ready):
    while not bound.wait(0.05):
        if stop.is_set():
            return
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
        ready.set()
        for packet, _, _, _ in simulated_datagrams(stop):
            if stop.is_set():
                break
            destination = imu_port if packet.startswith(telemetry.IMU_HEADER) else port
            sender.sendto(packet, ("127.0.0.1", destination))


def lidar(a, run, ready, start, stop, cutoff, stats, health, bound, progress):
    stats["kernel_rxq_last_reported"] = None
    last_receive = None
    last_valid_receive = None
    last_kernel_receive = None
    last_native = {}
    last_clock_observation_ns = None
    last_epoch_hint = None
    last_sync = time.monotonic_ns()
    next_gap_ns = None
    outage_reported = False
    startup_good = 0
    bad_epoch_packets = 0
    gap_ns = int(a.lidar_gap_ms * 1e6)
    duration_ns = round(a.seconds * NS)
    ancillary_buffer = socket.CMSG_SPACE(16) + socket.CMSG_SPACE(4)
    offset = 0
    digest = hashlib.sha256()
    imu_offset = 0
    imu_digest = hashlib.sha256()
    imu_stats = Counter()
    stats["imu"] = imu_stats
    scan_observation = telemetry.ScanObservation()
    scan_progress, imu_progress = progress.get("lidar"), progress.get("imu")
    folder = run / "lidar"
    imu_folder = run / "imu"
    with ExitStack() as stack:
        sockets = {}
        if a.simulate:
            simulated = stack.enter_context(closing(simulated_datagrams(stop)))
            stats["socket"] = {"simulation": True}
        else:
            sock, stats["socket"] = udp_receiver(a.listen, a.port)
            sockets[stack.enter_context(sock)] = a.port
            if a.imu_receive_port != a.port:
                try:
                    imu_socket, imu_stats["socket"] = udp_receiver(a.listen, a.imu_receive_port)
                    sockets[stack.enter_context(imu_socket)] = a.imu_receive_port
                except OSError as exc:
                    imu_stats["bind_error"] = str(exc)
        raw = stack.enter_context((folder / "raw.bin").open("wb"))
        packets = stack.enter_context((folder / "packets.jsonl").open("w"))
        imu_raw = stack.enter_context((imu_folder / "raw.bin").open("wb"))
        imu_samples = stack.enter_context((imu_folder / "samples.jsonl").open("w"))
        bound.set()
        previous_port = a.port
        try:
            if a.simulate:
                ready.set()
                while not start.wait(0.05) and not stop.is_set():
                    pass
            while not stop.is_set() and time.monotonic_ns() < cutoff.value:
                if start.is_set() and next_gap_ns is None:
                    next_gap_ns = cutoff.value - duration_ns + gap_ns
                payload, port = None, a.port
                try:
                    if a.simulate:
                        payload, ancillary, flags, source = next(simulated)
                        if payload.startswith(telemetry.IMU_HEADER):
                            port = a.imu_receive_port
                    else:
                        readable, _, _ = select.select(list(sockets), [], [], 0.05)
                        if readable:
                            # If both queues are ready, service the ports in turn.
                            receiver = next((item for item in readable if sockets[item] != previous_port), readable[0])
                            payload, ancillary, flags, source = receiver.recvmsg(65535, ancillary_buffer)
                            port = sockets[receiver]
                            previous_port = port
                    wall, mono = time.time_ns(), time.monotonic_ns()
                except StopIteration:
                    break
                except socket.timeout:
                    payload, mono = None, time.monotonic_ns()
                accepted = payload is not None and (a.simulate or not a.lidar_source or source[0] == a.lidar_source)
                imu_datagram = accepted and (port != a.port or payload.startswith(telemetry.IMU_HEADER))
                if not start.is_set():
                    stats["startup_datagrams"] += int(payload is not None and not imu_datagram)
                    if accepted and not imu_datagram and not ready.is_set():
                        try:
                            compact = parse_compact(payload)
                        except ValueError:
                            stats["startup_compact_errors"] += 1
                            startup_good = 0
                        else:
                            received_ns, _ = udp_ancillary(ancillary, flags)
                            lag_ns = (received_ns or wall) - 1000 * compact["transmit_timestamp_us"]
                            if a.require_lidar_realtime and abs(lag_ns) >= 100_000_000:
                                if not stats["startup_epoch_mismatch_packets"]:
                                    write_jsonl(health, {"event": "lidar_startup_epoch_mismatch",
                                                         "receive_minus_native_tx_ns": lag_ns})
                                    sync_file(health)
                                stats["startup_epoch_mismatch_packets"] += 1
                                startup_good = 0
                            else:
                                startup_good += 1
                                if startup_good >= (6 if a.require_lidar_realtime else 1):
                                    ready.set()
                    continue
                if mono < cutoff.value - duration_ns:
                    continue
                if mono >= cutoff.value or stop.is_set():
                    break
                if mono - last_sync >= NS:
                    sync_file(raw)
                    sync_file(packets)
                    sync_file(imu_raw)
                    sync_file(imu_samples)
                    sync_file(health)
                    last_sync = mono
                if next_gap_ns is not None and mono >= next_gap_ns and not outage_reported:
                    stats["receive_gap_events"] += 1
                    write_jsonl(health, {"event": "lidar_receive_gap", "monotonic_ns": mono,
                                         "last_receive_monotonic_ns": last_receive})
                    outage_reported = True
                if mono - (last_valid_receive or (cutoff.value - duration_ns)) >= 5 * NS:
                    raise TimeoutError("no valid LiDAR scan packets for five seconds")
                if not accepted:
                    if payload is not None:
                        (stats if port == a.port else imu_stats)["filtered_datagrams"] += 1
                    continue

                kernel_ns, overflow = udp_ancillary(ancillary, flags)
                row = {
                    "payload_bytes": len(payload), "source_ip": source[0], "source_port": source[1],
                    "destination_port": port, "recv_realtime_ns": wall, "recv_monotonic_ns": mono,
                    "kernel_recv_realtime_ns": kernel_ns, "kernel_rxq_overflow": overflow,
                    "socket_message_flags": flags,
                }
                record = RAW_HEADER.pack(wall, len(payload)) + payload
                if imu_datagram:
                    row.update(packet_index=imu_stats["datagrams"], raw_offset_bytes=imu_offset)
                    try:
                        sample = telemetry.decode_imu(payload)
                    except ValueError as exc:
                        row["imu_error"] = str(exc)
                        imu_stats["invalid_datagrams"] += 1
                        if imu_progress is not None:
                            imu_progress.invalid_samples += 1
                    else:
                        stamp = sample["sensor_timestamp_us"]
                        previous = imu_stats.get("last_sensor_timestamp_us")
                        if previous is not None:
                            if stamp <= previous:
                                imu_stats["nonadvancing_sensor_timestamps"] += 1
                            else:
                                imu_stats["max_sensor_interval_us"] = max(imu_stats["max_sensor_interval_us"],
                                                                          stamp - previous)
                        imu_stats.setdefault("first_sensor_timestamp_us", stamp)
                        imu_stats["last_sensor_timestamp_us"] = stamp
                        imu_stats["valid_samples"] += 1
                        row.update(sample)
                        row["receive_minus_native_timestamp_ns"] = (kernel_ns or wall) - 1000 * stamp
                    if overflow is not None:
                        imu_stats.setdefault("kernel_rxq_overflow_by_port", {})[str(port)] = overflow
                    if kernel_ns is None and not a.simulate:
                        imu_stats["kernel_timestamp_missing"] += 1
                    imu_raw.write(record)
                    imu_digest.update(record)
                    write_jsonl(imu_samples, row)
                    imu_offset += len(record)
                    imu_stats["datagrams"] += 1
                    if imu_progress is not None and "sensor_timestamp_us" in row:
                        imu_progress.observe(mono)
                        if overflow is not None:
                            imu_progress.drop_indicators = overflow
                    continue

                if kernel_ns is not None:
                    if last_kernel_receive is not None:
                        kernel_gap = kernel_ns - last_kernel_receive
                        stats["max_kernel_receive_gap_ns"] = max(stats["max_kernel_receive_gap_ns"], kernel_gap)
                        if kernel_gap >= gap_ns:
                            stats["kernel_receive_gap_events"] += 1
                            write_jsonl(health, {"event": "lidar_kernel_receive_gap",
                                                 "monotonic_ns": mono, "gap_ns": kernel_gap})
                    last_kernel_receive = kernel_ns
                if overflow is not None:
                    stats["kernel_rxq_last_reported"] = overflow
                    if overflow != stats.get("previous_rxq_overflow", 0):
                        write_jsonl(health, {"event": "lidar_socket_drops", "monotonic_ns": mono,
                                             "kernel_rxq_overflow": overflow})
                    stats["previous_rxq_overflow"] = overflow
                if flags & socket.MSG_TRUNC:
                    stats["truncated_datagrams"] += 1
                if flags & socket.MSG_CTRUNC:
                    stats["ancillary_truncations"] += 1
                if kernel_ns is None and not a.simulate:
                    stats["kernel_timestamp_missing"] += 1
                if last_receive is not None:
                    stats["max_receive_gap_ns"] = max(stats["max_receive_gap_ns"], mono - last_receive)
                last_receive = mono
                next_gap_ns = mono + gap_ns
                outage_reported = False

                row.update(packet_index=stats["packets"], raw_offset_bytes=offset)
                try:
                    compact = parse_compact(payload)
                except ValueError as exc:
                    row["compact_error"] = str(exc)
                    stats["compact_errors"] += 1
                    if scan_progress is not None:
                        scan_progress.invalid_samples += 1
                else:
                    last_valid_receive = mono
                    row["compact"] = compact
                    stats["compact_valid_packets"] += 1
                    for module in compact["modules"]:
                        scan_observation.observe(source[0], module)
                    counter, tx = compact["telegram_counter"], compact["transmit_timestamp_us"]
                    received_ns = kernel_ns if kernel_ns is not None else wall
                    receive_minus_tx_ns = received_ns - 1000 * tx
                    row["receive_minus_native_tx_ns"] = receive_minus_tx_ns
                    epoch_hint = abs(receive_minus_tx_ns) < 100_000_000
                    bad_epoch_packets = 0 if epoch_hint else bad_epoch_packets + 1
                    if (last_clock_observation_ns is None or
                            mono - last_clock_observation_ns >= NS or epoch_hint != last_epoch_hint):
                        last_clock_observation_ns, last_epoch_hint = mono, epoch_hint
                        stats["last_receive_minus_native_tx_ns"] = receive_minus_tx_ns
                        write_jsonl(health, {
                            "event": "lidar_clock_observation", "monotonic_ns": mono,
                            "receive_minus_native_tx_ns": receive_minus_tx_ns,
                            "receive_clock_event": "kernel" if kernel_ns is not None else "userspace",
                            "near_realtime_epoch": epoch_hint, "sync_lock": "unverified",
                        })
                    key = (source[0], compact["modules"][0]["sender_id"])
                    previous_ctr, previous_tx = last_native.get(key, (counter - 1, tx))
                    delta = counter - previous_ctr
                    if delta != 1 or tx < previous_tx:
                        stats["telegram_gap_candidates"] += max(0, delta - 1)
                        stats["telegram_nonadvancing"] += int(delta <= 0)
                        stats["transmit_time_regressions"] += int(tx < previous_tx)
                        write_jsonl(health, {"event": "lidar_native_discontinuity", "monotonic_ns": mono,
                                             "packet_index": row["packet_index"], "telegram_step": delta,
                                             "transmit_timestamp_us_step": tx - previous_tx})
                    if delta > 0 or tx < previous_tx:
                        last_native[key] = (counter, tx)

                raw.write(record)
                digest.update(record)
                write_jsonl(packets, row)
                stats["packets"] += 1
                stats["payload_bytes"] += len(payload)
                if scan_progress is not None and "compact" in row:
                    scan_progress.observe(mono)
                    scan_progress.drop_indicators = max(stats["telegram_gap_candidates"],
                                                        stats["kernel_rxq_last_reported"] or 0)
                if a.require_lidar_realtime and bad_epoch_packets >= 25:
                    raise RuntimeError("LiDAR transmit clock departed from Pi realtime")
                offset += RAW_HEADER.size + len(payload)
        finally:
            stats.pop("previous_rxq_overflow", None)
            sync_file(raw)
            sync_file(packets)
            sync_file(imu_raw)
            sync_file(imu_samples)
            sync_directory(folder)
            sync_directory(imu_folder)
            stats["raw_sha256"] = digest.hexdigest()
            stats["scan_observation"] = scan_observation.summary()
            imu_stats["raw_sha256"] = imu_digest.hexdigest()


def package_version(name):
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def command_stdout(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=0.5)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() or None


class SimulatedRequest:
    # 16 x 16 valid JPEG of a uniform gray patch.
    jpeg = base64.b64decode(
        "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4n"
        "ICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAAQABABAREA/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/"
        "xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAA/AKoB/9k="
    )

    def __init__(self, sequence, mono, period, exposure):
        self.metadata = {"SensorTimestamp": mono - 1_000_000, "ExposureTime": exposure,
                         "FrameDuration": period, "SensorSequence": sequence}

    def get_metadata(self):
        return self.metadata

    def acquire(self):
        pass

    def release(self):
        pass

    def save(self, stream, output, format):
        output.write(self.jpeg)


def configure_camera(a, buffer_count):
    import libcamera
    from picamera2 import Picamera2

    model, sensor_size, depth, _ = PROFILES[a.profile]
    picam = Picamera2(a.camera)
    try:
        properties = picam.camera_properties
        observed = str(properties.get("Model", "")).lower()
        if model not in observed:
            raise RuntimeError(f"profile {a.profile} expects {model}, camera reports {observed!r}")

        modes = [m for m in picam.sensor_modes
                 if tuple(m.get("size", ())) == sensor_size and m.get("bit_depth") == depth
                 and m.get("fps", 0) >= a.fps]
        if not modes:
            raise RuntimeError(f"no compatible {sensor_size} {depth}-bit mode for {a.fps:g} fps")
        mode = modes[0]
        # Request both exact sensor geometry and the corresponding Bayer mode.
        # Explicit raw format/size also works on older Picamera2 builds.
        # Bullseye Picamera2's request.save accepts RGB image streams. Its
        # Pillow helper cannot turn a YUV420 request into a JPEG.
        image_format = "BGR888"
        config = picam.create_video_configuration(
            main={"format": image_format, "size": sensor_size},
            raw={"format": str(mode["format"]), "size": sensor_size},
            transform=libcamera.Transform(), buffer_count=buffer_count, queue=False,
        )
        explicit_sensor_config = "sensor" in config
        if explicit_sensor_config:
            config["sensor"] = {"output_size": sensor_size, "bit_depth": depth}
        picam.configure(config)
        applied = picam.camera_configuration()
        applied_sensor = applied.get("sensor") or {}
        raw_config = applied["raw"]
        if (tuple(applied["main"]["size"]) != sensor_size or applied["main"]["format"] != image_format
                or tuple(raw_config["size"]) != sensor_size
                or tuple(applied_sensor.get("output_size", sensor_size)) != sensor_size
                or applied_sensor.get("bit_depth", depth) != depth
                or not str(raw_config["format"]).split("_")[0].endswith(str(depth))):
            raise RuntimeError(f"unexpected applied camera mode: {applied!r}")

        supported = picam.camera_controls
        period = round(1e6 / a.fps)
        controls = {"FrameDurationLimits": (period, period)}
        if not a.auto_exposure:
            controls.update(AeEnable=False, ExposureTime=a.exposure_us, AnalogueGain=a.gain)
        if "HdrMode" in supported:
            controls["HdrMode"] = libcamera.controls.HdrModeEnum.Off
        if model == "imx708":
            if not {"AfMode", "LensPosition"} <= set(supported):
                raise RuntimeError("IMX708 autofocus controls are unavailable in this camera stack")
            low, high, _ = supported["LensPosition"]
            if not low <= a.lens_position <= high:
                raise RuntimeError(f"lens position outside supported range [{low}, {high}]")
            controls.update(AfMode=libcamera.controls.AfModeEnum.Manual, LensPosition=a.lens_position)
        picam.options["quality"] = a.jpeg_quality
        picam.set_controls(controls)
        applied = {
            "picamera2_version": package_version("picamera2"),
            "libcamera_version": getattr(libcamera, "__version__", None),
            "system_package_versions": command_stdout([
                "dpkg-query", "-W", "-f=${binary:Package}\t${Version}\n",
                "python3-picamera2", "python3-libcamera", "rpicam-apps", "libcamera-apps",
            ]),
            "camera_info": Picamera2.global_camera_info()[a.camera],
            "camera_properties": properties, "selected_sensor_mode": mode,
            "sensor_mode_selection": "sensor-and-raw" if explicit_sensor_config else "raw-format-and-size",
            "applied_configuration": applied, "requested_controls": controls,
            "focus_mode": "manual-lens-position" if model == "imx708" else "fixed-focus",
            "hdr": "requested-off" if "HdrMode" in controls else "control-unavailable",
        }
        return picam, json_values(applied)
    except BaseException:
        picam.close()
        raise


def persist_frame(jpeg, row, folder, stats, frames):
    name = f"frame_{row['frame_index']:08d}.jpg"
    path = folder / name
    temp = folder / f".{name}.partial"
    try:
        if not jpeg:
            raise OSError("camera returned an empty JPEG")
        with temp.open("wb") as image:
            image.write(jpeg)
            sync_file(image)
        row["image_bytes"] = len(jpeg)
        row["image_sha256"] = hashlib.sha256(jpeg).hexdigest()
        temp.replace(path)
        row["image"] = f"camera/{name}"
        write_jsonl(frames, row)
        stats["frames_saved"] += 1
        stats["saved_with_native_metadata"] += int(row["native_metadata_complete"])
        stats["image_bytes"] += row["image_bytes"]
    finally:
        temp.unlink(missing_ok=True)


def camera(a, run, ready, start, stop, cutoff, stats, health, _bound, progress):
    full_resolution = a.profile.endswith(("-flight", "-full"))
    pending = Queue(maxsize=2 if full_resolution else 3)
    encoded = Queue(maxsize=8 if full_resolution else 24)
    disk_done = Event()
    disk_errors = deque(maxlen=1)
    callback_errors = deque(maxlen=1)
    observed = Counter()
    previous_ts = previous_sequence = previous_observed_ns = None
    folder = run / "camera"
    period_us = round(1e6 / a.fps)
    duration_ns = round(a.seconds * NS)
    picam = None
    jpeg_encoder = None
    warmup_frames = 0
    frame_progress = progress.get("camera")
    frame_gap_limit_ns = round(max(1.0, 1.5 / a.fps) * NS)

    def encode(request, row):
        tick = time.monotonic_ns()
        try:
            if jpeg_encoder is None:
                buffer = io.BytesIO()
                request.save("main", buffer, format="jpeg")
                jpeg = buffer.getvalue()
            else:
                jpeg = jpeg_encoder.encode_func(request, "main")
        finally:
            request.release()
        row["jpeg_encode_ns"] = time.monotonic_ns() - tick
        observed["max_jpeg_encode_ns"] = max(observed["max_jpeg_encode_ns"], row["jpeg_encode_ns"])
        try:
            encoded.put_nowait((jpeg, row))
        except Full:
            observed["camera_disk_queue_drops"] += 1

    def write_images(frames):
        last_sync = time.monotonic_ns()
        try:
            while not disk_done.is_set() or not encoded.empty():
                try:
                    jpeg, row = encoded.get(timeout=0.05)
                except Empty:
                    continue
                tick = time.monotonic_ns()
                persist_frame(jpeg, row, folder, stats, frames)
                committed = time.monotonic_ns()
                stats["max_image_commit_ns"] = max(stats["max_image_commit_ns"], committed - tick)
                if frame_progress is not None:
                    frame_progress.observe(committed, frame_gap_limit_ns)
                    frame_progress.invalid_samples = stats["frames_saved"] - stats["saved_with_native_metadata"]
                    frame_progress.drop_indicators = observed["encoder_queue_drops"] + observed["camera_disk_queue_drops"]
                if tick - last_sync >= NS:
                    sync_directory(folder)
                    sync_file(frames)
                    last_sync = tick
            sync_directory(folder)
            sync_file(frames)
        except Exception as exc:
            disk_errors.append(exc)

    def on_request(request):
        nonlocal previous_ts, previous_sequence, previous_observed_ns, warmup_frames
        now = time.monotonic_ns()
        metadata = request.get_metadata()
        native_valid = all(isinstance(metadata.get(name), int) and metadata[name] > 0
                           for name in FRAME_METADATA)
        if not ready.is_set():
            warmup_frames = warmup_frames + 1 if native_valid else 0
            if warmup_frames >= 3:
                ready.set()
        if not start.is_set() or stop.is_set() or not cutoff.value - duration_ns <= now < cutoff.value:
            return

        # The callback runs in Picamera2's preview/event thread. Do not encode,
        # wait for storage, or hold more than the configured buffer queue.
        sequence = getattr(getattr(request, "request", None), "sequence", None)
        number = metadata.get("SensorSequence")
        number_source = "SensorSequence"
        if number is None:
            raw_stream = getattr(request, "stream_map", {}).get("raw")
            raw_buffer = getattr(getattr(request, "request", None), "buffers", {}).get(raw_stream)
            number = getattr(getattr(raw_buffer, "metadata", None), "sequence", None)
            number_source = "raw_buffer_sequence" if number is not None else None

        row = {
            "frame_index": observed["requests_observed"],
            "request_sequence": sequence,
            "sensor_sequence": number, "sensor_sequence_source": number_source,
            "observed_monotonic_ns": now, "observed_realtime_ns": time.time_ns(),
            "observed_boottime_ns": time.clock_gettime_ns(time.CLOCK_BOOTTIME),
            "metadata": json_values(metadata),
            **{key: metadata.get(name) for name, key in FRAME_METADATA.items()},
        }
        observed["requests_observed"] += 1
        row["native_metadata_complete"] = native_valid
        if not row["native_metadata_complete"]:
            observed["metadata_incomplete"] += 1
        native = row["SensorTimestamp_ns"]
        if native is not None:
            if previous_ts is not None:
                step = native - previous_ts
                row["sensor_timestamp_step_ns"] = step
                observed["max_sensor_gap_ns"] = max(observed["max_sensor_gap_ns"], step)
                observed["sensor_timestamp_regressions"] += int(step <= 0)
                frame_duration_ns = (row["FrameDuration_us"] or period_us) * 1000
                if step > 1.5 * frame_duration_ns:
                    observed["sensor_cadence_gap_events"] += 1
            previous_ts = native
        sequence_key = (number_source, number)
        if number is not None and previous_sequence and number_source == previous_sequence[0]:
            step = (number - previous_sequence[1]) % (1 << 32)
            row["sensor_sequence_step"] = step
            if 1 < step < (1 << 31):
                observed["sensor_sequence_missing"] += step - 1
            if step == 0 or step >= (1 << 31):
                observed["sensor_sequence_nonadvancing"] += 1
        previous_sequence = sequence_key
        previous_observed_ns = now
        request.acquire()
        try:
            pending.put_nowait((request, row))
        except Full:
            observed["encoder_queue_drops"] += 1
            request.release()

    def capture_callback(request):
        try:
            on_request(request)
        except Exception as exc:
            callback_errors.append(exc)

    if a.simulate:
        stats["configuration"] = {"simulation": True, "saved_image_size": [16, 16]}
    else:
        picam, stats["configuration"] = configure_camera(a, buffer_count=4 if full_resolution else 6)
        try:
            from picamera2.encoders import JpegEncoder
        except ImportError:
            stats["configuration"]["jpeg_encoder"] = "Picamera2 request.save"
        else:
            jpeg_encoder = JpegEncoder(num_threads=1, q=a.jpeg_quality)
            stats["configuration"]["jpeg_encoder"] = "Picamera2 JpegEncoder (simplejpeg)"
    write_json(folder / "configuration.json", stats["configuration"])
    reported_outage_start = None
    outage_limit_ns = int(max(0.5, 3 / a.fps) * NS)
    last_sync = time.monotonic_ns()
    due = last_sync
    sequence = 0
    started = False
    with (folder / "frames.jsonl").open("w") as frames:
        writer = Thread(target=write_images, args=(frames,), daemon=True)
        writer.start()
        try:
            if picam is not None:
                picam.post_callback = capture_callback
                picam.start(show_preview=False)
                started = True
            else:
                ready.set()
            while not stop.is_set() and time.monotonic_ns() < cutoff.value:
                if callback_errors:
                    raise RuntimeError("camera completion callback failed") from callback_errors[0]
                if disk_errors:
                    raise RuntimeError("camera image writer failed") from disk_errors[0]
                if not start.wait(0.025):
                    continue
                now = time.monotonic_ns()
                if a.simulate and now >= due:
                    on_request(SimulatedRequest(sequence, now, period_us, a.exposure_us))
                    sequence += 1
                    due = max(due + period_us * 1000, now)
                last = previous_observed_ns or (cutoff.value - duration_ns)
                if now - last >= outage_limit_ns and reported_outage_start != last:
                    stats["camera_stall_events"] += 1
                    reported_outage_start = last
                    write_jsonl(health, {"event": "camera_request_stall", "monotonic_ns": now,
                                         "last_observed_monotonic_ns": previous_observed_ns})

                try:
                    request, row = pending.get(timeout=0.01 if a.simulate else 0.05)
                except Empty:
                    pass
                else:
                    encode(request, row)
                if now - last_sync >= NS:
                    sync_file(health)
                    last_sync = now

            if started:
                picam.stop()
                started = False
            while not pending.empty():
                encode(*pending.get_nowait())
        finally:
            try:
                if started:
                    picam.stop()
            finally:
                while not pending.empty():
                    pending.get_nowait()[0].release()
                disk_done.set()
                writer.join()
                stats.update(observed)
                if picam is not None:
                    picam.close()
    if disk_errors:
        raise RuntimeError("camera image writer failed") from disk_errors[0]


def worker(target, args, run, ready, start, stop, cutoff, bound, progress):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    stats = Counter()
    error = None
    try:
        with (run / target.__name__ / "health.jsonl").open("w") as health:
            try:
                target(args, run, ready, start, stop, cutoff, stats, health, bound, progress)
            finally:
                sync_file(health)
    except Exception as cause:
        error = f"{type(cause).__name__}: {cause}"
        traceback.print_exc()
    stats["error"] = error
    write_json(run / target.__name__ / "summary.json", dict(stats))
    if error is not None:
        sys.exit(1)


def bracket(clock):
    before = time.clock_gettime_ns(clock)
    wall = time.clock_gettime_ns(time.CLOCK_REALTIME)
    after = time.clock_gettime_ns(clock)
    return {"before_ns": before, "realtime_ns": wall, "after_ns": after,
            "bracket_width_ns": after - before, "realtime_minus_midpoint_ns": wall - (before + after) // 2}


class ClockAnchors:
    def __init__(self):
        self.previous = None
        self.segment = 0
        self.index = 0

    def sample(self, filestream, health):
        clocks = {"CLOCK_MONOTONIC": bracket(time.CLOCK_MONOTONIC),
                  "CLOCK_BOOTTIME": bracket(time.CLOCK_BOOTTIME)}
        valid = all(value["bracket_width_ns"] <= 200_000 for value in clocks.values())
        changes = []
        if self.previous is not None:
            older = self.previous["clocks"]
            if not valid or not self.previous["valid_host_bracket"]:
                changes.append("host_clock_bracket_invalid")
            for name, values in clocks.items():
                offset_change = values["realtime_minus_midpoint_ns"] - older[name]["realtime_minus_midpoint_ns"]
                if abs(offset_change) > 2_000_000:
                    changes.append(f"{name}_realtime_offset_discontinuity")
            if clocks["CLOCK_MONOTONIC"]["before_ns"] - older["CLOCK_MONOTONIC"]["before_ns"] > 3 * NS:
                changes.append("anchor_gap")
        elif not valid:
            changes.append("host_clock_bracket_invalid")
        if changes:
            self.segment += 1
            write_jsonl(health, {"event": "clock_anchor_break", "anchor_index": self.index, "reasons": changes})
        row = {"anchor_index": self.index, "host_clock_segment": self.segment, "clocks": clocks,
               "valid_host_bracket": valid, "lidar_lock": "unverified", "association_valid": False}
        write_jsonl(filestream, row)
        self.previous = row
        self.index += 1


def power_telemetry(simulate):
    if simulate:
        return {"power_status": "simulated"}
    try:
        result = subprocess.run(["vcgencmd", "get_throttled"], capture_output=True, text=True, timeout=0.5)
        flags = int(result.stdout.strip().removeprefix("throttled="), 0) if result.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        flags = None
    try:
        temperature = int(Path("/sys/class/thermal/thermal_zone0/temp").read_text()) / 1000
    except (OSError, ValueError):
        temperature = None
    return {"pi_throttled_bitmask": flags, "pi_temperature_c": temperature,
            "undervoltage_active": bool(flags & 1) if flags is not None else None,
            "undervoltage_since_boot": bool(flags & 0x10000) if flags is not None else None}


def archive_input(source, run, kind):
    destination = run / (kind + source.suffix)
    temporary = run / f".{destination.name}.partial"
    try:
        shutil.copyfile(source, temporary)
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
            checksum = file_sha256(stream)
        temporary.replace(destination)
        sync_directory(run)
        return {"path": destination.name, "sha256": checksum}
    finally:
        temporary.unlink(missing_ok=True)


def lidar_snapshot(a, run, phase, sensor_control):
    variables = ("DeviceIdent", "SerialNumber", "FirmwareVersion", "OrdNum", "SCdevicestate",
                 "ScanDataEnable", "ScanDataEthSettings", "ScanDataFormat", "LMPscancfg",
                 "TSCRole", "TSCTCSrvAddr", *telemetry.FILTER_FIELDS,
                 "PerformanceProfileNumber", "ImuDataEnable", "ImuDataEthSettings")
    replies, rest, errors = {}, {}, {}
    snapshot = {"phase": phase, "lidar_address": a.lidar_source,
                "realtime_ns": time.time_ns(), "simulated": a.simulate or a.simulate_lidar}
    if snapshot["simulated"]:
        replies["LMPscancfg"] = "sRA LMPscancfg 1388 1 9C4 FFEAF160 150EA0"
        rest = {
            **telemetry.DEFAULT_PROFILE["filters"],
            "LFPmovingAveragingFilter": {"bEnable": False, "uiAveragingDepth": 3},
            "ImuDataEnable": True,
            "ImuDataEthSettings": {"Protocol": 1, "IPAddress": [127, 0, 0, 1],
                                   "Port": a.imu_port or telemetry.DEFAULT_IMU_PORT},
        }
    elif a.lidar_source:
        if sensor_control is not None:
            replies = sensor_control.snapshot(run / "lidar" / f"config_{phase}.txt", variables)
        else:
            from lidar_record import cola

            for name in variables:
                try:
                    replies[name] = cola(a.lidar_source, f"sRN {name}", timeout=0.35).strip()
                except OSError as exc:
                    replies[name] = str(exc)
                    break
        rest, errors = telemetry.rest_settings(a.lidar_source, a.listen)
    snapshot["values"] = {
        name: {"status": "read" if telemetry.cola_values(reply, name) else "unknown", "reply": reply}
        for name, reply in replies.items()
    }
    snapshot["rest_values"] = rest
    snapshot["rest_errors"] = errors
    observed = telemetry.decode_snapshot(replies, rest)
    snapshot["observed"] = observed
    name = f"config_{phase}.json"
    write_json(run / "lidar" / name, snapshot)
    return f"lidar/{name}", observed


def record_lidar_snapshot(a, run, manifest, phase, sensor_control):
    try:
        path, observed = lidar_snapshot(a, run, phase, sensor_control)
    except OSError as exc:
        manifest.setdefault("lidar_configuration_errors", {})[phase] = str(exc)
        return {}
    manifest.setdefault("lidar_configuration", {})[phase] = path
    manifest["lidar_profile"]["observed"][phase] = observed
    return observed


def host_info():
    def read_file(path):
        try:
            return Path(path).read_text().rstrip("\x00\r\n")
        except OSError:
            return None

    return {"platform": platform.platform(), "python": platform.python_version(), "hostname": socket.gethostname(),
            "os_release": read_file("/etc/os-release"),
            "pi_model": read_file("/proc/device-tree/model"),
            "boot_id": read_file("/proc/sys/kernel/random/boot_id")}


def supervise(a, run, manifest, sensor_control=None, on_recording=None, heartbeat=None):
    context = multiprocessing.get_context("spawn")
    start, stop = context.Event(), context.Event()
    lidar_bound = context.Event()
    cutoff = context.RawValue("Q", sys.maxsize)
    progress = {name: context.RawValue(StreamProgress) for name in ("camera", "lidar", "imu")} if heartbeat else {}
    workers = {}
    interrupted = []
    markers = deque(maxlen=64)
    previous_handlers = {}
    stream_touched = False

    def signal_handler(number, frame):
        if number == signal.SIGUSR1:
            markers.append((time.monotonic_ns(), time.time_ns()))
        elif not interrupted:
            interrupted.append(number)

    for number in (signal.SIGINT, signal.SIGTERM, signal.SIGUSR1):
        previous_handlers[number] = signal.signal(number, signal_handler)

    try:
        with (run / "health.jsonl").open("w") as health, (run / "clock" / "anchors.jsonl").open("w") as anchors:
            clocks = ClockAnchors()
            try:
                manifest["inputs"] = {
                    kind: archive_input(source, run, kind)
                    for kind, source in (("calibration", a.calibration_file), ("context", a.context_file),
                                         ("camera_timing_evidence", a.camera_timing_evidence))
                    if source is not None
                }
                before = record_lidar_snapshot(a, run, manifest, "before", sensor_control)
                endpoint = telemetry.imu_udp_destination(before.get("imu_data_eth_settings"))
                configured_port = endpoint[1] if endpoint and a.listen in ("0.0.0.0", endpoint[0]) else None
                a.imu_receive_port = a.imu_port or configured_port or telemetry.DEFAULT_IMU_PORT
                manifest["imu"].update(
                    listen=a.listen, receive_port=a.imu_receive_port,
                    receive_port_source="override" if a.imu_port else "scanner" if configured_port else "SICK default",
                )
                write_json(run / "manifest.json", manifest)
                for capture in (lidar, camera):
                    ready = context.Event()
                    process = context.Process(name=capture.__name__, target=worker,
                                              args=(capture, a, run, ready, start, stop, cutoff, lidar_bound, progress))
                    process.start()
                    workers[capture.__name__] = (process, ready)
                if a.simulate_lidar:
                    ready = context.Event()
                    fixture = context.Process(name="localhost_lidar_fixture", target=publish_loopback,
                                              args=(stop, a.port, a.imu_receive_port, lidar_bound, ready))
                    fixture.start()
                    workers[fixture.name] = (fixture, ready)

                startup_deadline = time.monotonic() + a.startup_timeout
                while True:
                    if interrupted:
                        return "interrupted"
                    if any(process.exitcode is not None for process, _ in workers.values()):
                        return "startup_worker_failed"
                    if sensor_control and not stream_touched and lidar_bound.is_set() and workers["camera"][1].is_set():
                        stream_touched = True
                        sensor_control.start()
                    if all(ready.is_set() for _, ready in workers.values()):
                        break
                    if time.monotonic() >= startup_deadline:
                        return "startup_timeout"
                    time.sleep(0.025)

                clocks.sample(anchors, health)
                sync_file(anchors)
                now = time.monotonic_ns()
                manifest["start_monotonic_ns"] = now
                cutoff.value = now + round(a.seconds * NS)
                manifest["planned_stop_monotonic_ns"] = cutoff.value
                start.set()
                if heartbeat:
                    expected = {"lidar": NS, "camera": round(max(1.0, 1.5 / a.fps) * NS)}
                    if a.simulate or a.simulate_lidar or a.imu_port is not None or before.get("imu_data_enable") is True:
                        expected["imu"] = NS
                    heartbeat.publish("recording", expected_streams=expected,
                                      planned_stop_monotonic_ns=cutoff.value)
                if on_recording:
                    on_recording()
                print("recording (camera and Compact LiDAR ready)", flush=True)
                next_anchor = now + NS
                next_power = now
                while not interrupted and time.monotonic_ns() < cutoff.value:
                    if any(process.exitcode not in (None, 0) for process, _ in workers.values()):
                        return "capture_worker_failed"
                    now = time.monotonic_ns()
                    while markers:
                        monotonic_ns, realtime_ns = markers.popleft()
                        write_jsonl(health, {"event": "operator_marker", "monotonic_ns": monotonic_ns,
                                             "realtime_ns": realtime_ns, "source": "SIGUSR1"})
                    if now >= next_anchor:
                        clocks.sample(anchors, health)
                        sync_file(anchors)
                        sync_file(health)
                        next_anchor += (1 + (now - next_anchor) // NS) * NS
                    if now >= next_power:
                        free_bytes = shutil.disk_usage(run).free
                        power = power_telemetry(a.simulate)
                        write_jsonl(health, {"event": "host_health", "monotonic_ns": now,
                                             "free_bytes": free_bytes, **power})
                        if heartbeat:
                            heartbeat.publish("recording", streams={name: p.snapshot() for name, p in progress.items()},
                                              host={"free_bytes": free_bytes, "storage_reserve_bytes": a.min_free_mib * 1024 ** 2,
                                                    "clock_segment": clocks.segment, **power})
                        if free_bytes < a.min_free_mib * 1024 ** 2:
                            return "storage_reserve_reached"
                        next_power = now + NS
                    time.sleep(0.01)
                return "interrupted" if interrupted else "elapsed"
            except Exception as cause:
                manifest["supervisor_error"] = f"{type(cause).__name__}: {cause}"
                return "supervisor_error"
            finally:
                if interrupted:
                    manifest["signal"] = signal.Signals(interrupted[0]).name
                manifest["stop_requested_monotonic_ns"] = time.monotonic_ns()
                if heartbeat:
                    heartbeat.publish("finalizing", streams={name: p.snapshot() for name, p in progress.items()})
                stop.set()
                if stream_touched:
                    try:
                        manifest["sensor_cleanup_errors"] = sensor_control.idle()
                    except Exception as cause:
                        manifest["sensor_cleanup_errors"] = [f"{type(cause).__name__}: {cause}"]
                # All workers share one grace deadline. Even a hung native
                # camera must not indefinitely block UDP cleanup or manifest.
                deadline = time.monotonic() + a.shutdown_timeout
                for process, _ in workers.values():
                    process.join(max(0, deadline - time.monotonic()))
                for name, (process, ready) in workers.items():
                    if process.is_alive():
                        process.kill()
                        write_jsonl(health, {"event": "worker_shutdown_timeout", "worker": name})
                        process.join(1)
                    manifest.setdefault("workers", {})[name] = {"exitcode": process.exitcode, "ready": ready.is_set()}
                if heartbeat:
                    heartbeat.publish("finalizing", streams={name: p.snapshot() for name, p in progress.items()})
                clocks.sample(anchors, health)
                write_jsonl(health, {"event": "host_health_end", "monotonic_ns": time.monotonic_ns(),
                                     **power_telemetry(a.simulate)})
                sync_file(anchors)
                sync_file(health)
                record_lidar_snapshot(a, run, manifest, "after", sensor_control)
                if a.pose_file is not None:
                    try:
                        manifest.setdefault("inputs", {})["pose"] = archive_input(a.pose_file, run, "pose")
                    except OSError as cause:
                        manifest["pose_attachment_error"] = f"{type(cause).__name__}: {cause}"
    finally:
        for number, handler in previous_handlers.items():
            signal.signal(number, handler)


def parse_arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True, type=Path, help="directory in which to create a new run")
    parser.add_argument("--seconds", type=float, default=30)
    parser.add_argument("--label", default="capture")
    parser.add_argument("--profile", choices=("auto", *PROFILES), default="auto")
    parser.add_argument("--fps", type=float, help="camera cadence override, 10–15 for bench or 3 for flight")
    parser.add_argument("--exposure-us", default=1000, type=int)
    parser.add_argument("--auto-exposure", action="store_true")
    parser.add_argument("--gain", default=1.0, type=float)
    parser.add_argument("--lens-position", type=float, help="manual focus in diopters, IMX708 default 0.33 bench / 0.17 flight")
    parser.add_argument("--jpeg-quality", default=88, type=int)
    parser.add_argument("--camera", default=0, type=int)
    parser.add_argument("--note", default="")
    parser.add_argument("--listen", default="0.0.0.0")
    parser.add_argument("--port", default=2115, type=int)
    parser.add_argument("--lidar-source", help="accept only this LiDAR IPv4 address")
    parser.add_argument("--snapshot-lidar", action="store_true",
                        help="legacy flag, settings are read automatically with --lidar-source")
    telemetry.add_arguments(parser)
    parser.add_argument("--lidar-gap-ms", default=100, type=float)
    parser.add_argument("--startup-timeout", default=15, type=float)
    parser.add_argument("--shutdown-timeout", default=6, type=float)
    parser.add_argument("--min-free-mib", default=256, type=int)
    parser.add_argument("--calibration-id")
    parser.add_argument("--calibration-file", type=Path, help="copy an existing calibration record into the run")
    parser.add_argument("--context-file", type=Path, help="copy the run setup and sensor settings into the run")
    parser.add_argument("--pose-file", type=Path, help="copy an external native-time pose log at run shutdown")
    parser.add_argument("--camera-clock", choices=("CLOCK_MONOTONIC", "CLOCK_BOOTTIME"))
    parser.add_argument("--camera-timestamp-event", choices=("frame-start-readout", "first-row-exposure-start"))
    parser.add_argument("--camera-timing-evidence", type=Path,
                        help="copy separately verified evidence for the installed camera clock/event")
    parser.add_argument("--simulate", action="store_true", help="use synthetic Compact datagrams and JPEGs on Linux")
    parser.add_argument("--simulate-lidar", action="store_true",
                        help="use the real camera and synthetic Compact packets on localhost")
    parser.add_argument("--require-lidar-realtime", action="store_true",
                        help="gate capture on a plausible scanner/receive clock epoch")
    a = parser.parse_args(argv)
    try:
        a.lidar_profile = telemetry.load_profile(a.lidar_profile_file)
    except (OSError, ValueError) as exc:
        parser.error(f"--lidar-profile-file: {exc}")
    if a.simulate and a.simulate_lidar:
        parser.error("choose only one simulation mode")
    if a.simulate_lidar:
        a.listen = a.lidar_source = "127.0.0.1"
    if a.profile == "auto":
        if a.simulate:
            a.profile = "imx708-bench"
        else:
            from picamera2 import Picamera2
            cameras = Picamera2.global_camera_info()
            if not 0 <= a.camera < len(cameras):
                parser.error(f"camera {a.camera} is unavailable")
            model = str(cameras[a.camera].get("Model", "")).lower()
            if model not in ("imx219", "imx708"):
                parser.error(f"no auto profile for camera model {model!r}")
            a.profile = ("imx219-full" if model == "imx219" and a.fps is not None and a.fps <= 5
                         else model + "-bench")
    _, _, _, default_fps = PROFILES[a.profile]
    a.fps = default_fps if a.fps is None else a.fps
    for name in ("seconds", "startup_timeout", "shutdown_timeout", "lidar_gap_ms", "gain", "fps"):
        value = getattr(a, name)
        if not math.isfinite(value) or value <= 0:
            parser.error(f"--{name.replace('_', '-')} must be positive and finite")
    if a.seconds > 1200:
        parser.error("--seconds must be at most 1200")
    flight = a.profile.endswith("flight")
    if ((flight and a.fps != 3.0) or
            (a.profile == "imx219-full" and not 1 <= a.fps <= 5) or
            (a.profile.endswith("-bench") and not 5 <= a.fps <= 15)):
        parser.error("cadence must be 5–15 fps for binned, 1–5 for IMX219 full, or 3 for IMX708 flight")
    if not 0 < a.exposure_us < round(1e6 / a.fps):
        parser.error("--exposure-us must be positive and shorter than the frame period")
    if not 1 <= a.jpeg_quality <= 100 or not 1 <= a.port <= 65535 or a.camera < 0 or a.min_free_mib < 0:
        parser.error("invalid JPEG quality, UDP port, camera index, or storage reserve")
    for name in ("listen", "lidar_source"):
        address = getattr(a, name)
        if address is not None:
            try:
                socket.inet_pton(socket.AF_INET, address)
            except OSError:
                parser.error(f"--{name.replace('_', '-')} must be an IPv4 address")
    if a.lens_position is None and a.profile.startswith("imx708"):
        a.lens_position = 0.17 if flight else 0.33
    if a.lens_position is not None and (
        not a.profile.startswith("imx708") or not math.isfinite(a.lens_position) or a.lens_position < 0
    ):
        parser.error("--lens-position requires the IMX708 profile and a nonnegative finite value")
    timing = (a.camera_clock, a.camera_timestamp_event, a.camera_timing_evidence)
    if any(timing) and (not all(timing) or a.simulate):
        parser.error("camera clock, timestamp event, and evidence file must be supplied together for a hardware run")
    if a.snapshot_lidar and (not a.lidar_source or a.simulate or a.simulate_lidar):
        parser.error("--snapshot-lidar requires --lidar-source and a hardware run")
    for field in ("calibration_file", "context_file", "camera_timing_evidence"):
        path = getattr(a, field)
        if path is not None and not path.is_file():
            parser.error(f"--{field.replace('_', '-')} must name an existing file")
    return a


def main(argv=None, *, sensor_control=None, run_path=None, on_recording=None, release_id=None, heartbeat=None):
    a = parse_arguments(argv)
    if sys.platform != "linux" or not hasattr(time, "CLOCK_BOOTTIME"):
        print("collect_v2 requires Linux CLOCK_BOOTTIME and Linux UDP ancillary data", file=sys.stderr)
        return 2

    a.out.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(a.out).free < a.min_free_mib * 1024 ** 2:
        print(f"storage reserve unavailable in {a.out}", file=sys.stderr)
        return 2
    label = re.sub(r"[^a-zA-Z0-9_-]+", "-", a.label).strip("-_")[:48] or "capture"
    now = datetime.now(timezone.utc)
    run = Path(run_path) if run_path else a.out.resolve() / f"{now:%Y%m%dT%H%M%S%fZ}_{label}"
    run.mkdir()
    for directory in ("lidar", "imu", "camera", "clock"):
        (run / directory).mkdir()
    sync_directory(run.parent)
    manifest = {
        "schema": "pavewatch-collection-v2", "run_id": run.name, "created_utc": now.isoformat(),
        "status": "in_progress", "simulated": a.simulate or a.simulate_lidar, "host": host_info(),
        "recorder_release": release_id,
        "simulation": {"camera": a.simulate, "lidar": a.simulate or a.simulate_lidar},
        "storage_mount": command_stdout(["findmnt", "-n", "-o", "SOURCE,FSTYPE,TARGET", "-T", str(run)]),
        "label": a.label, "note": a.note, "capture_profile": a.profile, "seconds_requested": a.seconds,
        "camera_fps_requested": a.fps, "jpeg_quality_requested": a.jpeg_quality,
        "camera_model_requested": PROFILES[a.profile][0],
        "camera_sensor_size_requested": PROFILES[a.profile][1],
        "camera_bit_depth_requested": PROFILES[a.profile][2], "camera_index": a.camera,
        "camera_exposure_us_requested": None if a.auto_exposure else a.exposure_us,
        "camera_analogue_gain_requested": None if a.auto_exposure else a.gain,
        "camera_lens_position_diopters_requested": a.lens_position,
        "lidar_listen": a.listen, "lidar_port": a.port, "lidar_source": a.lidar_source,
        "lidar_profile": {
            "requested": a.lidar_profile, "observed": {},
            "evidence": "synthetic" if a.simulate or a.simulate_lidar else "scanner",
            "verification": {"status": "pending"},
        },
        "imu": {"status": "pending", "receive_port_requested": a.imu_port},
        "lidar_gap_threshold_ms": a.lidar_gap_ms, "min_free_mib": a.min_free_mib,
        "require_lidar_realtime_epoch": a.require_lidar_realtime,
        "calibration_id": a.calibration_id,
        "timing": {
            "camera_metadata": "Picamera2 same-request libcamera controls",
            "camera_timestamp_clock": "CLOCK_MONOTONIC" if a.simulate else a.camera_clock or "unverified",
            "camera_timestamp_event": "synthetic" if a.simulate else a.camera_timestamp_event or "unverified",
            "camera_timing_evidence_status": "operator-supplied" if a.camera_timing_evidence else "unverified",
            "pi4_vc4_unicam_source_candidate": {
                "clock": "CLOCK_MONOTONIC", "event": "first-data-byte/frame-start readout",
                "driver": "https://github.com/raspberrypi/linux/blob/rpi-6.12.y/drivers/media/platform/broadcom/bcm2835-unicam.c#L3475-L3496",
                "pipeline": "https://github.com/raspberrypi/libcamera/blob/main/src/libcamera/pipeline/rpi/vc4/vc4.cpp#L3475-L3492",
            },
            "generic_libcamera_documentation": {"clock": "CLOCK_BOOTTIME", "event": "first-row exposure"},
            "lidar_timestamp": "sensor-native Compact Type 1 microseconds; epoch and lock unverified",
            "lidar_raw_receive_clock": "userspace CLOCK_REALTIME",
            "imu_timestamp": "sensor-native Compact Type 2 microseconds; epoch and lock unverified",
            "common_clock_association": "unverified",
            "pose_time_mapping": "not supplied by the recorder",
        },
    }
    write_json(run / "manifest.json", manifest)
    print(f"run {run} (PID {os.getpid()})", flush=True)
    reason = supervise(a, run, manifest, sensor_control, on_recording, heartbeat)
    for name in ("lidar", "camera"):
        path = run / name / "summary.json"
        if path.is_file():
            manifest.setdefault("workers", {}).setdefault(name, {}).update(json.loads(path.read_text()))
    lidar_data = manifest.get("workers", {}).get("lidar", {})
    camera_data = manifest.get("workers", {}).get("camera", {})
    profile = manifest["lidar_profile"]
    observed = profile["observed"]
    before, after = observed.get("before", {}), observed.get("after", {})
    observed["stream"] = lidar_data.get("scan_observation", {})
    profile["verification"] = telemetry.verify_profile(a.lidar_profile, before, after, observed["stream"])
    imu = manifest["imu"]
    imu_stats = lidar_data.get("imu", {})
    imu_before, imu_after = before.get("imu_data_enable"), after.get("imu_data_enable")
    imu.update(imu_stats)
    imu.update(
        configured_enable_before=imu_before, configured_enable_after=imu_after,
        configured_destination_before=before.get("imu_data_eth_settings"),
        configured_destination_after=after.get("imu_data_eth_settings"),
        raw="imu/raw.bin" if "raw_sha256" in imu_stats else None,
        samples="imu/samples.jsonl" if "raw_sha256" in imu_stats else None,
        datagrams=imu_stats.get("datagrams", 0), valid_samples=imu_stats.get("valid_samples", 0),
    )
    imu["status"] = (
        "recorded" if imu["valid_samples"] else "invalid_datagrams" if imu["datagrams"]
        else "receiver_error" if imu.get("bind_error") else "disabled" if imu_before is False and imu_after is False
        else "no_datagrams"
    )
    if imu["valid_samples"] > 1 and not imu.get("nonadvancing_sensor_timestamps"):
        elapsed_us = imu["last_sensor_timestamp_us"] - imu["first_sensor_timestamp_us"]
        imu["received_sample_rate_hz"] = round(1e6 * (imu["valid_samples"] - 1) / elapsed_us, 4)
    if reason == "elapsed":
        if any(data.get("exitcode") != 0 for data in (lidar_data, camera_data)):
            reason = "capture_worker_failed"
        elif not lidar_data.get("compact_valid_packets") or not camera_data.get("frames_saved"):
            reason = "required_stream_missing"
        elif not camera_data.get("saved_with_native_metadata"):
            reason = "camera_native_metadata_unavailable"
    if manifest.get("sensor_cleanup_errors") and reason == "elapsed":
        reason = "sensor_idle_unverified"
    if reason == "startup_timeout" and lidar_data.get("startup_epoch_mismatch_packets"):
        reason = "lidar_clock_epoch_unverified"
    warning_names = (
        (camera_data.get("encoder_queue_drops"), "camera_encoder_queue_drops"),
        (camera_data.get("camera_disk_queue_drops"), "camera_disk_queue_drops"),
        (camera_data.get("sensor_cadence_gap_events"), "camera_native_cadence_gaps"),
        (camera_data.get("metadata_incomplete"), "camera_incomplete_metadata"),
        (lidar_data.get("receive_gap_events"), "lidar_userspace_receive_stalls"),
        (lidar_data.get("kernel_receive_gap_events"), "lidar_kernel_receive_gaps"),
        (lidar_data.get("telegram_gap_candidates"), "possible_lidar_telegram_loss"),
        (lidar_data.get("startup_epoch_mismatch_packets"), "lidar_clock_epoch_mismatch_at_start"),
        (imu.get("invalid_datagrams"), "lidar_imu_invalid_datagrams"),
        (imu.get("nonadvancing_sensor_timestamps"), "lidar_imu_nonadvancing_sensor_time"),
        (imu.get("bind_error"), "lidar_imu_receive_port_unavailable"),
        (any(imu.get("kernel_rxq_overflow_by_port", {}).values()), "possible_lidar_imu_socket_loss"),
        ((imu_before is True or imu_after is True or a.imu_port is not None) and not imu["valid_samples"],
         "lidar_imu_no_valid_samples"),
    )
    manifest["quality_flags"] = [name for count, name in warning_names if count]
    verification_status = profile["verification"]["status"]
    if verification_status != "verified":
        manifest["quality_flags"].append("lidar_profile_" + verification_status)
    if reason == "elapsed" and camera_data.get("frames_saved", 0) < 0.9 * a.fps * a.seconds:
        manifest["quality_flags"].append("camera_frame_shortfall")
    try:
        with (run / "health.jsonl").open() as stream:
            if any(json.loads(line).get("undervoltage_active") is True for line in stream):
                manifest["quality_flags"].append("pi_undervoltage_observed")
    except (OSError, ValueError):
        manifest["quality_flags"].append("host_health_incomplete")
    manifest["stop_reason"] = reason
    manifest["status"] = "complete" if reason == "elapsed" else "incomplete"
    write_json(run / "manifest.json", manifest)
    print(f"{manifest['status']} ({reason})", flush=True)
    if reason == "interrupted":
        return 128 + signal.Signals[manifest["signal"]].value
    return 0 if reason == "elapsed" else 1


if __name__ == "__main__":
    sys.exit(main())
