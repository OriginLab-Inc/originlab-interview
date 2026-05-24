# Origin Lab — Interview Project

## Segment Activity Detection & Highlighting

| | |
|---|---|
| **Stack** | Python 3.11+ (backend) / Framework of your choice (frontend) |
| **Deliverable** | GitHub repo or zip |

---

## Context

Origin Lab captures gameplay recordings from various games. Each recording session consists of one or more **segments** (pause/resume takes). Alongside the video, we capture:

- **Input logs** — every keyboard press, mouse movement, and click, timestamped in microseconds
- **Camera telemetry** — the in-game camera position, rotation, and field of view, captured every frame

We need a system that automatically analyzes these signals to **detect activity patterns** and **highlight interesting moments** in a recording — segments where the player is in combat, completing objectives, encountering rare events, or demonstrating specific game mechanics.

---

## What You Receive

### 1. Sample Code Package

A standalone Python package with parsers for our data formats:

- `src/parser.py` — Input log parser (reads msgpack, outputs activity summary with event counts and time buckets)
- `src/telemetry.py` — Camera telemetry parser (reads position, rotation, movement stats from the same msgpack)
- `src/schemas.py` — Data models: `GameMechanic`, `ActivityPhase`, `Highlight`
- `src/loader.py` — Helper to load all data for a recording directory

### 2. Sample Recordings

3 recordings across different game genres (~7 hours total), downloaded via `python download_data.py`:

| Recording | Game | Genre |
|-----------|------|-------|
| recording_01 | Astor: Blade of the Monolith | Action RPG |
| recording_02 | Empyrion - Galactic Survival | Survival / Sandbox |
| recording_03 | SnowRunner | Driving / Simulation |

Each recording includes an input log (msgpack), metadata, and game mechanics definitions.

### 3. Game Mechanics Definitions

For each game, a `mechanics.json` file listing known game mechanics:

```json
[
  {
    "mechanic_id": "resource_gathering",
    "display_name": "Resource Gathering",
    "category": "survival",
    "reasoning": "Player collects wood, stone, and other materials from the environment"
  }
]
```

---

## The Assignment

Build a full-stack application that analyzes gameplay recordings and presents the results in a usable interface.

### Part 1: Activity Classification

Analyze the input log and camera telemetry to classify each moment in the recording into activity phases.

**Input:** `input_log.msgpack` (contains both input events and camera telemetry)

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

### Part 2: Highlight Detection

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
  }
]
```

**What makes a good highlight:**
- High activity segments (action, combat)
- Segments that match known game mechanics
- Transitions between phases (entering/exiting combat)
- Unusual patterns (sudden spike after long idle = something happened)
- Longer sustained activity sequences over brief spikes

### Part 3: User Interface

Build a web interface that lets a user explore the analysis results for any recording. The UI should make the data useful — not just display it.

**Requirements:**
- Load and display results for any of the 3 sample recordings
- Show the activity timeline visually (what phase is happening at each point in time)
- Display detected highlights with their details (label, confidence, matched mechanics)
- Let the user click on a highlight or timeline section to see more detail
- Show the game mechanics for the recording and which ones were detected

**We're evaluating:**
- Can you design an interface that makes complex data understandable?
- Do your layout, interaction, and information hierarchy choices make sense?
- Is it functional and usable, not just a data dump?

Use whatever frontend framework you're comfortable with. We care about the result, not the stack.

### Part 4: Documentation & Testing

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

1. **Working analysis pipeline** that processes any recording from the sample data
2. **Web interface** to explore the results
3. **Pre-computed results** for all 3 sample recordings
4. **`APPROACH.md`** — technical writeup (1-2 pages)
5. **Tests** — at least basic coverage for the classifier and detector
6. **Setup instructions** — we should be able to run your project with minimal steps

---

## Evaluation Criteria

| Criteria | Weight | What We Look For |
|----------|--------|-----------------|
| **Algorithm Quality** | 25% | Does the classifier produce meaningful results? Are the highlights actually interesting? |
| **UI / Product Sense** | 25% | Is the interface usable and well-designed? Does it make the data understandable? Good information hierarchy? |
| **Code Quality** | 20% | Clean, readable, well-structured code across both frontend and backend. |
| **Technical Judgment** | 15% | Smart use of signals. Reasonable thresholds. Good tradeoffs. |
| **Documentation & Testing** | 15% | Clear explanation of approach. Honest about limitations. Tests that verify behavior. |

### What We Value

- **Pragmatic solutions** over perfect ones. A rule-based classifier that works well beats a half-finished ML pipeline.
- **Clear thinking** over clever code. We want to understand your reasoning.
- **Honest assessment** of what works and what doesn't. Tell us where your approach breaks down.
- **Product instinct**. The UI should feel like something a real user would want to use, not a developer debug tool.
- **Production awareness**. Think about: What if there are 10,000 recordings? What if a new game has completely different mechanics?

### What We Don't Want

- Over-engineered solutions with unnecessary abstractions
- Copy-pasted ML boilerplate without understanding
- Perfect backend with no usable interface
- A pretty UI with no working analysis behind it
- Unsubstantiated claims about accuracy

---

## Questions?

If anything is unclear about the data format, the assignment scope, or the expected output, reach out. Asking good questions is a positive signal, not a negative one.
