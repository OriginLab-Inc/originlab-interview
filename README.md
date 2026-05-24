# Origin Lab — Interview Project

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Explore the Data

```bash
python examples/explore_data.py data/recording_01/
```

This will print a summary of the recording: event counts, activity timeline, camera stats, and game mechanics.

## Assignment

See **[ASSIGNMENT.md](ASSIGNMENT.md)** for the full project brief.

## Project Structure

```
src/
  parser.py        # Input log parser (msgpack -> activity summary)
  telemetry.py     # Camera telemetry parser (position, rotation, movement stats)
  schemas.py       # Data models: GameMechanic, ActivityPhase, Highlight
  loader.py        # Loads all data for a recording directory
data/
  recording_01/    # ~45 min gameplay recording
  recording_02/    # ~45 min gameplay recording
  recording_03/    # ~45 min gameplay recording
videos/
  README.md        # Links to download video files
examples/
  explore_data.py  # Quick data exploration script
```

## Data Format

Each recording directory contains:

- **`input_log.msgpack`** — Timestamped keyboard/mouse events in msgpack format. The parser extracts event counts, activity-over-time buckets, and inactivity gaps.
- **`metadata.json`** — Game name, duration, resolution, FPS.
- **`mechanics.json`** — List of known game mechanics for this game (mechanic_id, display_name, category).

Camera telemetry (position, rotation, FOV) is embedded in the input log and extracted automatically by the telemetry parser.
