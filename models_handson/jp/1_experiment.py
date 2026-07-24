"""
1: Experiment Tracking - 実験管理の基本

環境構築（models_handson ディレクトリで実行）:
    uv sync

このスクリプトで学べること:
- Config、Tags、Group、Job Type による Run の整理
- train/ と val/ を使ったメトリクスの階層化
- define_metric() によるカスタム X 軸
- with wandb.init(...) による Run の確実な終了

事前に WANDB_ENTITY を設定してください。WANDB_PROJECT を省略した場合は
"wandb-models-handson" を使用します。
"""

from __future__ import annotations

import math
import os
import random

import wandb


DEFAULT_PROJECT = "wandb-models-handson"
LEARNING_RATES = [0.0005, 0.001, 0.003, 0.01, 0.03]


def get_wandb_target() -> tuple[str, str]:
    """環境変数から保存先を取得し、誤った場所への記録を防ぐ。"""
    entity = os.getenv("WANDB_ENTITY")
    if not entity:
        raise RuntimeError(
            "WANDB_ENTITY が未設定です。W&B の Team Entity を設定してください。"
        )
    return entity, os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)


def simulate_metrics(run_index: int, epoch: int) -> dict[str, float]:
    """Run と epoch が同じなら同じ値になる軽量な模擬メトリクスを返す。"""
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
    entity, project = get_wandb_target()

    for run_index, learning_rate in enumerate(LEARNING_RATES):
        config = {
            "learning_rate": learning_rate,
            "architecture": "small-mlp",
            "dataset": "synthetic-classification",
            "epochs": 10,
            "seed": 10_000 + run_index,
        }

        with wandb.init(
            entity=entity,
            project=project,
            name=f"experiment-{run_index + 1}",
            group="models-handson-baselines",
            job_type="experiment",
            config=config,
            tags=["handson", "experiment", "baseline"],
        ) as run:
            # custom/epoch_squared を X 軸として custom/inverse_epoch を表示する。
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

    print("\nW&B UI の Workspace で Run の比較、Group、Tags、各曲線を確認してください。")


if __name__ == "__main__":
    main()
