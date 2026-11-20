"""picoScan150 profile readback and Compact scan/IMU telemetry."""

from collections import Counter
from copy import deepcopy
import http.client
from ipaddress import IPv4Address
import json
import math
from pathlib import Path
from statistics import median
import struct
import zlib


MAGIC = 0x02020202
IMU_HEADER = struct.pack("<II", MAGIC, 2)
IMU_PACKET = struct.Struct("<III10fQI")
DEFAULT_IMU_PORT = 7503
FILTER_FIELDS = {
    "LFPmovingAveragingFilter": ("bEnable", "uiAveragingDepth"),
    "LFPintervalFilter": ("bEnable", "uiReductionFactor"),
    "LFPangleRangeFilter": ("bEnable", "fThetaStart", "fThetaStop", "fPhiStart", "fPhiStop", "uiBeamIncrement"),
    "LFPradialDistanceRangeFilter": ("bEnable", "ulDistMin", "ulDistMax"),
    "LFPcubicareafilter": ("bEnable", "lXMin", "lXMax", "lYMin", "lYMax"),
    "LFPparticle": ("bEnable", "uiThreshold"),
    "FREchoFilter": (),
    "MCSenseLevel": (),
}
DEFAULT_PROFILE = {
    "name": "pavewatch-50hz-025deg-276deg",
    "scan_rate_hz": 50.0,
    "angular_resolution_deg": 0.25,
    "field_of_view_deg": 276.0,
    "filters": {
        **{name: {"bEnable": False} for name, fields in FILTER_FIELDS.items() if fields},
        "FREchoFilter": 1,
        "MCSenseLevel": 0,
    },
}
TOLERANCES = {"scan_rate_hz": 0.5, "angular_resolution_deg": 0.005, "field_of_view_deg": 0.5}
MIN_OBSERVATIONS = 5


def load_profile(path):
    if path is None:
        return deepcopy(DEFAULT_PROFILE)
    profile = json.loads(path.read_text())
    if not isinstance(profile, dict) or set(profile) != set(DEFAULT_PROFILE):
        raise ValueError("LiDAR profile must contain name, scan_rate_hz, angular_resolution_deg, field_of_view_deg and filters")
    if not isinstance(profile["name"], str) or not profile["name"].strip():
        raise ValueError("LiDAR profile name must be a nonempty string")
    for name in TOLERANCES:
        value = profile[name]
        if type(value) not in (int, float) or not 0 < value <= 360:
            raise ValueError(f"LiDAR profile {name} must be a positive finite number within 360")
    filters = profile["filters"]
    if not isinstance(filters, dict) or not filters:
        raise ValueError("LiDAR profile filters must be a nonempty object")
    for name, value in filters.items():
        if name not in FILTER_FIELDS:
            raise ValueError(f"unknown picoScan150 filter {name}")
        fields = FILTER_FIELDS[name]
        if fields:
            if not isinstance(value, dict) or not value or not value.keys() <= set(fields):
                raise ValueError(f"invalid fields for {name}, expected {', '.join(fields)}")
            if any(type(item) is not (bool if key == "bEnable" else int) for key, item in value.items()):
                raise ValueError(f"{name} requires a boolean bEnable and integer parameters")
        elif type(value) is not int or not 0 <= value <= (2 if name == "FREchoFilter" else 1):
            raise ValueError(f"invalid picoScan150 filter value for {name}")
    return profile


def add_arguments(parser):
    parser.add_argument("--lidar-profile-file", type=Path, help="JSON file with the named expected LiDAR settings")
    parser.add_argument("--imu-port", type=udp_port,
                        help="override the IMU receive port (scanner readback or UDP 7503 by default)")


def udp_port(text):
    port = int(text)
    if not 1 <= port <= 65535:
        raise ValueError("UDP port must be 1–65535")
    return port


def decode_imu(payload):
    if len(payload) != IMU_PACKET.size:
        raise ValueError(f"expected {IMU_PACKET.size} bytes for Compact IMU")
    magic, kind, version, *values, stamp, crc = IMU_PACKET.unpack(payload)
    if (magic, kind, version) != (MAGIC, 2, 1):
        raise ValueError("unsupported Compact Type 2 header")
    if zlib.crc32(memoryview(payload)[:-4]) != crc:
        raise ValueError("CRC32 mismatch")
    if not all(map(math.isfinite, values)):
        raise ValueError("non-finite IMU measurement")
    return {
        "telegram_version": version, "sensor_timestamp_us": stamp,
        "acceleration_m_s2_xyz": values[:3], "angular_velocity_rad_s_xyz": values[3:6],
        "orientation_quaternion_wxyz": values[6:],
    }


def scan_geometry(payload, row_metadata, data_start, end, beams, echoes):
    """Read a single-row Compact module's angular window and beam spacing."""
    start, stop = struct.unpack_from("<ff", payload, row_metadata + 20)
    if not (-math.pi <= start <= stop <= math.pi) or beams < 2:
        return None
    _, echo_flags, beam_flags, _ = struct.unpack_from("<4B", payload, data_start - 4)
    if beam_flags & 2:
        azimuth_offset = 2 * echoes * ((echo_flags & 1) + bool(echo_flags & 2)) + (beam_flags & 1)
        stride = azimuth_offset + 2
        if echo_flags & ~3 or beam_flags & ~3 or data_start + beams * stride != end:
            return None
        # Sample a baseline from the start of the segment. The final segment can
        # contain beam slots past the nominal stop angle, even with all ranges zero.
        baseline = min(64, beams - 1)
        first = struct.unpack_from("<H", payload, data_start + azimuth_offset)[0]
        later = struct.unpack_from("<H", payload, data_start + azimuth_offset + baseline * stride)[0]
        if abs((first - 16384) / 5215 - start) > 0.0004 or later <= first:
            return None
        step = (later - first) / (5215 * baseline)
    else:
        step = (stop - start) / (beams - 1)
    if step <= 0:
        return None
    return {
        "start_azimuth_deg": math.degrees(start), "stop_azimuth_deg": math.degrees(stop),
        "angular_resolution_deg": math.degrees(step),
        "angle_source": "per-beam azimuth" if beam_flags & 2 else "module endpoints",
    }


class ScanObservation:
    """Summarize recurring scan windows and the sensor-native frame cadence."""

    def __init__(self):
        self.sender = None
        self.mixed_senders = False
        self.frame = None
        self.segments = {}
        self.frame_windows = Counter()
        self.first_frame = True
        self.previous_frame = None
        self.frame_periods_us = []
        self.received_periods_us = []
        self.echo_counts = Counter()
        self.interior_frames = 0

    def observe(self, source_ip, module):
        sender = (source_ip, module["sender_id"])
        if self.sender is None:
            self.sender = sender
        if sender != self.sender:
            self.mixed_senders = True
            return
        self.echo_counts[str(module["echoes_per_beam"])] += 1
        frame = module["frame_number"]
        if frame != self.frame:
            if self.frame is not None:
                if frame < self.frame:
                    return
                if not self.first_frame:
                    self.finish_frame()
                self.first_frame = False
            self.frame = frame
            self.segments = {}
        if module.get("scan_geometry"):
            self.segments[module["segment_counter"]] = module

    def finish_frame(self):
        self.interior_frames += 1
        ordered = sorted(self.segments.values(), key=lambda item: item["scan_geometry"]["start_azimuth_deg"])
        if not ordered:
            return
        geometry = [item["scan_geometry"] for item in ordered]
        step = median(item["angular_resolution_deg"] for item in geometry)
        if any(abs(item["angular_resolution_deg"] - step) > TOLERANCES["angular_resolution_deg"]
               for item in geometry if item["angle_source"] == "per-beam azimuth"):
            return
        if any(abs(b["start_azimuth_deg"] - a["stop_azimuth_deg"] - step) > 0.03
               for a, b in zip(geometry, geometry[1:])):
            return
        start = geometry[0]["start_azimuth_deg"]
        stop = geometry[-1]["stop_azimuth_deg"]
        signature = (round(start, 2), round(stop, 2), round(step, 3), len(geometry))
        self.frame_windows[signature] += 1
        stamp = ordered[0]["timestamp_start_us"][0]
        previous = self.previous_frame
        self.previous_frame = (self.frame, stamp, signature)
        if previous and signature == previous[2] and stamp > previous[1] > 0:
            elapsed = stamp - previous[1]
            period = elapsed / (self.frame - previous[0])
            if 5_000 <= period <= 200_000:
                self.frame_periods_us.append(period)
                self.received_periods_us.append(elapsed)

    def summary(self):
        windows = self.frame_windows.most_common(1)
        start, stop, step, segments = windows[0][0] if windows else (None, None, None, None)
        consistent_frames = windows[0][1] if windows else 0
        contiguous_frames = sum(self.frame_windows.values())
        period_count = len(self.frame_periods_us)
        scan_rate = 1e6 / median(self.frame_periods_us) if period_count else None
        consistent_periods = sum(abs(1e6 / value - scan_rate) <= TOLERANCES["scan_rate_hz"]
                                 for value in self.frame_periods_us) if period_count else 0
        return {
            "scan_rate_hz": round(scan_rate, 4) if scan_rate is not None else None,
            "received_frame_rate_hz": round(1e6 / median(self.received_periods_us), 4) if period_count else None,
            "angular_resolution_deg": step, "field_of_view_deg": round(stop - start, 2) if windows else None,
            "start_azimuth_deg": start, "stop_azimuth_deg": stop, "segments_per_observed_frame": segments,
            "interior_frames": self.interior_frames, "contiguous_frames": contiguous_frames,
            "frames_matching_window": consistent_frames, "scan_period_samples": period_count,
            "scan_period_samples_near_median": consistent_periods,
            "geometry_stable": consistent_frames >= MIN_OBSERVATIONS and consistent_frames >= 0.9 * contiguous_frames,
            "scan_rate_stable": period_count >= MIN_OBSERVATIONS and consistent_periods >= 0.9 * period_count,
            "mixed_senders": self.mixed_senders,
            "echoes_per_beam_module_counts": dict(self.echo_counts),
        }


def cola_values(reply, name):
    parts = reply.split()
    if len(parts) > 2 and parts[0] == "sRA" and parts[1].lower() == name.lower():
        return parts[2:]
    return []


def cola_int(token, signed=False):
    value = int(token, 10) if token.startswith(("+", "-")) else int(token, 16)
    return value - 2 ** 32 if signed and 2 ** 31 <= value < 2 ** 32 else value


def scan_configuration(reply):
    try:
        rate, sector, step, first, last = cola_values(reply, "LMPscancfg")
        start = cola_int(first, signed=True) / 1e4
        stop = cola_int(last, signed=True) / 1e4
        if cola_int(sector) == 1 and stop > start:
            return {"scan_rate_hz": cola_int(rate) / 100, "angular_resolution_deg": cola_int(step) / 1e4,
                    "field_of_view_deg": round(stop - start, 4), "start_azimuth_deg": start, "stop_azimuth_deg": stop}
    except ValueError:
        pass
    return None


def rest_settings(address, listen):
    """Read the documented picoScan150 REST settings without authenticating."""
    names = (*FILTER_FIELDS, "PerformanceProfileNumber", "ImuDataEnable", "ImuDataEthSettings")
    settings, errors = {}, {}
    source = None if listen == "0.0.0.0" else (listen, 0)
    connection = http.client.HTTPConnection(address, timeout=0.4, source_address=source)
    try:
        for name in names:
            try:
                connection.request("GET", f"/api/{name}", headers={"Accept": "application/json"})
                response = connection.getresponse()
                raw = response.read(65537)
            except (OSError, http.client.HTTPException) as exc:
                errors[name] = f"{type(exc).__name__}: {exc}"
                break
            if response.status != 200 or len(raw) > 65536:
                errors[name] = f"HTTP {response.status}, {len(raw)} bytes"
                continue
            try:
                reply = json.loads(raw)
                header, data = reply["header"], reply["data"]
                if header.get("status") != 0 or not isinstance(data, dict) or not data:
                    raise ValueError(f"invalid or rejected REST reply, status {header.get('status')}")
                value = data[name] if name in data else data
                # Prevent nonstandard NaN/Infinity values from entering the manifest.
                json.dumps(value, allow_nan=False)
                settings[name] = value
            except (AttributeError, KeyError, TypeError, ValueError) as exc:
                errors[name] = str(exc)
    finally:
        connection.close()
    return settings, errors


def decode_snapshot(cola, rest):
    settings = dict(rest)
    for name, fields in FILTER_FIELDS.items():
        if name in settings:
            continue
        values = cola_values(cola.get(name, ""), name)
        try:
            if not fields and len(values) == 1:
                settings[name] = cola_int(values[0])
            elif len(values) == len(fields) and values and values[0] in ("0", "1", "+0", "+1", "00", "01"):
                settings[name] = {
                    field: bool(cola_int(value)) if field == "bEnable" else cola_int(value, signed=True)
                    for field, value in zip(fields, values)
                }
        except ValueError:
            continue
    for name in ("PerformanceProfileNumber", "ImuDataEnable"):
        values = cola_values(cola.get(name, ""), name)
        if name not in settings and len(values) == 1:
            try:
                value = cola_int(values[0])
                if name == "PerformanceProfileNumber" or value in (0, 1):
                    settings[name] = bool(value) if name == "ImuDataEnable" else value
            except ValueError:
                pass
    destination = cola_values(cola.get("ImuDataEthSettings", ""), "ImuDataEthSettings")
    if "ImuDataEthSettings" not in settings and len(destination) == 6:
        try:
            protocol, *address, port = map(cola_int, destination)
            settings["ImuDataEthSettings"] = {"Protocol": protocol, "IPAddress": address, "Port": port}
        except ValueError:
            pass
    return {
        "scan_configuration": scan_configuration(cola.get("LMPscancfg", "")),
        "filters": {name: settings.get(name) for name in FILTER_FIELDS},
        "sensor_performance_profile": settings.get("PerformanceProfileNumber"),
        "imu_data_enable": settings.get("ImuDataEnable"),
        "imu_data_eth_settings": settings.get("ImuDataEthSettings"),
    }


def imu_udp_destination(settings):
    if not isinstance(settings, dict) or settings.get("Protocol") != 1:
        return None
    port = settings.get("Port")
    address = settings.get("IPAddress")
    if type(port) is not int or not 1 <= port <= 65535 or not isinstance(address, list):
        return None
    try:
        return str(IPv4Address(bytes(address))), port
    except (TypeError, ValueError):
        return None


def compare_filter(expected, actual):
    if actual is None:
        return "unverified"
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return "unverified"
        checks = [compare_filter(value, actual.get(key)) for key, value in expected.items()]
        return combine_checks(checks)
    if type(expected) is not type(actual):
        return "unverified"
    return "verified" if actual == expected else "mismatch"


def combine_checks(checks):
    if "mismatch" in checks:
        return "mismatch"
    return "verified" if all(check == "verified" for check in checks) else "unverified"


def verify_profile(requested, before, after, stream):
    checks = {}
    for name, tolerance in TOLERANCES.items():
        observed = stream.get(name)
        stable = stream.get("scan_rate_stable" if name == "scan_rate_hz" else "geometry_stable")
        if observed is None or not stable or stream.get("mixed_senders"):
            checks[name] = "unverified"
        else:
            checks[name] = "verified" if abs(requested[name] - observed) <= tolerance else "mismatch"
    filters_before = before.get("filters", {})
    filters_after = after.get("filters", {})
    checks["filters"] = {
        name: combine_checks([compare_filter(value, found.get(name)) for found in (filters_before, filters_after)])
        for name, value in requested["filters"].items()
    }
    changed = [name for name in FILTER_FIELDS
               if filters_before.get(name) is not None and filters_after.get(name) is not None
               and filters_before[name] != filters_after[name]]
    for name in ("scan_configuration", "sensor_performance_profile"):
        if before.get(name) is not None and after.get(name) is not None and before[name] != after[name]:
            changed.append(name)
    # LMPscancfg describes the pre-filter scan. The packet geometry can be
    # deliberately cropped, so only compare like quantities here.
    readback = {}
    for phase, snapshot in (("before", before), ("after", after)):
        configured = snapshot.get("scan_configuration") or {}
        angle_filter = snapshot.get("filters", {}).get("LFPangleRangeFilter")
        comparable = TOLERANCES if isinstance(angle_filter, dict) and angle_filter.get("bEnable") is False else (
            "scan_rate_hz",
        )
        readback[phase] = {
            name: "verified" if abs(configured[name] - requested[name]) <= TOLERANCES[name] else "mismatch"
            for name in comparable if name in configured
        }
    status = combine_checks([checks[name] for name in TOLERANCES] + list(checks["filters"].values())
                            + list(readback["before"].values()) + list(readback["after"].values()))
    return {"status": "mismatch" if changed else status, "checks": checks,
            "scan_configuration_checks": readback, "tolerances": TOLERANCES, "configuration_changes": changed}
