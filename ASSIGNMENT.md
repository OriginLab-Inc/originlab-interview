# Origin Lab — Interview Project

## Segment Activity Detection & Highlighting

| | |
|---|---|
| **Duration** | 4-5 days |
| **Compensation** | $300 (paid regardless of outcome) |
| **Language** | Python 3.11+ |
| **Deliverable** | GitHub repo or zip |

---

## Context

Origin Lab captures gameplay recordings from various games. Each recording session consists of one or more **segments** (pause/resume takes). Alongside the video, we capture:

- **Input logs** — every keyboard press, mouse movement, and click, timestamped in microseconds
- **Camera telemetry** — the in-game camera position, rotation, and field of view, captured every frame

We need a system that automatically analyzes these signals to **detect activity patterns** and **highlight interesting moments** in a recording — segments where the player is in combat, completing objectives, encountering rare events, or demonstrating specific game mechanics.

---

## What You Receive

### 1. Sample Code Package (`originlab-interview/`)

A standalone Python package with:

```
originlab-interview/
  README.md                  # Setup instructions
  requirements.txt           # msgpack, pydantic
  src/
    parser.py                # Input log parser (reads msgpack, outputs activity summary)
    telemetry.py             # Camera telemetry parser (reads JSONL, outputs position/movement stats)
    schemas.py               # Data models: GameMechanic, VideoSegment, Highlight
    loader.py                # Helper to load all data for a recording
  data/
    recording_01/
      input_log.msgpack      # Raw input events
      camera_telemetry.jsonl # Camera frames
      metadata.json          # Game name, duration, segment info
      mechanics.json         # Game mechanics definitions for this game
    recording_02/
      ...
    recording_03/
      ...
  videos/
    README.md                # Links to download video files (2-3 hours total)
```

### 2. Video Files

2-3 hours of gameplay footage across multiple games, downloadable via provided links. Each recording has a matching `input_log.msgpack` and `camera_telemetry.jsonl` in the data directory.

### 3. Game Mechanics Definitions

For each game in the sample data, a `mechanics.json` file listing the known game mechanics:

```json
[
  {
    "mechanic_id": "resource_gathering",
    "display_name": "Resource Gathering",
    "category": "survival",
    "reasoning": "Player collects wood, stone, and other materials from the environment"
  },
  {
    "mechanic_id": "base_building",
    "display_name": "Base Building",
    "category": "construction",
    "reasoning": "Player places structures and builds shelters"
  }
]
```

---

## The Assignment

Build a pipeline that takes a recording's input log, camera telemetry, and game mechanics definitions as input, and outputs **a list of highlighted segments** identifying the most interesting moments.

### Part 1: Activity Classification (Days 1-2)

Analyze the input log and camera telemetry to classify each moment in the recording into activity phases.

**Input:** `input_log.msgpack` + `camera_telemetry.jsonl`

**Output:** A timeline of classified activity phases:

```json
[
  {"start": 0.0, "end": 12.5, "phase": "idle", "confidence": 0.95},
  {"start": 12.5, "end": 45.0, "phase": "exploration", "confidence": 0.82},
  {"start": 45.0, "end": 78.3, "phase": "high_activity", "confidence": 0.91},
  {"start": 78.3, "end": 90.0, "phase": "menu", "confidence": 0.88}
]
```

**Expected phases** (at minimum):
- `idle` — no meaningful input for extended periods
- `exploration` — steady movement, low input intensity
- `high_activity` — rapid inputs, fast camera movement (combat, action sequences)
- `menu` — repetitive clicks, no camera movement (UI interaction)

You may add more phases if you identify distinct patterns in the data.

**Signals to consider:**
- Input event frequency and type distribution (keys vs mouse vs clicks)
- Camera velocity and acceleration (fast rotation = action, slow pan = exploration)
- Camera position changes (stationary = idle/menu, moving = exploration/action)
- Input diversity (many different keys = gameplay, same key repeated = menu navigation)
- Gaps between events (long gaps = idle)

### Part 2: Highlight Detection (Days 3-4)

Use the activity classification and game mechanics definitions to identify the most interesting moments worth highlighting.

**Input:** Activity phases + `mechanics.json` + telemetry data

**Output:** A list of highlights:

```json
[
  {
    "start": 45.0,
    "end": 78.3,
    "label": "Intense combat sequence",
    "confidence": 0.91,
    "mechanics_matched": ["combat", "weapon_switching"],
    "reason": "High input rate (180 events/min), rapid camera rotation (avg 45 deg/s), multiple weapon key presses detected"
  },
  {
    "start": 120.0,
    "end": 155.0,
    "label": "Resource gathering session",
    "confidence": 0.75,
    "mechanics_matched": ["resource_gathering"],
    "reason": "Repeated interaction key presses near stationary camera positions, consistent with harvesting pattern"
  }
]
```

**What makes a good highlight:**
- High activity segments (action, combat)
- Segments that match known game mechanics
- Transitions between phases (entering/exiting combat)
- Unusual patterns (sudden spike after long idle = something happened)
- Longer sustained activity sequences over brief spikes

### Part 3: Documentation & Testing (Day 5)

- Write a brief technical document (1-2 pages) explaining:
  - Your classification approach and why you chose it
  - How you match activity patterns to game mechanics
  - What would you improve with more time or data
  - How this would scale to thousands of recordings
- Add tests for your classifier and highlight detector
- Make sure the pipeline runs end-to-end on all provided recordings

---

## Deliverables

Submit a GitHub repository (or zip) containing:

1. **Working pipeline** that processes any recording from the sample data and outputs highlights
2. **`classify.py`** — runs activity classification on a recording directory
3. **`highlight.py`** — runs highlight detection and outputs results
4. **`results/`** — pre-computed outputs for all sample recordings
5. **`APPROACH.md`** — technical writeup (1-2 pages)
6. **Tests** — at least basic coverage for the classifier and detector

### How to Run

Your submission should work with:

```bash
pip install -r requirements.txt
python classify.py data/recording_01/
python highlight.py data/recording_01/
```

---

## Evaluation Criteria

| Criteria | Weight | What We Look For |
|----------|--------|-----------------|
| **Algorithm Quality** | 30% | Does the classifier produce meaningful results? Are the highlights actually interesting? |
| **Code Quality** | 25% | Clean, readable, well-structured code. Good naming. No unnecessary complexity. |
| **Technical Judgment** | 20% | Smart use of signals. Reasonable thresholds. Good tradeoffs between precision and recall. |
| **Documentation** | 15% | Clear explanation of approach. Honest about limitations. Thoughtful about scaling. |
| **Testing** | 10% | Tests that verify behavior, not just coverage. Edge cases considered. |

### What We Value

- **Pragmatic solutions** over perfect ones. A rule-based classifier that works well beats a half-finished ML pipeline.
- **Clear thinking** over clever code. We want to understand your reasoning.
- **Honest assessment** of what works and what doesn't. Tell us where your approach breaks down.
- **Production awareness**. Think about: What if there are 10,000 recordings? What if a new game has completely different mechanics?

### What We Don't Want

- Over-engineered solutions with unnecessary abstractions
- Copy-pasted ML boilerplate without understanding
- Perfect code with no working output
- Unsubstantiated claims about accuracy

---

## Timeline

| Day | Focus | Expected Output |
|-----|-------|----------------|
| 1 | Explore the data. Understand the signals. | Notes on patterns you observe. |
| 2 | Build the activity classifier. | Working classifier with initial results. |
| 3 | Build the highlight detector. Wire up mechanics matching. | Working highlight pipeline. |
| 4 | Tune, test, handle edge cases. | Refined output, tests passing. |
| 5 | Write documentation. Final polish. | Complete submission. |

---

## Questions?

If anything is unclear about the data format, the assignment scope, or the expected output, reach out. Asking good questions is a positive signal, not a negative one.
