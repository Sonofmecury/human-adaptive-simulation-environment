"""Logging helpers for simulation runs."""

from __future__ import annotations

from simulation.adaptive_controller import AdaptationDecision
from simulation.metrics import MetricSnapshot, TrialRecord


class SimulationLogger:
    """Collect concise text logs for trials and adaptation decisions."""

    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose
        self.messages: list[str] = []

    def trial(self, record: TrialRecord, metrics: MetricSnapshot) -> None:
        message = (
            f"[trial] index={record.trial:03d} success={record.success} "
            f"delay={record.reaction_delay:.2f} success_rate={metrics.success_rate:.2f} "
            f"difficulty={record.difficulty:.2f} pacing={record.pacing:.2f}"
        )
        self._write(message)

    def decision(self, decision: AdaptationDecision | None) -> None:
        if decision is None:
            return
        if decision.action == "maintain":
            return
        self._write(
            f"[adapt] trial={decision.trial:03d} action={decision.action} "
            f"reason={decision.reason} difficulty={decision.difficulty:.2f} "
            f"pacing={decision.pacing:.2f} challenge={decision.challenge_level}"
        )

    def _write(self, message: str) -> None:
        self.messages.append(message)
        if self.verbose:
            print(message)
