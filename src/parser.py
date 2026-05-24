"""Input log parser.

Reads msgpack input log files and produces activity summary statistics:
event counts, activity-over-time buckets, and inactivity gap detection.
"""

import math
from collections import Counter
from pathlib import Path

import msgpack


MAX_ACTIVITY_BUCKETS = 500
INACTIVITY_THRESHOLD_SECONDS = 5


def load_msgpack(path: str | Path) -> list:
    """Load a msgpack input log file and return decoded values.

    Input log files may contain multiple concatenated msgpack values
    (streaming append pattern), so we use Unpacker to iterate all values.
    """
    raw_bytes = Path(path).read_bytes()
    try:
        unpacker = msgpack.Unpacker(raw=False, max_buffer_size=0)
        unpacker.feed(raw_bytes)
        return list(unpacker)
    except (UnicodeDecodeError, msgpack.exceptions.UnpackValueError):
        unpacker = msgpack.Unpacker(raw=True, max_buffer_size=0)
        unpacker.feed(raw_bytes)
        return list(unpacker)


def _normalize_dict(d: dict) -> dict:
    """Normalize a dict that may have bytes keys/values from raw msgpack decoding."""
    normalized = {}
    for k, v in d.items():
        key = k.decode("utf-8", errors="replace") if isinstance(k, bytes) else k
        if isinstance(v, bytes):
            v = v.decode("utf-8", errors="replace")
        elif isinstance(v, dict):
            v = _normalize_dict(v)
        normalized[key] = v
    return normalized


def _detect_inactivity_gaps(
    events: list[dict],
    first_ts: float,
    threshold_seconds: int,
) -> list[dict]:
    """Detect periods of inactivity (gaps between events exceeding threshold)."""
    gaps = []
    for i in range(1, len(events)):
        gap_seconds = events[i]["t"] - events[i - 1]["t"]
        if gap_seconds >= threshold_seconds:
            gaps.append(
                {
                    "start_seconds": events[i - 1]["t"] - first_ts,
                    "end_seconds": events[i]["t"] - first_ts,
                }
            )
    return gaps


def _extract_system_metadata(header: dict) -> dict:
    """Extract system metadata from a msgpack input log header record."""
    obs_raw = header.get("obs", {})
    obs = {
        "output_width": obs_raw.get("output_width"),
        "output_height": obs_raw.get("output_height"),
        "fps_numerator": obs_raw.get("fps_numerator"),
        "fps_denominator": obs_raw.get("fps_denominator"),
        "obs_version": obs_raw.get("obs_version"),
    }

    device_hw = header.get("device", {}).get("hardware", {})
    hardware = {
        "cpu_model": device_hw.get("cpu_model"),
        "cpu_cores_physical": device_hw.get("cpu_cores_physical"),
        "ram_total_bytes": device_hw.get("ram_total_bytes"),
        "os_version": device_hw.get("os_version"),
    }
    return {
        "obs": obs,
        "hardware": hardware,
        "game_name": header.get("game_name"),
        "platform": header.get("platform"),
        "started_at": header.get("started_at"),
        "recorder_version": header.get("version"),
    }


def parse_input_log(raw: list) -> dict:
    """Parse decoded msgpack input log data into summary statistics.

    Returns a dict with:
    - total_events: int
    - duration_seconds: int
    - events_per_minute: int
    - bucket_size_seconds: int
    - event_type_counts: list of {type, count} sorted by count DESC
    - activity_over_time: list of {label, events, gap_seconds?} buckets
    - inactivity_gaps: list of {start_seconds, end_seconds}
    - system_metadata: dict or None
    - raw_events: list of all parsed events (for downstream analysis)
    """
    excluded_types = {"obs_sync", "heartbeat", "frame_pts", "camera"}
    events: list[dict] = []
    camera_events: list[dict] = []
    system_metadata = None

    for item in raw:
        if isinstance(item, dict):
            item = _normalize_dict(item)
        if isinstance(item, dict) and item.get("__meta__"):
            system_metadata = _extract_system_metadata(item)
            continue
        if isinstance(item, list):
            for evt in item:
                if isinstance(evt, dict):
                    evt = _normalize_dict(evt)
                if isinstance(evt, dict) and "t" in evt and "type" in evt:
                    if evt["type"] == "camera":
                        camera_events.append(evt)
                    elif evt["type"] not in excluded_types:
                        events.append(evt)
        elif isinstance(item, dict) and "t" in item and "type" in item:
            if item["type"] == "camera":
                camera_events.append(item)
            elif item["type"] not in excluded_types:
                events.append(item)

    if not events:
        return {
            "total_events": 0,
            "duration_seconds": 0,
            "events_per_minute": 0,
            "bucket_size_seconds": 1,
            "event_type_counts": [],
            "activity_over_time": [],
            "inactivity_gaps": [],
            "system_metadata": system_metadata,
            "raw_events": [],
            "camera_events": [],
        }

    events.sort(key=lambda e: e["t"])
    camera_events.sort(key=lambda e: e["t"])

    first_ts = events[0]["t"]
    last_ts = events[-1]["t"]
    duration_raw = last_ts - first_ts
    duration_seconds = round(duration_raw)
    duration_minutes = duration_seconds / 60
    events_per_minute = (
        round(len(events) / duration_minutes) if duration_minutes > 0 else len(events)
    )

    type_counts = Counter(evt["type"] for evt in events)
    event_type_counts = sorted(
        [{"type": t, "count": c} for t, c in type_counts.items()],
        key=lambda x: x["count"],
        reverse=True,
    )

    bucket_size = max(1, math.ceil(duration_seconds / MAX_ACTIVITY_BUCKETS))
    bucket_count = max(1, math.ceil(duration_seconds / bucket_size))
    buckets = []
    for i in range(bucket_count):
        start_sec = i * bucket_size
        mins = start_sec // 60
        secs = start_sec % 60
        buckets.append({"label": f"{mins}:{secs:02d}", "events": 0})

    for evt in events:
        offset_sec = evt["t"] - first_ts
        bucket_idx = min(int(offset_sec // bucket_size), len(buckets) - 1)
        buckets[bucket_idx]["events"] += 1

    inactivity_gaps = _detect_inactivity_gaps(events, first_ts, INACTIVITY_THRESHOLD_SECONDS)

    for gap in inactivity_gaps:
        first_bi = max(0, int(gap["start_seconds"] // bucket_size))
        last_bi = min(len(buckets) - 1, int(gap["end_seconds"] // bucket_size))
        for bi in range(first_bi, last_bi + 1):
            b_start = bi * bucket_size
            b_end = b_start + bucket_size
            overlap = max(
                0.0, min(gap["end_seconds"], b_end) - max(gap["start_seconds"], b_start)
            )
            buckets[bi]["gap_seconds"] = round(
                buckets[bi].get("gap_seconds", 0.0) + overlap, 2
            )

    return {
        "total_events": len(events),
        "duration_seconds": duration_seconds,
        "events_per_minute": events_per_minute,
        "bucket_size_seconds": bucket_size,
        "event_type_counts": event_type_counts,
        "activity_over_time": buckets,
        "inactivity_gaps": inactivity_gaps,
        "system_metadata": system_metadata,
        "raw_events": events,
        "camera_events": camera_events,
    }


def parse_input_log_file(path: str | Path) -> dict:
    """Load and parse a msgpack input log file. Convenience wrapper."""
    decoded = load_msgpack(path)
    return parse_input_log(decoded)
