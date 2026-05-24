# Origin Lab — Interview Project

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Download Data

Download the sample recordings (~7 hours of gameplay across 3 games):

```bash
# Download input logs only (required, ~100 MB)
python download_data.py --no-video

# Download everything including video files (~20 GB)
python download_data.py
```

Download links expire after 7 days. Contact us if they have expired.

## Explore the Data

```bash
python examples/explore_data.py data/recording_01/
```

This prints a summary of the recording: event counts, activity timeline, camera stats, and game mechanics.

## Assignment

See **[ASSIGNMENT.md](ASSIGNMENT.md)** for the full project brief.

## Sample Recordings

| Recording | Game | Genre | Duration |
|-----------|------|-------|----------|
| recording_01 | Astor: Blade of the Monolith | Action RPG | ~181 min |
| recording_02 | Empyrion - Galactic Survival | Survival / Sandbox | ~124 min |
| recording_03 | The Witch of Fern Island | Life Sim / RPG | ~143 min |

## Project Structure

```
download_data.py   # Downloads sample data from presigned URLs
src/
  parser.py        # Input log parser (msgpack -> activity summary)
  telemetry.py     # Camera telemetry parser (position, rotation, movement stats)
  schemas.py       # Data models: GameMechanic, ActivityPhase, Highlight
  loader.py        # Loads all data for a recording directory
data/
  recording_01/    # Astor: Blade of the Monolith (Action RPG)
  recording_02/    # Empyrion - Galactic Survival (Survival / Sandbox)
  recording_03/    # The Witch of Fern Island (Life Sim / RPG)
examples/
  explore_data.py  # Quick data exploration script
```

## Data Format

Each recording directory contains:

- **`input_log.msgpack`** — Timestamped keyboard/mouse events in msgpack format. The parser extracts event counts, activity-over-time buckets, and inactivity gaps.
- **`metadata.json`** — Game name, duration, resolution, FPS.
- **`mechanics.json`** — List of known game mechanics for this game (mechanic_id, display_name, category).

Camera telemetry (position, rotation, FOV) is embedded in the input log and extracted automatically by the telemetry parser.

Video files (screen.mp4) are optional — useful for visual context but not needed by the pipeline.
