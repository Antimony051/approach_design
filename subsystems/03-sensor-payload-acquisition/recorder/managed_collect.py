"""Run the combined recorder through the Pi's shared LiDAR service."""

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import subprocess
import time
import uuid

import lidar_telemetry as telemetry
from recorder_watchdog import Heartbeat


def add_arguments(parser):
    parser.add_argument("legacy_label", nargs="?")
    parser.add_argument("legacy_seconds", nargs="?", type=float)
    parser.add_argument("--label")
    parser.add_argument("--seconds", type=float)
    parser.add_argument("--profile", choices=("auto", "imx219-bench", "imx219-full",
                                             "imx708-bench", "imx708-flight"), default="auto")
    parser.add_argument("--w", type=int, help="legacy width used with --h")
    parser.add_argument("--h", type=int, help="legacy height used with --w")
    parser.add_argument("--fps", type=float)
    exposure = parser.add_mutually_exclusive_group()
    exposure.add_argument("--exposure-us", "--shutter", type=int, default=1000,
                          help="fixed exposure in microseconds, or zero for auto")
    exposure.add_argument("--auto-exposure", action="store_true")
    parser.add_argument("--gain", type=float, default=1.0)
    parser.add_argument("--lens-position", type=float, help="manual lens position in diopters")
    parser.add_argument("--note", default="", help="route, weather, rig and test notes")
    parser.add_argument("--out", type=Path, help="existing writable survey-media directory")
    parser.add_argument("--calibration-id")
    parser.add_argument("--calibration-file", type=Path)
    parser.add_argument("--context-file", type=Path)
    parser.add_argument("--pose-file", type=Path)
    telemetry.add_arguments(parser)
    parser.add_argument("--allow-unsynced", action="store_true", help="diagnostic collection with a suspect scanner clock")
    parser.add_argument("--test-camera", action="store_true", help="record the real camera and localhost LiDAR fixtures")
    parser.add_argument("--wait", action="store_true", help="wait for recording to finalize")


def output_directory(control, path, test_camera):
    if path is None:
        return control.DATA / ("diagnostics-v2" if test_camera else "collections-v2")
    if not path.is_dir():
        raise ValueError(f"recording directory must already exist: {path}")
    output = path.resolve()
    result = subprocess.run(["findmnt", "-n", "-o", "TARGET", "-T", str(output)],
                            check=True, capture_output=True, text=True, timeout=2)
    if result.stdout.strip() == "/" and not output.is_relative_to(control.DATA.resolve()):
        raise ValueError(f"{output} is on boot storage outside the recorder's data directory")
    return output


def submit(control, args):
    if args.label is not None and args.legacy_label is not None:
        raise ValueError("supply the label once")
    if args.seconds is not None and args.legacy_seconds is not None:
        raise ValueError("supply the duration once")
    if control.active_state() in ("active", "activating", "deactivating") or control.legacy_recorders():
        raise RuntimeError("a recorder already owns the acquisition service")

    label = args.label or args.legacy_label or ("camera-test" if args.test_camera else "survey")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", label):
        raise ValueError("label must contain 1–48 letters, digits, hyphens or underscores")
    seconds = args.seconds if args.seconds is not None else args.legacy_seconds
    seconds = 30 if seconds is None else seconds
    if not math.isfinite(seconds) or not 1 <= seconds <= control.MAX_RECORDING_SECONDS:
        raise ValueError("capture duration must be between 1 and 1200 seconds")
    telemetry.load_profile(args.lidar_profile_file)
    profile = args.profile
    if args.w is not None or args.h is not None:
        sizes = {(3280, 2464): "imx219-full", (1640, 1232): "imx219-bench",
                 (2304, 1296): "imx708-bench", (4608, 2592): "imx708-flight"}
        geometry_profile = sizes.get((args.w, args.h))
        if geometry_profile is None or (profile != "auto" and profile != geometry_profile):
            raise ValueError("requested width and height do not match a supported profile")
        profile = geometry_profile

    if not args.test_camera:
        control.assert_sensor_link()
        errors = control.recover_capture_sensor()
        if errors:
            raise RuntimeError("could not restore scanner idle: " + ", ".join(errors))
    out = output_directory(control, args.out, args.test_camera)
    run_id = f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}_{label}"
    request = {
        "request_id": uuid.uuid4().hex, "kind": "combined-v2", "label": label,
        "requested_monotonic_ns": time.monotonic_ns(),
        "seconds": seconds, "test_camera": args.test_camera, "allow_unsynced": args.allow_unsynced,
        "session": str(out / run_id), "profile": profile, "fps": args.fps,
        "storage_device": out.stat().st_dev if out.is_dir() else None,
        "exposure_us": args.exposure_us, "auto_exposure": args.auto_exposure or args.exposure_us == 0,
        "gain": args.gain, "lens_position": args.lens_position, "note": args.note,
        "calibration_id": args.calibration_id,
        "imu_port": args.imu_port,
        **{key: str(value.resolve()) if value is not None else None
           for key, value in (("calibration_file", args.calibration_file),
                              ("context_file", args.context_file), ("pose_file", args.pose_file),
                              ("lidar_profile_file", args.lidar_profile_file))},
    }
    control.atomic_json(control.RUN / "request.json", request)
    result = control.systemctl("start", control.UNIT)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    print("Run: " + request["session"], flush=True)
    return request


def wait_for_capture(control, request, wait):
    deadline = time.monotonic() + (request["seconds"] + 45 if wait else 22)
    while time.monotonic() < deadline:
        state = control.read_json(control.STATE)
        service = control.active_state()
        if state.get("request_id") == request["request_id"]:
            status = state.get("status")
            if status in ("completed", "failed", "stopped") or (status == "recording" and not wait):
                if wait and service in ("active", "activating", "deactivating"):
                    time.sleep(0.2)
                    continue
                print(f"Recorder: {status}")
                if state.get("error"):
                    print("Capture detail: " + state["error"])
                if state.get("quality_flags"):
                    print("Quality flags: " + ", ".join(state["quality_flags"]))
                return 1 if status == "failed" or service == "failed" else 0
        if service == "failed":
            raise RuntimeError(f"capture service failed; check journalctl -u {control.UNIT}")
        time.sleep(0.2)
    print("The recorder is still running. Use collect status to check progress.")
    return int(wait)


class Scanner:
    def __init__(self, control, request_id):
        self.control = control
        self.request_id = request_id
        self.attempted = False

    def start(self):
        c = self.control
        with c.Cola() as connection:
            identity = connection.request("sRN DeviceIdent")
        if not identity.startswith("sRA DeviceIdent ") or "picoscan" not in identity.lower():
            raise RuntimeError("the configured Ethernet peer did not identify as a picoScan")
        state = c.sensor_state()
        if state["ScanDataEnable"] != 0:
            raise RuntimeError("the LiDAR stream is already enabled; check collect status")
        c.atomic_json(c.CAPTURE_OWNER, {"request_id": self.request_id, "attempted_at": c.now()})
        self.attempted = True
        c.sensor_start()

    def idle(self):
        return self.control.recover_capture_sensor() if self.attempted else []

    def snapshot(self, path, variables):
        try:
            return self.control.snapshot(path, variables=variables)
        except OSError as exc:
            print(f"Sensor settings snapshot failed: {exc}", flush=True)
            return {}


def record(control, request):
    from collect_v2 import main

    session = Path(request["session"])
    test_camera = request["test_camera"]
    heartbeat = Heartbeat(control.RUN / "heartbeat.json", request["request_id"], session,
                          check_ethernet=not test_camera)
    heartbeat.publish("starting")
    status = {
        "request_id": request["request_id"], "session": str(session),
        "recorder": "pavewatch-collection-v2", "capture_type": "camera-diagnostic" if test_camera else "field",
        "started_at": control.now(), "status": "starting", "packets": 0, "frames": 0,
    }
    control.atomic_json(control.STATE, status)

    def started():
        status["status"] = "recording"
        control.atomic_json(control.STATE, status)

    flags = [
        "--label", request["label"], "--out", str(session.parent),
        "--seconds", str(request["seconds"]), "--profile", request["profile"],
        "--listen", control.PI_ETH_IP, "--lidar-source", control.IP, "--port", str(control.PORT),
        "--min-free-mib", "1024", "--gain", str(request["gain"]), "--note", request["note"],
    ]
    if test_camera:
        flags += ["--simulate-lidar"]
    if not request["allow_unsynced"]:
        flags += ["--require-lidar-realtime"]
    if request["auto_exposure"]:
        flags += ["--auto-exposure"]
    else:
        flags += ["--exposure-us", str(request["exposure_us"])]
    for name in ("fps", "lens_position", "calibration_id", "calibration_file", "context_file", "pose_file",
                 "lidar_profile_file", "imu_port"):
        if request.get(name) is not None:
            flags += ["--" + name.replace("_", "-"), str(request[name])]
    try:
        if not test_camera:
            control.assert_sensor_link()
        if request.get("storage_device") is not None and session.parent.stat().st_dev != request["storage_device"]:
            raise RuntimeError("the selected storage filesystem changed before recording")
        release_id = Path("/opt/pavewatch-recorder/.git/pavewatch-active").read_text().strip()
        result = main(flags, run_path=session, on_recording=started,
                      sensor_control=None if test_camera else Scanner(control, request["request_id"]),
                      release_id=release_id, heartbeat=heartbeat)
    except (Exception, SystemExit) as exc:
        status["error"] = str(exc)
        result = 1
    manifest = control.read_json(session / "manifest.json")
    workers = manifest.get("workers", {})
    status.update(
        status="completed" if result == 0 else "stopped" if result in (130, 143) else "failed",
        stopped_at=control.now(),
        packets=workers.get("lidar", {}).get("compact_valid_packets", 0),
        frames=workers.get("camera", {}).get("frames_saved", 0),
        quality_flags=manifest.get("quality_flags", []),
        cleanup_errors=manifest.get("sensor_cleanup_errors", []),
    )
    if manifest.get("pose_attachment_error"):
        status["quality_flags"].append("pose_attachment_failed")
    if result:
        status["error"] = (manifest.get("supervisor_error") or manifest.get("stop_reason")
                           or status.get("error") or "no capture manifest created")
        details = [f"{name}: {worker['error']}" for name, worker in workers.items() if worker.get("error")]
        if details:
            status["error"] += " (" + ", ".join(details) + ")"
    control.atomic_json(control.STATE, status)
    heartbeat.publish_terminal(status)
    control.log(f"Combined recorder {status['status']}: {session}; {status['frames']} camera frames, "
                f"{status['packets']} Compact packets; {status.get('error', 'elapsed')}.")
    # A requested graceful stop finalized the data, so systemd can stay inactive.
    return 0 if result in (0, 130, 143) and not status["cleanup_errors"] else 1
