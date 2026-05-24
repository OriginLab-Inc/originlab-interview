"""Download sample recording data from presigned URLs.

Run this once after cloning the repo:
    python download_data.py

Links expire 7 days after generation (May 31, 2026).
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
            "input_log.msgpack": "https://originlab-collections.s3.us-east-1.amazonaws.com/recordings/04222cdd-6912-497d-9bc9-002981c888c7/segment-1/input_log.msgpack?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260524%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260524T204648Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=674b46d8d04f04622ac4c27a8d2de6443d81247cff809d35e37f3a4f7ece7046",
            "screen.mp4": "https://originlab-collections.s3.us-east-1.amazonaws.com/recordings/04222cdd-6912-497d-9bc9-002981c888c7/segment-1/screen.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260524%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260524T204648Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=133c7ab06d012ac6be0873e6f3f8a8f32a7b8167418a9ea25d805d6d623d9edc",
        },
    },
    "recording_02": {
        "game": "Empyrion - Galactic Survival",
        "genre": "Survival / Sandbox",
        "duration_seconds": 7464,
        "resolution": "1920x1080",
        "fps": 60,
        "files": {
            "input_log.msgpack": "https://originlab-collections.s3.us-east-1.amazonaws.com/recordings/bd43b50c-de99-49f8-aa04-3cdac79a97a5/segment-1/input_log.msgpack?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260524%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260524T204649Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=11a0ed71ee877c14756a2b24123748c119ab7cb4fb06c88223363e887f6f2a74",
            "screen.mp4": "https://originlab-collections.s3.us-east-1.amazonaws.com/recordings/bd43b50c-de99-49f8-aa04-3cdac79a97a5/segment-1/screen.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260524%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260524T204649Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=b934fbfc261d94eea154d7ea7ea8b0ab5c7e9dc12ceb25f822b127f585d27108",
        },
    },
    "recording_03": {
        "game": "SnowRunner",
        "genre": "Driving / Simulation",
        "duration_seconds": 6048,
        "resolution": "1920x1080",
        "fps": 60,
        "files": {
            "input_log.msgpack": "https://originlab-collections.s3.us-east-1.amazonaws.com/videogame/snowrunner/samples/showcase_deepmind.msgpack?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260524%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260524T204649Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=05dc58b9fdd605cb5b6b9558ea35f98f5031b3ca46be0d80d818dae45a46400b",
            "screen.mp4": "https://originlab-collections.s3.us-east-1.amazonaws.com/videogame/snowrunner/samples/showcase_deepmind.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDVFRA5HZOJLNORJ%2F20260524%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260524T204649Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=5d631273639d435fa479ebe498aead7c2570a13d16710d43556879dcc5124246",
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
