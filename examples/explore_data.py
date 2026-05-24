"""Quick exploration script to understand the recording data.

Usage:
    python examples/explore_data.py data/recording_01/
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.loader import load_recording


def main():
    if len(sys.argv) < 2:
        print("Usage: python examples/explore_data.py <recording_dir>")
        sys.exit(1)

    recording_dir = sys.argv[1]
    print(f"Loading recording from: {recording_dir}\n")

    data = load_recording(recording_dir)

    # Metadata
    meta = data["metadata"]
    print(f"Game: {meta['game']}")
    print(f"Duration: {meta['duration_seconds']}s ({meta['duration_seconds'] / 60:.1f} min)")
    print(f"Resolution: {meta['resolution']} @ {meta['fps']} FPS")
    print()

    # Input log summary
    summary = data["input_summary"]
    print(f"Total input events: {summary['total_events']}")
    print(f"Events per minute: {summary['events_per_minute']}")
    print(f"Bucket size: {summary['bucket_size_seconds']}s")
    print(f"Inactivity gaps: {len(summary['inactivity_gaps'])}")
    print()

    print("Event types:")
    for tc in summary["event_type_counts"][:8]:
        print(f"  {tc['type']}: {tc['count']}")
    print()

    # Activity timeline (first 20 buckets)
    print("Activity over time (first 20 buckets):")
    for bucket in summary["activity_over_time"][:20]:
        bar = "#" * min(bucket["events"], 50)
        gap = f" [gap: {bucket['gap_seconds']}s]" if bucket.get("gap_seconds") else ""
        print(f"  {bucket['label']:>6s} | {bucket['events']:>4d} {bar}{gap}")
    print(f"  ... ({len(summary['activity_over_time'])} total buckets)")
    print()

    # Camera telemetry
    cam = data["camera_telemetry"]
    stats = cam["stats"]
    print(f"Camera frames: {stats['frame_count']}")
    print(f"Avg camera FPS: {stats['avg_fps']}")
    print(f"Distance traveled: {stats['distance_traveled']}")
    print(f"FOV: {stats['fov']}")
    print(f"Map: {stats['map_name']}")
    print(f"Axis convention: {stats['axis_convention']}")
    print()

    # Game mechanics
    print(f"Game mechanics ({len(data['mechanics'])}):")
    for m in data["mechanics"]:
        print(f"  [{m.category}] {m.display_name} ({m.mechanic_id})")
    print()

    # Raw events sample
    if summary["raw_events"]:
        print("Sample raw events (first 5):")
        for evt in summary["raw_events"][:5]:
            print(f"  {json.dumps(evt)}")
    print()

    if summary["camera_events"]:
        print("Sample camera events (first 3):")
        for evt in summary["camera_events"][:3]:
            print(f"  {json.dumps(evt)}")


if __name__ == "__main__":
    main()
