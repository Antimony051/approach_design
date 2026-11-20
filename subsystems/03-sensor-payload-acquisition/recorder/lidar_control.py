#!/usr/bin/env python3
"""Manual start/stop control and supervised picoScan recording (Python 3.9+)."""

import argparse
import csv
from datetime import datetime
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
import uuid
import zlib

import recorder_watchdog as watchdog


HOME = Path("/home/pavewatch")
DATA = HOME / "data"
RUN = Path("/run/pavewatch-lidar")
STATE = Path("/var/lib/pavewatch-lidar/state.json")
UNIT = "pavewatch-recorder.service"
IP = "192.168.0.1"
PI_ETH_IP = "192.168.0.100"
SENSOR_INTERFACE = "eth0"
PORT = 2115
CAPTURE_OWNER = STATE.parent / "capture_sensor_owner.json"
CONTROL_LOCK = Path("/run/lock/pavewatch-recorder.lock")
RESERVE = 1024 ** 3
MAX_RECORDING_SECONDS = 20 * 60
VARS = ("DeviceIdent", "SerialNumber", "FirmwareVersion", "OrdNum",
        "SCdevicestate", "ScanDataEnable", "ScanDataEthSettings", "ScanDataFormat",
        "LMPscancfg", "EIIpAddr", "TSCRole", "TSCTCSrvAddr", "LFPmovingAveragingFilter",
        "ImuDataEnable", "EncoderDataEnable")


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def log(message):
    print(message, flush=True)
    with (HOME / "WORKLOG.md").open("a") as f:
        f.write("- %s (lidar control) %s\n" % (now(), message.replace("\n", " ")))


def atomic_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + ".tmp")
    with temp.open("w") as f:
        json.dump(value, f, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return {}


def recording_limit(seconds):
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("--seconds must be zero (20-minute maximum) or a positive finite number")
    return min(seconds or MAX_RECORDING_SECONDS, MAX_RECORDING_SECONDS)


def assert_sensor_link():
    carrier = Path("/sys/class/net") / SENSOR_INTERFACE / "carrier"
    try:
        connected = carrier.read_text().strip() == "1"
    except OSError:
        connected = False
    if not connected:
        raise ConnectionError(f"LiDAR Ethernet {SENSOR_INTERFACE} has no carrier")
    result = subprocess.run(["ip", "-j", "-4", "route", "get", IP],
                            capture_output=True, text=True, timeout=2, check=True)
    route = json.loads(result.stdout)[0]
    if route.get("dev") != SENSOR_INTERFACE or route.get("prefsrc") != PI_ETH_IP or route.get("gateway"):
        raise ConnectionError(f"LiDAR route must be directly on {SENSOR_INTERFACE} from {PI_ETH_IP}")


class Cola:
    """One CoLa-A connection; read through ETX, even when TCP splits a reply."""

    def __init__(self, ip=IP, timeout=2.0):
        assert_sensor_link()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE,
                                   SENSOR_INTERFACE.encode() + b"\0")
            self.socket.bind((PI_ETH_IP, 0))
            self.socket.settimeout(timeout)
            self.socket.connect((ip, 2111))
        except BaseException:
            self.socket.close()
            raise
        self.timeout = timeout
        self.pending = b""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.socket.close()

    def request(self, command):
        self.socket.sendall(b"\x02" + command.encode("ascii") + b"\x03")
        deadline = time.monotonic() + self.timeout
        while b"\x03" not in self.pending:
            left = deadline - time.monotonic()
            if left <= 0:
                raise TimeoutError("sensor reply timed out")
            self.socket.settimeout(left)
            chunk = self.socket.recv(4096)
            if not chunk:
                raise ConnectionError("sensor closed the connection before its reply ended")
            self.pending += chunk
            if len(self.pending) > 65536:
                raise ValueError("sensor reply exceeded 64 KiB")
        reply, self.pending = self.pending.split(b"\x03", 1)
        if not reply.startswith(b"\x02"):
            raise ValueError("invalid sensor reply framing")
        return reply[1:].decode("ascii")

    def expect(self, command, expected):
        if self.request(command) != expected:
            # Never include the login command, hash, password or reply in errors.
            raise RuntimeError("sensor did not acknowledge " + command.split()[1])

    def login(self):
        text = (HOME / "LIDAR_CREDENTIALS.txt").read_text()
        match = re.search(r"^password:\s*(.+?)\s*$", text, re.M)
        if not match:
            raise ValueError("sensor credential file has no password field")
        words = struct.unpack("<4I", hashlib.md5(match[1].encode()).digest())
        value = "%08X" % (words[0] ^ words[1] ^ words[2] ^ words[3])
        self.expect("sMN SetAccessMode 4 " + value, "sAN SetAccessMode 1")


def sensor_state():
    with Cola() as c:
        result = {}
        for name in ("SCdevicestate", "ScanDataEnable"):
            parts = c.request("sRN " + name).split()
            if len(parts) != 3 or parts[:2] != ["sRA", name]:
                raise RuntimeError("could not read sensor " + name)
            result[name] = int(parts[2], 16)
        return result


def sensor_start():
    with Cola() as c:
        c.login()
        c.expect("sMN LMCstartmeas", "sAN LMCstartmeas 0")
        c.expect("sWN ScanDataEnable 1", "sWA ScanDataEnable")
        c.expect("sMN Run", "sAN Run 1")


def sensor_idle():
    errors = []
    # Attempt measurement stop even if disabling output fails.
    try:
        with Cola() as c:
            c.login()
            c.expect("sWN ScanDataEnable 0", "sWA ScanDataEnable")
            c.expect("sMN Run", "sAN Run 1")
    except Exception as e:
        errors.append("disable output: " + str(e))
    try:
        with Cola() as c:
            c.login()
            c.expect("sMN LMCstopmeas", "sAN LMCstopmeas 0")
    except Exception as e:
        errors.append("stop measurement: " + str(e))
    try:
        state = sensor_state()
        if state != {"SCdevicestate": 0, "ScanDataEnable": 0}:
            errors.append("sensor did not reach measurement stopped / output off")
    except Exception as e:
        errors.append("verify idle: " + str(e))
    return errors


def recover_capture_sensor():
    if not CAPTURE_OWNER.is_file():
        return []
    errors = sensor_idle()
    if not errors:
        CAPTURE_OWNER.unlink(missing_ok=True)
    return errors


def snapshot(path, variables=VARS):
    # A missing snapshot must not prevent finalization or sensor shutdown.
    lines = ["# " + now()]
    replies = {}
    try:
        with Cola(timeout=1.0) as c:
            for name in variables:
                replies[name] = c.request("sRN " + name)
                lines.append(name + " -> " + replies[name])
    except Exception as e:
        lines.append("# snapshot incomplete: " + str(e))
    Path(path).write_text("\n".join(lines) + "\n")
    return replies


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def finalize(session, summary):
    atomic_json(session / "summary.json", summary)
    lines = [sha256(p) + "  " + p.name + "\n" for p in sorted(session.iterdir())
             if p.is_file() and p.name not in ("SHA256SUMS", "SHA256SUMS.tmp")]
    temp = session / "SHA256SUMS.tmp"
    with temp.open("w") as f:
        f.writelines(lines)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, session / "SHA256SUMS")
    with (DATA / "INDEX.csv").open("a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0, os.SEEK_END)
        writer = csv.writer(f, lineterminator="\n")
        if f.tell() == 0:
            writer.writerow(("session", "recorded_at", "seconds", "packets", "bytes", "raw_sha256"))
        writer.writerow((session.name, summary["started_at"], summary["wall_seconds"],
                         summary["packets"], summary["bytes"], summary["raw_sha256"]))
        f.flush()
        os.fsync(f.fileno())


def record(request, stop=None):
    # Enforce inside the recorder too: a direct service start or edited request
    # must not bypass the limit imposed by the command-line controller.
    limit = recording_limit(request["seconds"])
    duration_reason = "max_duration_reached" if limit == MAX_RECORDING_SECONDS else "duration_reached"
    stop = stop or threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, lambda _sig, _frame: stop.set())
    session = None
    first = last = None
    count = size = ignored = crc_bad = 0
    gap_sum = gap_max = 0.0
    digest = hashlib.sha256()
    error = None
    reason = "stopped"
    cleanup = []
    owns_sensor = False
    heartbeat = watchdog.Heartbeat(RUN / "heartbeat.json", request["request_id"], check_ethernet=True)
    progress = watchdog.StreamProgress()
    heartbeat.publish("starting")
    summary = {"request_id": request["request_id"],
               "seconds_requested": request.get("requested_seconds", request["seconds"]),
               "seconds_limit": limit, "max_continuous_seconds": MAX_RECORDING_SECONDS,
               "started_at": now(), "status": "starting", "packets": 0,
               "recorder": "pavewatch-lidar-control-v2", "measurement_left_running": None}
    atomic_json(STATE, summary)
    sock = None
    try:
        if shutil.disk_usage(DATA).free < RESERVE:
            raise RuntimeError("less than 1 GiB free; recording refused")
        # Bind before changing the sensor, so another collector cannot be displaced.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)
        sock.bind(("0.0.0.0", PORT))
        sock.settimeout(0.2)
        owns_sensor = True
        label = re.sub(r"[^a-z0-9]+", "-", request["label"].lower()).strip("-")[:64]
        suffix = "%gs" % limit
        name = "_".join(x for x in (datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), label, suffix) if x)
        session = DATA / "sessions" / name
        session.mkdir()
        summary["session"] = str(session)
        snapshot(session / "config_before.txt")
        if stop.is_set():
            reason = "stopped_before_start"
        else:
            sensor_start()
        enabled = time.monotonic()
        next_update = enabled
        if not stop.is_set():
            log("Recording requested: " + str(session))
        with (session / "raw.bin").open("wb") as raw:
            while not stop.is_set():
                tick = time.monotonic()
                if first is not None and tick - first >= limit:
                    reason = duration_reason
                    break
                if tick - (last if last is not None else enabled) > (5.0 if last is not None else 10.0):
                    raise TimeoutError("no sensor packets for " + ("5 seconds" if last is not None else "10 seconds after start"))
                if tick >= next_update:
                    free_bytes = shutil.disk_usage(DATA).free
                    heartbeat.publish(
                        "recording" if first is not None else "starting", session=str(session),
                        expected_streams={"lidar": watchdog.NS}, streams={"lidar": progress.snapshot()},
                        planned_stop_monotonic_ns=round((first + limit) * watchdog.NS) if first is not None else None,
                        host={"free_bytes": free_bytes, "storage_reserve_bytes": RESERVE},
                    )
                    if free_bytes < RESERVE:
                        raise RuntimeError("less than 1 GiB free; recording stopped")
                    summary.update(status="recording" if first is not None else "waiting_for_packets",
                                   packets=count, bytes=size, elapsed_seconds=round(tick - first, 3) if first is not None else 0)
                    atomic_json(STATE, summary)
                    next_update = tick + 1.0
                try:
                    packet, source = sock.recvfrom(65535)
                except socket.timeout:
                    continue
                received = time.time_ns()  # user-space receive time; same raw.bin framing as the original recorder
                tick = time.monotonic()
                if first is not None and tick - first >= limit:
                    reason = duration_reason
                    break
                if source[0] != IP:
                    ignored += 1
                    continue
                if first is None:
                    first = tick
                    summary["first_packet_wait_s"] = round(tick - enabled, 3)
                if last is not None:
                    gap = (tick - last) * 1000
                    gap_sum += gap
                    gap_max = max(gap_max, gap)
                last = tick
                frame = struct.pack("<QI", received, len(packet)) + packet
                raw.write(frame)
                digest.update(frame)
                count += 1
                size += len(packet)
                if len(packet) < 4 or zlib.crc32(packet[:-4]) & 0xFFFFFFFF != struct.unpack("<I", packet[-4:])[0]:
                    crc_bad += 1
                    progress.invalid_samples = crc_bad
                elif packet.startswith(b"\x02\x02\x02\x02\x01\0\0\0"):
                    progress.observe(round(tick * watchdog.NS))
            raw.flush()
            os.fsync(raw.fileno())
    except Exception as e:
        error = str(e)
        reason = "error"
    finally:
        heartbeat.publish("finalizing", session=str(session) if session is not None else None,
                          streams={"lidar": progress.snapshot()})
        if sock is not None:
            sock.close()
        # Neither a sensor/network failure nor a bad snapshot may skip metadata.
        cleanup = sensor_idle() if owns_sensor else []
        # Duration describes collection, excluding sensor cleanup time.
        elapsed = last - first if first is not None and last is not None else 0.0
        summary.update(status="failed" if error or cleanup else ("completed" if reason in ("duration_reached", "max_duration_reached") else "stopped"),
                       stop_reason=reason, stopped_at=now(), packets=count, bytes=size,
                       wall_seconds=round(elapsed, 6), elapsed_seconds=round(elapsed, 6),
                       ignored_other_sources=ignored, crc_failures=crc_bad,
                       gap_ms_mean_max=[round(gap_sum / (count - 1), 3), round(gap_max, 3)] if count > 1 else None,
                       raw_sha256=digest.hexdigest(), error=error, cleanup_errors=cleanup,
                       measurement_left_running=False if owns_sensor and not cleanup else None)
        try:
            if session is not None:
                if not (session / "raw.bin").exists():
                    (session / "raw.bin").touch()
                snapshot(session / "config_after.txt")
                finalize(session, summary)
        except Exception as e:
            summary["finalization_error"] = str(e)
            summary["status"] = "failed"
        atomic_json(STATE, summary)
        heartbeat.publish_terminal(summary)
        log("Recording %s: %s; %d packets, %d payload bytes; reason=%s; error=%s; cleanup=%s" %
            (summary["status"], str(session), count, size, reason, error, cleanup))
    return 1 if summary["status"] == "failed" else 0


def systemctl(*args):
    return subprocess.run(["systemctl", *args], text=True, capture_output=True, timeout=40)


def active_state():
    result = systemctl("show", UNIT, "--property=ActiveState", "--value")
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def legacy_recorders():
    found = []
    target = str(HOME / "03-sensor-payload-acquisition/tools/lidar_record.py")
    for p in Path("/proc").glob("[0-9]*"):
        try:
            args = (p / "cmdline").read_bytes().split(b"\0")
            # Only the known original Python recorder, never shell/SSH commands mentioning it.
            if len(args) > 1 and b"python" in Path(os.fsdecode(args[0])).name.encode():
                script = Path(os.fsdecode(args[1]))
                if not script.is_absolute():
                    script = (p / "cwd").resolve() / script
                if str(script.resolve()) == target:
                    found.append(int(p.name))
        except (OSError, ValueError):
            continue
    return found


def start(seconds, label):
    limit = recording_limit(seconds)
    if active_state() in ("active", "activating", "deactivating") or legacy_recorders():
        raise RuntimeError("a recorder is already running/stopping; use lidar status or lidar stop")
    assert_sensor_link()
    errors = recover_capture_sensor()
    if errors:
        raise RuntimeError("could not restore scanner idle: " + ", ".join(errors))
    request = {"request_id": uuid.uuid4().hex, "seconds": limit, "requested_monotonic_ns": time.monotonic_ns(),
               "requested_seconds": seconds, "label": label}
    atomic_json(RUN / "request.json", request)
    result = systemctl("start", UNIT)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    deadline = time.monotonic() + 18
    while time.monotonic() < deadline:
        state = read_json(STATE)
        if state.get("request_id") == request["request_id"]:
            if state.get("status") in ("recording", "completed", "stopped"):
                print("Recorder: " + state["status"])
                print("Session: " + state.get("session", "unknown"))
                print("Limit: %g seconds (maximum continuous recording: 20 minutes)" % limit)
                return
            if state.get("status") == "failed":
                raise RuntimeError("recording failed: " + json.dumps(state))
        if active_state() == "failed":
            raise RuntimeError("recorder service failed; run lidar status and journalctl -u " + UNIT)
        time.sleep(0.2)
    print("Recorder is still starting; run lidar status.")


def stop_recording():
    result = systemctl("stop", UNIT)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    old = legacy_recorders()
    for pid in old:
        try:
            os.kill(pid, signal.SIGINT)
        except ProcessLookupError:
            pass
    if old:
        deadline = time.monotonic() + 6
        while legacy_recorders() and time.monotonic() < deadline:
            time.sleep(0.1)
    try:
        assert_sensor_link()
    except ConnectionError as error:
        last = read_json(STATE)
        if last.get("capture_type") == "camera-diagnostic" and not CAPTURE_OWNER.is_file():
            log("Camera diagnostic stopped; no hardware LiDAR was used.")
            return
        log(f"Recorder service stopped; sensor idle unverified: {error}")
        raise
    try:
        idle = sensor_state() == {"SCdevicestate": 0, "ScanDataEnable": 0}
    except Exception:
        idle = False
    errors = [] if idle else sensor_idle()
    if legacy_recorders():
        errors.append("original recorder has not exited; sensor shutdown was attempted")
    if not errors:
        CAPTURE_OWNER.unlink(missing_ok=True)
    log("Stop requested; recorder service stopped; sensor " + ("measurement stopped, UDP output off" if not errors else "idle not verified: " + "; ".join(errors)))
    if errors:
        raise RuntimeError("; ".join(errors))


def status():
    print("Recorder service: " + active_state())
    print("Maximum continuous recording: 20 minutes (1200 seconds)")
    old = legacy_recorders()
    print("Original manual recorder PIDs: " + (", ".join(map(str, old)) if old else "none"))
    try:
        s = sensor_state()
        print("Sensor measurement: " + ("stopped" if s["SCdevicestate"] == 0 else "active (state %d)" % s["SCdevicestate"]))
        print("UDP output: " + ("off" if s["ScanDataEnable"] == 0 else "on"))
    except Exception as e:
        print("Sensor: unreachable or unreadable: " + str(e))
    last = read_json(STATE)
    if last:
        print("Current/last session: " + last.get("session", "none"))
        print("Session status: %s; %d packets" % (last.get("status"), last.get("packets", 0)))
        if last.get("recorder") == "pavewatch-collection-v2":
            print("Capture type: %s; %d saved camera frames" % (last.get("capture_type"), last.get("frames", 0)))
            if last.get("quality_flags"):
                print("Quality flags: " + ", ".join(last["quality_flags"]))
        if last.get("error") or last.get("cleanup_errors") or last.get("finalization_error"):
            print("Last errors: " + json.dumps({k: last.get(k) for k in ("error", "cleanup_errors", "finalization_error")}))
    watchdog.show_status(runtime=RUN)
    for folder in ("sessions", "derived"):
        count = sum(p.stat().st_size for p in (DATA / folder).rglob("*") if p.is_file())
        print("Stored %s: %.2f MB (%d bytes)" % (folder, count / 1e6, count))
    if CAPTURE_OWNER.is_file():
        print("A prior combined capture left scanner shutdown unverified.")
    print("Free storage: %.2f GB" % (shutil.disk_usage(DATA).free / 1e9))


def main():
    import managed_collect

    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("start", help="start in background; independent of SSH")
    p.add_argument("--seconds", type=float, default=MAX_RECORDING_SECONDS,
                   help="automatic stop after N seconds; default/maximum 1200 (20 minutes); 0 also uses the maximum")
    p.add_argument("--label", default="remote")
    p = sub.add_parser("capture", help="start the V2 camera and LiDAR capture")
    managed_collect.add_arguments(p)
    sub.add_parser("stop", help="stop recording and put the powered sensor in idle")
    sub.add_parser("status", help="show recorder, sensor and storage status")
    p = sub.add_parser("diagnostics", help="show the independent watchdog's latest report")
    p.add_argument("--json", action="store_true", help="print counters and alerts as JSON")
    sub.add_parser("idle-if-inactive", help=argparse.SUPPRESS)
    sub.add_parser("cleanup-capture", help=argparse.SUPPRESS)
    p = sub.add_parser("record", help=argparse.SUPPRESS)
    p.add_argument("--request", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "diagnostics":
        return watchdog.show_status(runtime=RUN, as_json=args.json)
    if args.action == "record":
        request = read_json(args.request)
        if request.get("kind") == "combined-v2":
            return managed_collect.record(sys.modules[__name__], request)
        return record(request)
    if args.action == "cleanup-capture":
        errors = recover_capture_sensor()
        if errors:
            log("Combined capture cleanup could not confirm sensor idle: " + ", ".join(errors))
        return int(bool(errors))
    if os.geteuid() != 0:
        raise PermissionError("run through /usr/local/bin/lidar, which uses existing passwordless sudo")
    RUN.mkdir(mode=0o755, exist_ok=True)
    # Serialize start and stop to prevent a stop/start race from re-enabling output.
    capture = None
    with CONTROL_LOCK.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if args.action == "start":
            start(args.seconds, args.label)
        elif args.action == "capture":
            capture = managed_collect.submit(sys.modules[__name__], args)
        elif args.action == "stop":
            stop_recording()
        elif args.action == "idle-if-inactive":
            if active_state() not in ("active", "activating", "deactivating") and not legacy_recorders():
                assert_sensor_link()
                if sensor_state() != {"SCdevicestate": 0, "ScanDataEnable": 0}:
                    errors = sensor_idle()
                    if errors:
                        raise RuntimeError(", ".join(errors))
                CAPTURE_OWNER.unlink(missing_ok=True)
        else:
            status()
    if capture:
        return managed_collect.wait_for_capture(sys.modules[__name__], capture, args.wait)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("Error: " + str(exc), file=sys.stderr)
        sys.exit(1)
