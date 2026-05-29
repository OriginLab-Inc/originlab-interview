"""Download sample recording data from presigned URLs.

Run this once after cloning the repo:
    python download_data.py

Links expire 7 days after generation (June 5, 2026).
If expired, contact us for fresh links.
"""

import sys
import urllib.request
from pathlib import Path

RECORDINGS = {
    "recording_01": {
        "game": "Astor: Blade of the Monolith",
        "genre": "Action RPG",
        "duration_seconds": 10866,
        "resolution": "1920x1080",
        "fps": 60,
        "files": {
            "input_log.msgpack": "https://originlab-assets.s3.amazonaws.com/recordings/04222cdd-6912-497d-9bc9-002981c888c7/segment-1/input_log.msgpack?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260529%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260529T183946Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=0da1f5284e8f8744cdaf498732abe1f2171e0444873172e70dcd3b5f241bb849",
            "screen.mp4": "https://originlab-assets.s3.amazonaws.com/recordings/04222cdd-6912-497d-9bc9-002981c888c7/segment-1/screen.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260529%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260529T183946Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=2e240bc37ff0861d80f3315c8e052edf630c75e70d5428f5a57785b7dc9b7c88",
        },
    },
    "recording_02": {
        "game": "Empyrion - Galactic Survival",
        "genre": "Survival / Sandbox",
        "duration_seconds": 7464,
        "resolution": "1920x1080",
        "fps": 60,
        "files": {
            "input_log.msgpack": "https://originlab-assets.s3.amazonaws.com/recordings/bd43b50c-de99-49f8-aa04-3cdac79a97a5/segment-1/input_log.msgpack?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260529%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260529T183946Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=fe30712810b1c86b597e4e1122c73c50ffe693379c485d5724f1cab369941b3f",
            "screen.mp4": "https://originlab-assets.s3.amazonaws.com/recordings/bd43b50c-de99-49f8-aa04-3cdac79a97a5/segment-1/screen.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260529%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260529T183946Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=72856d14aa4c0eac8389cba0de7a0ef6b103404fbf86d8ac1eedf35d6e0ec7f3",
        },
    },
    "recording_03": {
        "game": "The Witch of Fern Island",
        "genre": "Life Sim / RPG",
        "duration_seconds": 8568,
        "resolution": "1920x1080",
        "fps": 60,
        "files": {
            "input_log.msgpack": "https://originlab-assets.s3.amazonaws.com/recordings/7c80264a-043b-4131-9b99-cb2fc28e3cfb/segment-1/input_log.msgpack?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260529%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260529T183946Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=8d9f9a06d1a1fb280a9de5cbce9c95c312f0e17d0a04590c39bcbde651627b46",
            "screen.mp4": "https://originlab-assets.s3.amazonaws.com/recordings/7c80264a-043b-4131-9b99-cb2fc28e3cfb/segment-1/screen.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260529%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260529T183946Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=0110b66c4ce5279fd7b93adaef69d05949fc4944b5b11393a80dfcf1ce851804",
        },
    },
}


def download_file(url: str, dest: Path) -> None:
    if dest.exists():
        print(f"  Already exists: {dest.name}")
        return
    print(f"  Downloading {dest.name}...", end="", flush=True)
    try:
        urllib.request.urlretrieve(url, dest)
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f" {size_mb:.1f} MB")
    except Exception as e:
        print(f" FAILED: {e}")
        if dest.exists():
            dest.unlink()


def main():
    import json

    data_dir = Path(__file__).parent / "data"
    skip_video = "--no-video" in sys.argv

    for name, rec in RECORDINGS.items():
        rec_dir = data_dir / name
        rec_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{rec['game']} ({rec['genre']}) -> {name}/")

        # Write metadata.json
        metadata = {
            "game": rec["game"],
            "genre": rec["genre"],
            "duration_seconds": rec["duration_seconds"],
            "segment_count": 1,
            "resolution": rec["resolution"],
            "fps": rec["fps"],
        }
        (rec_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
        print(f"  Wrote metadata.json")

        # Download files
        for filename, url in rec["files"].items():
            if skip_video and filename.endswith(".mp4"):
                print(f"  Skipping {filename} (--no-video)")
                continue
            download_file(url, rec_dir / filename)

    print("\nDone! Run 'python examples/explore_data.py data/recording_01/' to verify.")
    if skip_video:
        print("(Videos skipped. Run without --no-video to download them.)")


if __name__ == "__main__":
    main()
