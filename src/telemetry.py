"""Camera telemetry parser.

Extracts camera position/rotation data from input logs and computes
movement statistics: distance traveled, average FPS, axis convention.
"""

import math
import statistics
from pathlib import Path

from .parser import load_msgpack, _normalize_dict


_SECONDS_THRESHOLD = 50_000
MAX_CAMERA_EVENTS = 3000


def detect_axis_convention(events: list[dict]) -> str:
    """Determine the yaw->direction convention by correlating velocity with facing.

    Returns "compass" (yaw=0=North) or "ue" (yaw=0=East, Unreal Engine default).
    Defaults to "compass" if insufficient velocity data.
    """
    cam = [
        e
        for e in events
        if e.get("type") == "camera"
        and e.get("vx") is not None
        and e.get("vy") is not None
    ]
    if len(cam) < 10:
        return "compass"

    cam.sort(key=lambda e: e["t"])

    def _angle_diff(a: float, b: float) -> float:
        return abs(((a - b + math.pi) % (2 * math.pi)) - math.pi)

    errors_compass: list[float] = []
    errors_ue: list[float] = []

    for i in range(1, len(cam)):
        e0, e1 = cam[i - 1], cam[i]
        vx, vy = float(e0["vx"]), float(e0["vy"])
        speed = math.sqrt(vx * vx + vy * vy)
        if speed < 50:
            continue
        dyaw = abs(float(e1["yaw"]) - float(e0["yaw"]))
        if dyaw > 5:
            continue

        yaw_rad = float(e0["yaw"]) * math.pi / 180
        move_angle = math.atan2(vy, vx)
        compass_angle = math.atan2(-math.cos(yaw_rad), math.sin(yaw_rad))
        ue_angle = math.atan2(-math.sin(yaw_rad), math.cos(yaw_rad))
        errors_compass.append(_angle_diff(move_angle, compass_angle))
        errors_ue.append(_angle_diff(move_angle, ue_angle))

    if not errors_compass:
        return "compass"
    return "ue" if statistics.mean(errors_ue) < statistics.mean(errors_compass) else "compass"


def compute_camera_stats(
    events: list[dict], duration_s: float, game_name: str | None = None
) -> dict:
    """Compute camera telemetry statistics from a list of camera events.

    Returns frame_count, avg_fps, distance_traveled, fov, map_name,
    and axis_convention.
    """
    cam = sorted(
        [
            e
            for e in events
            if e.get("type") == "camera"
            and not (e.get("px") == 0 and e.get("py") == 0 and e.get("pz") == 0)
        ],
        key=lambda e: e["t"],
    )
    distance = 0.0
    for i in range(1, len(cam)):
        dx = cam[i]["px"] - cam[i - 1]["px"]
        dy = cam[i]["py"] - cam[i - 1]["py"]
        dz = cam[i]["pz"] - cam[i - 1]["pz"]
        distance += math.sqrt(dx * dx + dy * dy + dz * dz)

    convention = detect_axis_convention(cam)

    return {
        "frame_count": len(cam),
        "avg_fps": round(len(cam) / duration_s, 1) if duration_s > 0 else 0.0,
        "distance_traveled": round(distance, 0),
        "fov": cam[0].get("fov") if cam else None,
        "map_name": next((e["map"] for e in cam if e.get("map")), None),
        "axis_convention": convention,
    }


def parse_camera_telemetry(decoded: list) -> dict:
    """Extract camera telemetry from decoded msgpack data.

    Returns a dict with:
    - events: list of normalized camera events (0-based milliseconds)
    - stats: dict with frame_count, avg_fps, distance_traveled, fov, etc.
    """
    header_meta: dict = {}
    events: list[dict] = []
    for item in decoded:
        if isinstance(item, dict):
            item = _normalize_dict(item)
        if isinstance(item, dict) and item.get("__meta__"):
            header_meta = item
            continue
        if isinstance(item, list):
            for evt in item:
                if isinstance(evt, dict):
                    evt = _normalize_dict(evt)
                if isinstance(evt, dict) and "t" in evt and "type" in evt:
                    events.append(evt)
        elif isinstance(item, dict) and "t" in item and "type" in item:
            events.append(item)

    if not events:
        return {
            "events": [],
            "stats": {
                "frame_count": 0,
                "avg_fps": 0.0,
                "distance_traveled": 0.0,
                "fov": None,
                "map_name": None,
                "axis_convention": "compass",
            },
        }

    events.sort(key=lambda e: e["t"])
    first_ts = events[0]["t"]
    last_ts = events[-1]["t"]

    timestamp_unit = header_meta.get("timestamp_unit")
    if timestamp_unit == "microseconds":
        ms_factor = 1000
    else:
        ts_range = last_ts - first_ts
        ms_factor = 1000 if ts_range < _SECONDS_THRESHOLD else 1

    obs_sync_evt = next((e for e in events if e.get("type") == "obs_sync"), None)
    obs_start_offset_us: int | None = (
        obs_sync_evt.get("obs_start_offset_us") if obs_sync_evt else None
    )
    if obs_start_offset_us is not None:
        obs_start_t: float = (
            obs_start_offset_us / 1_000_000
            if ms_factor == 1000
            else obs_start_offset_us / 1_000
        )
    else:
        obs_start_t = first_ts

    recording_span = last_ts - obs_start_t
    duration_s = recording_span if ms_factor == 1000 else recording_span / 1000

    game_name: str | None = header_meta.get("game_name")

    recording_events = (
        [e for e in events if e["t"] >= obs_start_t]
        if obs_start_t > first_ts
        else events
    )

    stats = compute_camera_stats(recording_events, duration_s, game_name=game_name)

    cam_events = [
        e
        for e in recording_events
        if e.get("type") == "camera"
        and not (e.get("px") == 0 and e.get("py") == 0 and e.get("pz") == 0)
    ]
    cam_events.sort(key=lambda e: e["t"])

    normalized = []
    for evt in cam_events:
        t_ms = int((evt["t"] - obs_start_t) * ms_factor)
        normalized.append(
            {
                "t": t_ms,
                "type": "camera",
                "px": float(evt.get("px", 0)),
                "py": float(evt.get("py", 0)),
                "pz": float(evt.get("pz", 0)),
                "yaw": float(evt.get("yaw", 0)),
                "pitch": float(evt.get("pitch", 0)),
                "roll": float(evt.get("roll", 0)),
                "fov": float(evt["fov"]) if evt.get("fov") is not None else None,
            }
        )

    if len(normalized) > MAX_CAMERA_EVENTS:
        step = (len(normalized) - 1) / (MAX_CAMERA_EVENTS - 1)
        normalized = [
            normalized[min(int(i * step), len(normalized) - 1)]
            for i in range(MAX_CAMERA_EVENTS)
        ]

    return {"events": normalized, "stats": stats}


def parse_camera_telemetry_file(path: str | Path) -> dict:
    """Load a msgpack input log file and extract camera telemetry."""
    decoded = load_msgpack(path)
    return parse_camera_telemetry(decoded)
