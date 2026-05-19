from __future__ import annotations

from simulation.user_model import SimulatedUser


def test_simulated_user_returns_valid_response() -> None:
    user = SimulatedUser(seed=1)

    response = user.attempt(difficulty=0.4, pacing=1.0)

    assert isinstance(response.success, bool)
    assert response.reaction_delay > 0
    assert response.error_magnitude >= 0
