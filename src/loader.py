"""Data loader for interview recordings.

Loads all files for a recording directory and returns parsed data.
"""

import json
from pathlib import Path

from .parser import parse_input_log_file
from .schemas import GameMechanic
from .telemetry import parse_camera_telemetry_file


def load_recording(recording_dir: str | Path) -> dict:
    """Load all data for a recording directory.

    Expects the directory to contain:
    - input_log.msgpack (required)
    - metadata.json (required)
    - mechanics.json (required)

    Returns a dict with parsed data ready for analysis.
    """
    recording_dir = Path(recording_dir)

    metadata_path = recording_dir / "metadata.json"
    metadata = json.loads(metadata_path.read_text())

    input_log_path = recording_dir / "input_log.msgpack"
    input_summary = parse_input_log_file(input_log_path)

    camera_telemetry = parse_camera_telemetry_file(input_log_path)

    mechanics_path = recording_dir / "mechanics.json"
    mechanics_raw = json.loads(mechanics_path.read_text())
    mechanics = [GameMechanic(**m) for m in mechanics_raw]

    return {
        "metadata": metadata,
        "input_summary": input_summary,
        "camera_telemetry": camera_telemetry,
        "mechanics": mechanics,
    }
