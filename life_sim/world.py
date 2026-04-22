from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import random

from .types import Action, Agent, Position

DIRS = {
    Action.UP: (0, -1),
    Action.DOWN: (0, 1),
    Action.LEFT: (-1, 0),
    Action.RIGHT: (1, 0),
    Action.WAIT: (0, 0),
}


@dataclass(slots=True)
class StepResult:
    reward: float
    ate_food: bool
    done: bool


class GridWorld:
    def __init__(
        self,
        width: int,
        height: int,
        food_count: int,
        food_respawn_per_step: int,
        observation_radius: int,
        rewards: dict,
        rng: random.Random,
    ) -> None:
        self.width = width
        self.height = height
        self.food_count = food_count
        self.food_respawn_per_step = food_respawn_per_step
        self.observation_radius = observation_radius
        self.rewards = rewards
        self.rng = rng
        self.food: set[Position] = set()

    def in_bounds(self, x: int, y: int):
        """Is position within the bound of the world"""
        return 0 <= x < self.width and 0 <= y < self.height

    def clamp_move(self, x: int, y: int, action: Action) -> Position:
        """Take a step, if within the bounds of the world"""
        dx, dy = DIRS[action]
        nx, ny = x + dx, y + dy

        if not self.in_bounds(nx, ny):
            return x, y
        return nx, ny

    def random_empty_cell(self, occupied: Iterable[Position] = ()) -> Position:
        """
        Select the position of a random empty cell

        raises ValueError if there are no empty cell left
        """
        occupied_set = set(occupied)
        candidates = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in occupied_set
        ]

        if not candidates:
            raise ValueError("No empty cell available")
        return self.rng.choice(candidates)

    def reset_food(self, occupied: Iterable[Position] = ()) -> None:
        self.food.clear()
        occupied_set = set(occupied)
        candidates = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in occupied_set
        ]
        self.rng.shuffle(candidates)
        self.food.update(candidates[: self.food_count])

    def respawn_food(self, occupied: Iterable[Position] = ()) -> None:
        occupied_set = set(occupied)
        missing = max(0, self.food_count - len(self.food))
        to_add = min(self.food_respawn_per_step, missing)
        if to_add <= 0:
            return
        candidates = [
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in self.food and (x, y) not in occupied_set
        ]
        self.rng.shuffle(candidates)
        self.food.update(candidates[:to_add])

    def nearest_food_dir(self, x: int, y: int) -> str:
        visible = []
        for fx, fy in self.food:
            dist = abs(fx - x) + abs(fy - y)
            if dist <= self.observation_radius:
                visible.append((dist, fx, fy))
        if not visible:
            return "NONE"

        _, fx, fy = min(visible)
        if fx == x and fy == y:
            return "HERE"
        if abs(fx - x) >= abs(fy - y):
            return "RIGHT" if fx > x else "LEFT"
        return "DOWN" if fy > y else "UP"

    def observe(self, agent: Agent) -> dict:
        food_dir = self.nearest_food_dir(agent.x, agent.y)
        if agent.energy <= 5:
            bucket = "LOW"
        elif agent.energy <= 12:
            bucket = "MEDIUM"
        else:
            bucket = "HIGH"
        return {
            "x": agent.x,
            "y": agent.y,
            "food_here": (agent.x, agent.y) in self.food,
            "food_dir": food_dir,
            "energy_bucket": bucket,
        }

    def step_agent(self, agent: Agent, action: Action) -> StepResult:
        if not agent.alive:
            return StepResult(reward=0.0, ate_food=False, done=True)
        _step_penalty = float(self.rewards["step_penalty"])
        _food_reward = float(self.rewards["food_reward"])
        nx, ny = self.clamp_move(agent.x, agent.y, action)
        agent.x, agent.y = nx, ny
        agent.age += 1
        agent.energy += _step_penalty
        reward = _step_penalty
        ate_food = False

        if (agent.x, agent.y) in self.food:
            self.food.remove((agent.x, agent.y))
            agent.energy += _food_reward
            reward += _food_reward
            ate_food = True
        if agent.energy <= 0:
            agent.alive = False
            reward += float(self.rewards["death_penalty"])
            return StepResult(reward=reward, ate_food=ate_food, done=True)
        return StepResult(reward=reward, ate_food=ate_food, done=False)
