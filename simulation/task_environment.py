"""Simple task environment that can adapt difficulty and pacing."""

from __future__ import annotations

from dataclasses import dataclass

from simulation.user_model import SimulatedUser
from simulation.metrics import TrialRecord


@dataclass
class TaskState:
    """Current task parameters exposed to the adaptive controller."""

    difficulty: float = 0.35
    pacing: float = 1.0
    challenge_level: int = 1


class TaskEnvironment:
    """Runs simple trials and exposes methods for runtime adaptation."""

    def __init__(self, state: TaskState | None = None) -> None:
        self.state = state or TaskState()
        self.trial_index = 0

    def run_trial(self, user: SimulatedUser) -> TrialRecord:
        self.trial_index += 1
        response = user.attempt(self.state.difficulty, self.state.pacing)
        return TrialRecord(
            trial=self.trial_index,
            success=response.success,
            error=not response.success,
            reaction_delay=response.reaction_delay,
            difficulty=self.state.difficulty,
            pacing=self.state.pacing,
            challenge_level=self.state.challenge_level,
        )

    def increase_difficulty(self, amount: float = 0.08) -> None:
        self.state.difficulty = min(1.0, self.state.difficulty + amount)

    def decrease_difficulty(self, amount: float = 0.08) -> None:
        self.state.difficulty = max(0.05, self.state.difficulty - amount)

    def slow_pacing(self, amount: float = 0.08) -> None:
        self.state.pacing = max(0.55, self.state.pacing - amount)

    def restore_pacing(self, amount: float = 0.04) -> None:
        self.state.pacing = min(1.15, self.state.pacing + amount)

    def introduce_challenge(self) -> None:
        self.state.challenge_level += 1
        self.increase_difficulty(0.05)
