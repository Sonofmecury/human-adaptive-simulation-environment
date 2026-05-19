"""Rolling performance metrics for human-adaptive simulation."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from statistics import mean, pstdev


@dataclass(frozen=True)
class TrialRecord:
    """One trial outcome with the environment state used for that trial."""

    trial: int
    success: bool
    error: bool
    reaction_delay: float
    difficulty: float
    pacing: float
    challenge_level: int


@dataclass(frozen=True)
class MetricSnapshot:
    """Rolling metrics used by the adaptive controller."""

    success_rate: float
    error_rate: float
    average_reaction_delay: float
    consistency: float
    window_size: int


class PerformanceMetrics:
    """Track trial history and calculate rolling behavioral metrics."""

    def __init__(self, window_size: int = 12) -> None:
        self.window_size = window_size
        self.records: list[TrialRecord] = []
        self._window: deque[TrialRecord] = deque(maxlen=window_size)

    def add(self, record: TrialRecord) -> MetricSnapshot:
        self.records.append(record)
        self._window.append(record)
        return self.snapshot()

    def snapshot(self) -> MetricSnapshot:
        if not self._window:
            return MetricSnapshot(0.0, 0.0, 0.0, 0.0, 0)

        successes = [record.success for record in self._window]
        delays = [record.reaction_delay for record in self._window]
        success_rate = sum(successes) / len(successes)
        error_rate = 1.0 - success_rate
        average_delay = mean(delays)
        delay_std = pstdev(delays) if len(delays) > 1 else 0.0
        consistency = max(0.0, 1.0 - delay_std)

        return MetricSnapshot(
            success_rate=success_rate,
            error_rate=error_rate,
            average_reaction_delay=average_delay,
            consistency=consistency,
            window_size=len(self._window),
        )
