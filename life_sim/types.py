from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Tuple

# Position in a 2D world
Position = Tuple[int, int]


# Possible actions in this 2d world
class Action(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    WAIT = "WAIT"


@dataclass(slots=True)
class Traits:
    exploration_bias: float = 0.2
    reproduction_threshold: float = 18.0
    food_seek_weight: float = 1.0


@dataclass(slots=True)
class MemoryState:
    last_seen_food_dir: str = "NONE"
    steps_since_food: int = 0
    visited_counts: Dict[Position, int] = field(default_factory=dict)


@dataclass(slots=True)
class Agent:
    agent_id: int
    x: int
    y: int
    energy: float
    age: int = 0
    alive: bool = True
    traits: Traits = field(default_factory=Traits)
    memory: MemoryState = field(default_factory=MemoryState)

    @property
    def pos(self) -> Position:
        return (self.x, self.y)
