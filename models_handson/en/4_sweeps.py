"""
4: Sweeps - Hyperparameter Optimization

Setup (run from the models_handson directory):
    uv sync

This Random Sweep explores learning_rate, epochs, and batch_size. The local
Agent is limited to count=6, so it cannot run indefinitely unless increased.
"""

from __future__ import annotations

import os
import random

import numpy as np
import wandb


DEFAULT_PROJECT = "wandb-models-handson"

SWEEP_CONFIG = {
    "method": "random",
    "metric": {"name": "val/accuracy", "goal": "maximize"},
    "parameters": {
        "learning_rate": {"values": [0.0005, 0.001, 0.003, 0.01, 0.03]},
        "epochs": {"values": [5, 10, 15]},
        "batch_size": {"values": [16, 32, 64]},
    },
}


def simulated_fold_accuracy(
    learning_rate: float,
    epochs: int,
    batch_size: int,
    fold: int,
) -> float:
    """Return a reproducible simulated score that peaks near ideal values."""
    seed = int(learning_rate * 1_000_000) + epochs * 100 + batch_size + fold
    rng = random.Random(seed)
    lr_score = max(0.0, 1.0 - abs(np.log10(learning_rate) + 2.0) * 0.16)
    epoch_score = min(epochs / 15.0, 1.0)
    batch_penalty = abs(batch_size - 32) / 32.0 * 0.025
    return float(
        np.clip(
            0.58 + 0.22 * lr_score + 0.10 * epoch_score - batch_penalty + rng.uniform(-0.02, 0.02),
            0.0,
            0.99,
        )
    )


def train() -> None:
    project = os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)
    with wandb.init(
        project=project,
        job_type="sweep-trial",
        tags=["sweep"],
    ) as run:
        config = run.config
        fold_accuracies: list[float] = []
        for fold in range(5):
            accuracy = simulated_fold_accuracy(
                learning_rate=float(config.learning_rate),
                epochs=int(config.epochs),
                batch_size=int(config.batch_size),
                fold=fold,
            )
            fold_accuracies.append(accuracy)
            run.log(
                {
                    "fold/index": fold,
                    "fold/accuracy": accuracy,
                    "val/accuracy": float(np.mean(fold_accuracies)),
                }
            )


def main() -> None:
    project = os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)
    sweep_id = wandb.sweep(
        sweep=SWEEP_CONFIG,
        project=project,
    )
    print(f"Sweep ID: {sweep_id}")
    wandb.agent(sweep_id, function=train, count=6)


if __name__ == "__main__":
    main()
