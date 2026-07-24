"""
3: Artifacts - データとモデルのバージョン管理

環境構築（models_handson ディレクトリで実行）:
    uv sync

このスクリプトで作成する Artifact:
- models-handson-dataset
- models-handson-processed-dataset
- models-handson-model

データ生成、前処理、模擬学習を別 Run にし、use_artifact() で入力を宣言することで
W&B にデータからモデルまでの Lineage を記録します。
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
import tempfile

import numpy as np
import wandb


DEFAULT_PROJECT = "wandb-models-handson"
DATASET_NAME = "models-handson-dataset"
PROCESSED_DATASET_NAME = "models-handson-processed-dataset"
MODEL_NAME = "models-handson-model"


def get_wandb_target() -> tuple[str, str]:
    entity = os.getenv("WANDB_ENTITY")
    if not entity:
        raise RuntimeError(
            "WANDB_ENTITY が未設定です。W&B の Team Entity を設定してください。"
        )
    return entity, os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)


def create_dataset(path: Path, samples: int = 120) -> None:
    rng = np.random.default_rng(42)
    x1 = rng.normal(0.0, 1.0, samples)
    x2 = rng.normal(0.5, 1.2, samples)
    noise = rng.normal(0.0, 0.35, samples)
    target = (1.4 * x1 - 0.9 * x2 + noise > 0.0).astype(int)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["feature_1", "feature_2", "target"])
        writer.writerows(zip(x1, x2, target, strict=True))


def load_dataset(path: Path) -> tuple[np.ndarray, np.ndarray]:
    values = np.genfromtxt(path, delimiter=",", skip_header=1)
    return values[:, :2], values[:, 2]


def preprocess_dataset(source: Path, destination: Path) -> None:
    features, target = load_dataset(source)
    mean = features.mean(axis=0)
    std = features.std(axis=0)
    normalized = (features - mean) / np.where(std == 0.0, 1.0, std)

    with destination.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["feature_1", "feature_2", "target"])
        writer.writerows(
            zip(normalized[:, 0], normalized[:, 1], target.astype(int), strict=True)
        )


def is_offline_mode() -> bool:
    return os.getenv("WANDB_MODE", "").lower() in {"offline", "dryrun", "disabled"}


def artifact_input_path(
    run: wandb.Run,
    artifact_or_name: wandb.Artifact | str,
    filename: str,
    fallback: Path,
    download_root: Path,
) -> Path:
    """Online では Artifact を取得し、Offline smoke test ではローカル入力を使う。"""
    if is_offline_mode():
        try:
            run.use_artifact(artifact_or_name)
        except (TypeError, ValueError, wandb.Error):
            # Offline backend はサーバー上の alias を解決できないため、入力宣言だけ省略する。
            pass
        return fallback

    artifact = run.use_artifact(artifact_or_name)
    artifact_dir = Path(artifact.download(root=str(download_root)))
    return artifact_dir / filename


def train_logistic_model(
    run: wandb.Run,
    dataset_path: Path,
    model_path: Path,
    epochs: int = 20,
) -> float:
    features, target = load_dataset(dataset_path)
    split = int(len(features) * 0.8)
    x_train, x_val = features[:split], features[split:]
    y_train, y_val = target[:split], target[split:]

    weights = np.zeros(x_train.shape[1], dtype=np.float64)
    bias = 0.0
    learning_rate = 0.15
    best_accuracy = 0.0

    for epoch in range(epochs):
        logits = np.clip(x_train @ weights + bias, -30.0, 30.0)
        probabilities = 1.0 / (1.0 + np.exp(-logits))
        error = probabilities - y_train
        weights -= learning_rate * (x_train.T @ error) / len(x_train)
        bias -= learning_rate * float(error.mean())

        train_loss = -np.mean(
            y_train * np.log(probabilities + 1e-8)
            + (1.0 - y_train) * np.log(1.0 - probabilities + 1e-8)
        )
        val_probabilities = 1.0 / (1.0 + np.exp(-(x_val @ weights + bias)))
        val_loss = -np.mean(
            y_val * np.log(val_probabilities + 1e-8)
            + (1.0 - y_val) * np.log(1.0 - val_probabilities + 1e-8)
        )
        val_accuracy = float(np.mean((val_probabilities >= 0.5) == y_val))
        best_accuracy = max(best_accuracy, val_accuracy)
        run.log(
            {
                "train/loss": float(train_loss),
                "val/loss": float(val_loss),
                "val/accuracy": val_accuracy,
            }
        )

    np.savez(model_path, weights=weights, bias=np.array([bias]))
    return best_accuracy


def main() -> None:
    entity, project = get_wandb_target()

    with tempfile.TemporaryDirectory(prefix="wandb-models-handson-") as temp_dir:
        work_dir = Path(temp_dir)
        raw_csv = work_dir / "dataset.csv"
        processed_csv = work_dir / "processed_dataset.csv"
        model_file = work_dir / "model_weights.npz"
        create_dataset(raw_csv)

        with wandb.init(
            entity=entity,
            project=project,
            name="artifact-data-generation",
            job_type="data-generation",
            tags=["handson", "artifact", "dataset"],
        ) as data_run:
            dataset = wandb.Artifact(
                name=DATASET_NAME,
                type="dataset",
                description="W&B Models ハンズオン用の合成分類データ",
                metadata={"rows": 120, "source": "generated"},
            )
            dataset.add_file(str(raw_csv), name=raw_csv.name)
            logged_dataset = data_run.log_artifact(dataset, aliases=["raw"])

        with wandb.init(
            entity=entity,
            project=project,
            name="artifact-preprocessing",
            job_type="data-processing",
            tags=["handson", "artifact", "preprocessing"],
        ) as processing_run:
            source_csv = artifact_input_path(
                processing_run,
                logged_dataset if is_offline_mode() else f"{DATASET_NAME}:latest",
                raw_csv.name,
                raw_csv,
                work_dir / "downloaded-raw",
            )
            preprocess_dataset(source_csv, processed_csv)
            processed_dataset = wandb.Artifact(
                name=PROCESSED_DATASET_NAME,
                type="dataset",
                description="標準化済みの合成分類データ",
                metadata={"transform": "standardization"},
            )
            processed_dataset.add_file(str(processed_csv), name=processed_csv.name)
            logged_processed_dataset = processing_run.log_artifact(
                processed_dataset,
                aliases=["ready"],
            )

        with wandb.init(
            entity=entity,
            project=project,
            name="artifact-model-training",
            job_type="model-training",
            config={"learning_rate": 0.15, "epochs": 20, "model": "logistic-regression"},
            tags=["handson", "artifact", "training"],
        ) as training_run:
            training_csv = artifact_input_path(
                training_run,
                (
                    logged_processed_dataset
                    if is_offline_mode()
                    else f"{PROCESSED_DATASET_NAME}:latest"
                ),
                processed_csv.name,
                processed_csv,
                work_dir / "downloaded-processed",
            )
            best_accuracy = train_logistic_model(training_run, training_csv, model_file)
            model_artifact = wandb.Artifact(
                name=MODEL_NAME,
                type="model",
                description="NumPyで学習した軽量なロジスティック回帰モデル",
                metadata={"best_val_accuracy": best_accuracy},
            )
            model_artifact.add_file(str(model_file), name=model_file.name)
            training_run.log_artifact(model_artifact, aliases=["candidate"])
            training_run.summary["best/val_accuracy"] = best_accuracy
            print(f"Created model artifact from: {training_run.url}")

    print("Artifacts の Lineage で dataset -> processed dataset -> model を確認してください。")


if __name__ == "__main__":
    main()
