"""
4: Sweeps - ハイパーパラメータ探索

環境構築（models_handson ディレクトリで実行）:
    uv sync

Random Sweep で learning_rate と epochs を探索します。ローカル Agent の試行数は
count=6 に固定しているため、明示的に増やさない限り無制限には実行されません。
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


def get_wandb_target() -> tuple[str, str]:
    entity = os.getenv("WANDB_ENTITY")
    if not entity:
        raise RuntimeError(
            "WANDB_ENTITY が未設定です。W&B の Team Entity を設定してください。"
        )
    return entity, os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)


def simulated_fold_accuracy(
    learning_rate: float,
    epochs: int,
    batch_size: int,
    fold: int,
) -> float:
    """最適値付近で高精度になる、再現可能な模擬評価値を返す。"""
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
    entity, project = get_wandb_target()
    with wandb.init(
        entity=entity,
        project=project,
        job_type="sweep-trial",
        tags=["handson", "sweep"],
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
    entity, project = get_wandb_target()
    sweep_id = wandb.sweep(
        sweep=SWEEP_CONFIG,
        entity=entity,
        project=project,
    )
    print(f"Sweep ID: {sweep_id}")
    wandb.agent(sweep_id, function=train, count=6)


if __name__ == "__main__":
    main()
