"""Data models for the interview project.

Includes input schemas (game mechanics) and output schemas
(activity phases, highlights) for the candidate to use.
"""

from pydantic import BaseModel, Field


# --- Input schemas (provided with the sample data) ---


class GameMechanic(BaseModel):
    """A game mechanic that can be detected in gameplay recordings."""

    mechanic_id: str
    display_name: str
    category: str
    reasoning: str


class Checkpoint(BaseModel):
    """A specific gameplay moment tied to a mechanic."""

    description: str = Field(max_length=300)
    mechanic_id: str


# --- Output schemas (for the candidate to produce) ---


class ActivityPhase(BaseModel):
    """A classified time range within a recording."""

    start: float = Field(description="Start time in seconds from recording start")
    end: float = Field(description="End time in seconds from recording start")
    phase: str = Field(description="Phase label: idle, exploration, high_activity, menu, or custom")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")


class Highlight(BaseModel):
    """An interesting moment detected in a recording."""

    start: float = Field(description="Start time in seconds")
    end: float = Field(description="End time in seconds")
    label: str = Field(description="Short description of what happens")
    confidence: float = Field(ge=0.0, le=1.0)
    mechanics_matched: list[str] = Field(
        default_factory=list,
        description="List of mechanic_id values matched",
    )
    reason: str = Field(description="Why this moment is interesting")
