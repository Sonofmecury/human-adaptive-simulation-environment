"""Simulated human user model."""

from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class UserResponse:
    """Outcome of one simulated user attempt."""

    success: bool
    reaction_delay: float
    error_magnitude: float


class SimulatedUser:
    """Probabilistic user with skill, fatigue, and consistency parameters."""

    def __init__(
        self,
        *,
        skill: float = 0.65,
        consistency: float = 0.8,
        fatigue_rate: float = 0.003,
        seed: int | None = None,
    ) -> None:
        self.skill = skill
        self.consistency = consistency
        self.fatigue_rate = fatigue_rate
        self.rng = random.Random(seed)
        self.trials_seen = 0

    def attempt(self, difficulty: float, pacing: float) -> UserResponse:
        self.trials_seen += 1
        fatigue = min(0.25, self.trials_seen * self.fatigue_rate)
        noise = self.rng.uniform(-0.15, 0.15) * (1.0 - self.consistency)
        success_probability = self._clamp(
            self.skill - difficulty * 0.55 - fatigue + noise, 0.05, 0.95
        )
        success = self.rng.random() < success_probability

        base_delay = 0.55 + difficulty * 0.75 + fatigue
        pacing_pressure = max(0.0, 1.0 - pacing) * 0.25
        reaction_delay = max(
            0.2, base_delay + pacing_pressure + self.rng.uniform(-0.08, 0.08)
        )
        error_magnitude = 0.0 if success else self.rng.uniform(0.2, 1.0 + difficulty)

        return UserResponse(
            success=success,
            reaction_delay=round(reaction_delay, 3),
            error_magnitude=round(error_magnitude, 3),
        )

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))
