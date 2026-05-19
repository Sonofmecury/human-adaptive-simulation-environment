from __future__ import annotations

from simulation import TaskEnvironment


def test_difficulty_is_clamped_to_supported_bounds() -> None:
    environment = TaskEnvironment()

    for _ in range(20):
        environment.increase_difficulty()
    assert environment.state.difficulty == 1.0

    for _ in range(30):
        environment.decrease_difficulty()
    assert environment.state.difficulty == 0.05
