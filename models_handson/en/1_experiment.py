"""
1: Experiment Tracking Fundamentals

Setup (run from the models_handson directory):
    uv sync

What you will learn:
- Organize Runs with Config, Tags, Group, and Job Type
- Group metrics into train/ and val/ namespaces
- Define a custom X-axis with define_metric()
- Reliably finish Runs with with wandb.init(...)

The destination Entity is resolved from the W&B SDK login or WANDB_ENTITY.
If WANDB_PROJECT is omitted, the script uses "wandb-models-handson".
"""

from __future__ import annotations

import math
import os
import random

import wandb


DEFAULT_PROJECT = "wandb-models-handson"
LEARNING_RATES = [0.0005, 0.001, 0.003, 0.01, 0.03]


def simulate_metrics(run_index: int, epoch: int) -> dict[str, float]:
    """Return lightweight deterministic metrics for a Run and epoch."""
    rng = random.Random(10_000 + run_index * 100 + epoch)
    difficulty = run_index * 0.025
    train_loss = max(
        0.02,
        1.15 * math.exp(-0.32 * epoch) + difficulty + rng.uniform(-0.015, 0.015),
    )
    val_loss = max(
        0.03,
        1.25 * math.exp(-0.28 * epoch) + difficulty + rng.uniform(-0.01, 0.02),
    )
    val_accuracy = min(
        0.99,
        max(0.0, 1.0 - val_loss * 0.72 + rng.uniform(-0.01, 0.01)),
    )
    return {
        "train/loss": train_loss,
        "val/loss": val_loss,
        "val/accuracy": val_accuracy,
    }


def main() -> None:
    project = os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)

    for run_index, learning_rate in enumerate(LEARNING_RATES):
        config = {
            "learning_rate": learning_rate,
            "architecture": "small-mlp",
            "dataset": "synthetic-classification",
            "epochs": 10,
            "seed": 10_000 + run_index,
        }

        with wandb.init(
            project=project,
            name=f"experiment-{run_index + 1}",
            group="models-handson-baselines",
            job_type="experiment",
            config=config,
            tags=["experiment", "baseline"],
        ) as run:
            # Plot custom/inverse_epoch against custom/epoch_squared.
            run.define_metric("custom/epoch_squared")
            run.define_metric(
                "custom/inverse_epoch",
                step_metric="custom/epoch_squared",
            )

            best_accuracy = 0.0
            for epoch in range(config["epochs"]):
                metrics = simulate_metrics(run_index, epoch)
                best_accuracy = max(best_accuracy, metrics["val/accuracy"])
                run.log(
                    {
                        **metrics,
                        "custom/epoch_squared": epoch**2,
                        "custom/inverse_epoch": 1.0 / (epoch + 1),
                    }
                )

            run.summary["best/val_accuracy"] = best_accuracy
            print(f"Created: {run.name} -> {run.url}")

    print("\nOpen the W&B Workspace to compare Runs, Groups, Tags, and charts.")


if __name__ == "__main__":
    main()
