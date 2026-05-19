"""Run the human-adaptive simulation and save a performance plot."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

from simulation import AdaptiveController, PerformanceMetrics, SimulatedUser, TaskEnvironment
from simulation.logger import SimulationLogger


OUTPUT_PATH = Path(__file__).resolve().parents[1] / "outputs" / "performance_over_time.png"
LOG_PATH = Path(__file__).resolve().parents[1] / "outputs" / "trial_logs.jsonl"


def run_simulation(total_trials: int = 80, verbose: bool = True) -> PerformanceMetrics:
    user = SimulatedUser(skill=0.72, consistency=0.78, fatigue_rate=0.0025, seed=42)
    environment = TaskEnvironment()
    metrics = PerformanceMetrics(window_size=12)
    controller = AdaptiveController()
    logger = SimulationLogger(verbose=verbose)

    for _ in range(total_trials):
        record = environment.run_trial(user)
        snapshot = metrics.add(record)
        decision = controller.update(
            trial=record.trial,
            metrics=snapshot,
            environment=environment,
        )
        if record.trial % 5 == 0 or decision is not None and decision.action != "maintain":
            logger.trial(record, snapshot)
        logger.decision(decision)

    save_plot(metrics, OUTPUT_PATH)
    export_jsonl(metrics, LOG_PATH)
    if verbose:
        print(f"\nSaved plot to {OUTPUT_PATH}")
        print(f"Saved trial log to {LOG_PATH}")
    return metrics


def export_jsonl(metrics: PerformanceMetrics, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for record in metrics.records:
            file.write(
                json.dumps(
                    {
                        "trial": record.trial,
                        "success": record.success,
                        "error": record.error,
                        "reaction_delay": record.reaction_delay,
                        "difficulty": round(record.difficulty, 3),
                        "pacing": round(record.pacing, 3),
                        "challenge_level": record.challenge_level,
                    }
                )
                + "\n"
            )


def save_plot(metrics: PerformanceMetrics, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    trials = [record.trial for record in metrics.records]
    success_values = [1 if record.success else 0 for record in metrics.records]
    delays = [record.reaction_delay for record in metrics.records]
    difficulty = [record.difficulty for record in metrics.records]

    rolling_success = []
    for index in range(len(success_values)):
        start = max(0, index - 11)
        window = success_values[start : index + 1]
        rolling_success.append(sum(window) / len(window))

    plt.figure(figsize=(10, 6))
    plt.plot(trials, rolling_success, label="Rolling success rate", linewidth=2)
    plt.plot(trials, delays, label="Reaction delay", alpha=0.75)
    plt.plot(trials, difficulty, label="Difficulty", linewidth=2)
    plt.xlabel("Trial")
    plt.ylabel("Metric value")
    plt.title("Human-Adaptive Simulation Performance Over Time")
    plt.ylim(0, max(1.6, max(delays) + 0.1))
    plt.grid(alpha=0.25)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=140)
    plt.close()


def main() -> None:
    run_simulation()


if __name__ == "__main__":
    main()
