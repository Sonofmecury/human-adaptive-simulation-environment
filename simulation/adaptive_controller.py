"""Adaptation controller for simulated human behavior."""

from __future__ import annotations

from dataclasses import dataclass

from simulation.metrics import MetricSnapshot
from simulation.task_environment import TaskEnvironment


@dataclass(frozen=True)
class AdaptationDecision:
    """Controller decision made after a metric update."""

    trial: int
    action: str
    reason: str
    difficulty: float
    pacing: float
    challenge_level: int


class AdaptiveController:
    """Apply simple human-adaptive rules to a task environment."""

    def __init__(
        self,
        *,
        high_success_threshold: float = 0.78,
        high_error_threshold: float = 0.42,
        delay_threshold: float = 1.2,
        stability_threshold: float = 0.88,
        warmup_trials: int = 8,
        adaptation_cooldown: int = 3,
    ) -> None:
        self.high_success_threshold = high_success_threshold
        self.high_error_threshold = high_error_threshold
        self.delay_threshold = delay_threshold
        self.stability_threshold = stability_threshold
        self.warmup_trials = warmup_trials
        self.adaptation_cooldown = adaptation_cooldown
        self._last_adaptation_trial = 0
        self.decisions: list[AdaptationDecision] = []

    def update(
        self,
        *,
        trial: int,
        metrics: MetricSnapshot,
        environment: TaskEnvironment,
    ) -> AdaptationDecision | None:
        if metrics.window_size < self.warmup_trials:
            return None

        action = "maintain"
        reason = "performance within target band"
        can_adapt = trial - self._last_adaptation_trial >= self.adaptation_cooldown

        if can_adapt and metrics.error_rate >= self.high_error_threshold:
            environment.decrease_difficulty()
            action = "decrease_difficulty"
            reason = f"error_rate={metrics.error_rate:.2f}"
        elif can_adapt and metrics.average_reaction_delay >= self.delay_threshold:
            environment.slow_pacing()
            action = "slow_pacing"
            reason = f"reaction_delay={metrics.average_reaction_delay:.2f}"
        elif can_adapt and metrics.success_rate >= self.high_success_threshold:
            environment.increase_difficulty()
            action = "increase_difficulty"
            reason = f"success_rate={metrics.success_rate:.2f}"

        if (
            can_adapt
            and action == "maintain"
            and metrics.success_rate >= 0.65
            and metrics.consistency >= self.stability_threshold
        ):
            environment.introduce_challenge()
            action = "introduce_challenge"
            reason = f"consistency={metrics.consistency:.2f}"
        elif (
            action != "slow_pacing"
            and metrics.average_reaction_delay < self.delay_threshold * 0.9
        ):
            environment.restore_pacing()

        if action != "maintain":
            self._last_adaptation_trial = trial

        decision = AdaptationDecision(
            trial=trial,
            action=action,
            reason=reason,
            difficulty=environment.state.difficulty,
            pacing=environment.state.pacing,
            challenge_level=environment.state.challenge_level,
        )
        self.decisions.append(decision)
        return decision
