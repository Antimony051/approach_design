#!/usr/bin/env python3
"""Monitor PaveWatch capture progress without reading sensor data files."""

import argparse
import ctypes
import json
import os
from pathlib import Path
import re
import signal
from threading import Event
import time


NS = 1_000_000_000
POLL_SECONDS = 1.0
STALE_NS = 3 * NS
STARTUP_LIMIT_NS = 30 * NS
FINALIZATION_LIMIT_NS = 30 * NS
TERMINAL = ("completed", "stopped", "failed")
DEFAULT_RUNTIME = Path("/run/pavewatch-lidar")
DEFAULT_STATE = Path("/var/lib/pavewatch-lidar/state.json")
DEFAULT_OUTPUT = Path("/run/pavewatch-watchdog/status.json")
DEFAULT_ARCHIVE = Path("/var/lib/pavewatch-watchdog")


def read_object(path):
    try:
        with path.open("rb") as stream:
            data = json.loads(stream.read(65536))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def write_status(path, data):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w") as stream:
        json.dump(data, stream, separators=(",", ":"), allow_nan=False)
        stream.write("\n")
    temporary.replace(path)


def process_start_ticks(pid):
    """Use Linux process start ticks to distinguish a running recorder from a reused PID."""
    try:
        fields = (Path("/proc") / str(pid) / "stat").read_text().rsplit(")", 1)[1].split()
        if fields[0] not in ("Z", "X"):
            return int(fields[19])
    except (OSError, ValueError, IndexError):
        pass
    return None


class StreamProgress(ctypes.Structure):
    """Shared counters with one writer per stream and no lock on the recorder's hot path."""

    _fields_ = [(name, ctypes.c_uint64) for name in
                ("samples", "last_sample_monotonic_ns", "long_gaps", "invalid_samples", "drop_indicators")]

    def observe(self, now, gap_limit_ns=NS):
        previous = self.last_sample_monotonic_ns
        if previous and now - previous > gap_limit_ns:
            self.long_gaps += 1
        self.last_sample_monotonic_ns = now
        self.samples += 1

    def snapshot(self):
        return {name: getattr(self, name) for name, _ in self._fields_}


class Heartbeat:
    """Publish a small snapshot to tmpfs without waiting on the survey drive."""

    def __init__(self, path, request_id, session=None, *, check_ethernet=False):
        self.path = path
        self.data = {
            "request_id": request_id, "session": str(session) if session is not None else None,
            "pid": os.getpid(), "process_start_ticks": process_start_ticks(os.getpid()),
            "check_ethernet": check_ethernet,
        }
        self.write_error = False

    def publish(self, phase, **fields):
        now = time.monotonic_ns()
        if phase != self.data.get("phase"):
            self.data["phase_since_monotonic_ns"] = now
        self.data.update(fields, phase=phase, heartbeat_monotonic_ns=now)
        try:
            write_status(self.path, self.data)
        except OSError as exc:
            if not self.write_error:
                print(f"Recorder heartbeat unavailable: {exc}", flush=True)
            self.write_error = True
        else:
            self.write_error = False

    def publish_terminal(self, state):
        # Keep the last terminal record available while a new capture claims state.json.
        try:
            write_status(self.path.with_name("terminal.json"), state)
        except OSError as exc:
            print(f"Recorder terminal heartbeat unavailable: {exc}", flush=True)


def event(code, severity, detail):
    return {"code": code, "severity": severity, "detail": detail}


def streaming_alerts(heartbeat, age, now):
    if age > STALE_NS:
        return [event("recorder_heartbeat_stale", "error", f"Recorder heartbeat is {age / NS:.1f} s old")]
    alerts = []
    sampled = heartbeat["heartbeat_monotonic_ns"]
    if sampled < (heartbeat.get("planned_stop_monotonic_ns") or now + 1):
        for stream, limit in heartbeat.get("expected_streams", {}).items():
            progress = heartbeat.get("streams", {}).get(stream, {})
            last = progress.get("last_sample_monotonic_ns") or heartbeat["phase_since_monotonic_ns"]
            gap = sampled - last
            if gap > limit:
                label = {"camera": "saved camera frames", "lidar": "valid LiDAR scan packets", "imu": "valid IMU samples"}[stream]
                alerts.append(event(f"{stream}_stalled", "warning" if stream == "imu" else "error",
                                    f"No {label} for {gap / NS:.1f} s"))
    alerts.extend(quality_alerts(heartbeat))
    if heartbeat.get("check_ethernet"):
        try:
            carrier = Path("/sys/class/net/eth0/carrier").read_text().strip()
        except OSError:
            carrier = None
        if carrier == "0":
            alerts.append(event("lidar_ethernet_down", "error", "LiDAR Ethernet eth0 has no carrier"))
    host = heartbeat.get("host", {})
    free = host.get("free_bytes")
    if free is not None and free < host.get("storage_reserve_bytes", 0):
        alerts.append(event("storage_reserve_reached", "error", f"Recording filesystem has {free // 1024 ** 2} MiB free"))
    if host.get("undervoltage_active"):
        alerts.append(event("pi_undervoltage", "warning", "Pi reports active undervoltage"))
    if (host.get("pi_throttled_bitmask") or 0) & 0xE:
        alerts.append(event("pi_throttling", "warning", "Pi reports throttling, a frequency cap, or a temperature limit"))
    if host.get("clock_segment", 0):
        alerts.append(event("host_clock_anchor_break", "warning", "Recorder reported a break in host clock anchors"))
    return alerts


def quality_alerts(heartbeat):
    alerts = []
    for stream, progress in heartbeat.get("streams", {}).items():
        for field, label in (("long_gaps", "long sample gaps"), ("invalid_samples", "invalid samples"),
                             ("drop_indicators", "possible dropped samples")):
            count = progress.get(field, 0)
            if count:
                alerts.append(event(f"{stream}_{field}", "warning", f"{count} {label} in {stream}"))
    return alerts


class WatchRun:
    def __init__(self, request, previous):
        self.request_id = request["request_id"]
        self.requested_ns = request["requested_monotonic_ns"]
        self.session = request.get("session")
        self.finished = previous.get("phase") in TERMINAL
        self.history = previous.get("faults", {})
        self.active = {item["code"] for item in previous.get("active_alerts", [])}
        self.heartbeat = {}

    def evaluate(self, heartbeat, state, now):
        if state.get("status") in TERMINAL:
            phase = state["status"]
            alerts = quality_alerts(heartbeat)
            if phase == "failed":
                detail = state.get("finalization_error") or state.get("error") or "Recorder reported failure"
                alerts.append(event("recorder_failed", "error", detail))
            if state.get("cleanup_errors"):
                alerts.append(event("sensor_cleanup_failed", "error", " / ".join(state["cleanup_errors"])))
            if state.get("quality_flags"):
                alerts.append(event("recorder_quality_flags", "warning", ", ".join(state["quality_flags"])))
            return phase, alerts

        pid = heartbeat.get("pid")
        identity = heartbeat.get("process_start_ticks")
        # Read the terminal state again in the polling loop if exit and publication race.
        if pid and identity is not None and process_start_ticks(pid) != identity:
            return "failed", [event("recorder_exited", "error", f"Recorder PID {pid} exited without a terminal capture status")]
        phase = heartbeat.get("phase", "starting")
        age = now - heartbeat.get("heartbeat_monotonic_ns", self.requested_ns)
        if not heartbeat and state.get("status") == "recording" and age > STALE_NS:
            return "recording", [event("recorder_heartbeat_missing", "error", "Recorder has no readable heartbeat")]
        if phase == "starting" and now - self.requested_ns > STARTUP_LIMIT_NS:
            return phase, [event("recorder_startup_timeout", "error", "Recorder did not enter capture within 30 s")]
        if phase == "finalizing" and now - heartbeat["phase_since_monotonic_ns"] > FINALIZATION_LIMIT_NS:
            return phase, [event("recorder_finalization_timeout", "error", "Recorder has been finalizing for over 30 s")]
        if phase == "recording":
            alerts = streaming_alerts(heartbeat, age, now)
            if now - (heartbeat.get("planned_stop_monotonic_ns") or now) > STALE_NS:
                alerts.append(event("recorder_overrun", "error", "Recorder is past its scheduled stop"))
            return phase, alerts
        return phase, []

    def report(self, heartbeat, state, now, phase, alerts):
        observed_at = time.time_ns()
        current = {item["code"] for item in alerts}
        finished = phase in TERMINAL
        for item in alerts:
            code = item["code"]
            history = self.history.setdefault(code, {"first_monotonic_ns": now, "first_realtime_ns": observed_at,
                                                      "activations": 0})
            if code not in self.active:
                print(json.dumps({"event": "alert_raised", "request_id": self.request_id,
                                  "monotonic_ns": now, "realtime_ns": observed_at, **item}), flush=True)
                history["activations"] += 1
            history.update(item, last_monotonic_ns=now, last_realtime_ns=observed_at)
        if not finished:
            for code in sorted(self.active - current):
                print(json.dumps({"event": "alert_cleared", "request_id": self.request_id, "code": code,
                                  "monotonic_ns": now, "realtime_ns": observed_at}), flush=True)
        self.active = current
        self.session = heartbeat.get("session") or state.get("session") or self.session
        self.finished = finished
        stamp = heartbeat.get("heartbeat_monotonic_ns")
        known = self.history.values() if self.finished else alerts
        severity = "error" if any(item["severity"] == "error" for item in known) else "warning" if known else "ok"
        return {
            "schema": "pavewatch-recorder-diagnostics-v1", "request_id": self.request_id, "session": self.session,
            "phase": phase, "severity": severity, "checked_monotonic_ns": now, "checked_realtime_ns": observed_at,
            "heartbeat_monotonic_ns": stamp, "heartbeat_age_ms": (now - stamp) // 1_000_000 if stamp else None,
            "streams": heartbeat.get("streams", {}), "host": heartbeat.get("host", {}),
            "active_alerts": alerts, "faults": self.history,
        }


def matched(path, request_id):
    data = read_object(path)
    return data if data.get("request_id") == request_id else {}


def sample(run, runtime, state_path, output, archive, superseded=False):
    request_id = run.request_id
    heartbeat = matched(runtime / "heartbeat.json", request_id)
    if all(isinstance(heartbeat.get(key), int) for key in ("heartbeat_monotonic_ns", "phase_since_monotonic_ns")):
        run.heartbeat = heartbeat
    heartbeat = run.heartbeat
    state = matched(runtime / "terminal.json", request_id) or matched(state_path, request_id)
    now = time.monotonic_ns()
    phase, alerts = run.evaluate(heartbeat, state, now)
    if phase == "failed" and state.get("status") not in TERMINAL:
        # The recorder may have published its terminal state since this sample began.
        newer = matched(runtime / "terminal.json", request_id) or matched(state_path, request_id)
        if newer.get("status") in TERMINAL:
            state = newer
            phase, alerts = run.evaluate(heartbeat, state, now)
    if superseded and phase not in TERMINAL:
        phase = "failed"
        alerts = [event("recorder_status_missing", "error", "Capture was replaced before a terminal status was published")]
    report = run.report(heartbeat, state, now, phase, alerts)
    if run.finished:
        archive_path = archive / f"{request_id}.json"
        try:
            report["archive"] = str(archive_path)
            write_status(archive_path, report)
        except OSError as exc:
            report.pop("archive", None)
            report["archive_error"] = str(exc)
            print(f"Diagnostic report remains in {output}: {exc}", flush=True)
    write_status(output, report)


def watch(runtime, state_path, output, archive, stop):
    output.parent.mkdir(parents=True, exist_ok=True)
    archive.mkdir(parents=True, exist_ok=True)
    watch_run = None
    previous = read_object(output)
    while not stop.is_set():
        request = read_object(runtime / "request.json")
        request_id = request.get("request_id")
        requested_ns = request.get("requested_monotonic_ns")
        if (isinstance(request_id, str) and re.fullmatch(r"[0-9a-f]{32}", request_id)
                and isinstance(requested_ns, int)):
            if watch_run is None or watch_run.request_id != request_id:
                if watch_run is not None and not watch_run.finished:
                    sample(watch_run, runtime, state_path, output, archive, superseded=True)
                watch_run = WatchRun(request, previous if previous.get("request_id") == request_id else {})
            if not watch_run.finished:
                sample(watch_run, runtime, state_path, output, archive)
        stop.wait(POLL_SECONDS)


def current_status(runtime=DEFAULT_RUNTIME, output=DEFAULT_OUTPUT):
    request = read_object(runtime / "request.json")
    report = matched(output, request.get("request_id")) if request else {}
    if report and report["phase"] not in TERMINAL:
        report["status_stale"] = time.monotonic_ns() - report["checked_monotonic_ns"] > STALE_NS
    return report


def show_status(runtime=DEFAULT_RUNTIME, output=DEFAULT_OUTPUT, as_json=False):
    report = current_status(runtime, output)
    if as_json:
        print(json.dumps(report, indent=2))
    elif not report:
        print("Watchdog: waiting for a monitored capture")
    elif report.get("status_stale"):
        print("Watchdog: status is stale")
    else:
        print(f"Watchdog: {report['phase']} ({report['severity']})")
        if report.get("archive"):
            print(f"Run diagnostics: {report['archive']}")
        if report.get("archive_error"):
            print(f"Diagnostic archive unavailable: {report['archive_error']}")
        issues = report["faults"].values() if report["phase"] in TERMINAL else report["active_alerts"]
        for fault in issues:
            print(f"  {fault['severity']}: {fault['detail']}")
    return int(not report or report.get("status_stale") or report["severity"] == "error")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--status", action="store_true", help="show the latest report and exit")
    parser.add_argument("--json", action="store_true", help="print the report as JSON with --status")
    args = parser.parse_args()
    if args.status:
        return show_status(args.runtime, args.output, args.json)
    stop = Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    watch(args.runtime, args.state, args.output, args.archive, stop)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
