from __future__ import annotations

from simulation import AdaptiveController, TaskEnvironment
from simulation.metrics import MetricSnapshot


def test_controller_decreases_difficulty_when_error_rate_is_high() -> None:
    environment = TaskEnvironment()
    controller = AdaptiveController(warmup_trials=1)

    decision = controller.update(
        trial=12,
        metrics=MetricSnapshot(
            success_rate=0.4,
            error_rate=0.6,
            average_reaction_delay=0.9,
            consistency=0.8,
            window_size=12,
        ),
        environment=environment,
    )

    assert decision is not None
    assert decision.action == "decrease_difficulty"
    assert environment.state.difficulty < 0.35


def test_controller_increases_difficulty_when_success_rate_is_high() -> None:
    environment = TaskEnvironment()
    controller = AdaptiveController(warmup_trials=1)

    decision = controller.update(
        trial=12,
        metrics=MetricSnapshot(
            success_rate=0.9,
            error_rate=0.1,
            average_reaction_delay=0.8,
            consistency=0.8,
            window_size=12,
        ),
        environment=environment,
    )

    assert decision is not None
    assert decision.action == "increase_difficulty"
    assert environment.state.difficulty > 0.35
