from __future__ import annotations

import pytest

from simulation.metrics import PerformanceMetrics, TrialRecord


def test_performance_metrics_snapshot_uses_recent_window() -> None:
    metrics = PerformanceMetrics(window_size=3)

    for index, success in enumerate([True, False, True, True], start=1):
        metrics.add(
            TrialRecord(
                trial=index,
                success=success,
                error=not success,
                reaction_delay=0.5 + index * 0.1,
                difficulty=0.3,
                pacing=1.0,
                challenge_level=1,
            )
        )

    snapshot = metrics.snapshot()

    assert snapshot.window_size == 3
    assert snapshot.success_rate == pytest.approx(2 / 3)
    assert snapshot.error_rate == pytest.approx(1 / 3)
    assert snapshot.average_reaction_delay > 0
    assert 0 <= snapshot.consistency <= 1
