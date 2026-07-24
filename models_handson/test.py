"""W&B Models ハンズオンの主要機能を最小構成で事前確認する。

実際に次のオブジェクトを作成します。

- Experiment Run: 1つ
- Table: 1つ
- Artifact: 1つ
- Draft Report: 1つ
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import time


DEFAULT_PROJECT = "wandb-models-handson"
RUN_NAME = "pre-course-check"
ARTIFACT_NAME = "pre-course-check-data"
REQUIRED_PACKAGES = ("wandb", "wandb_workspaces")


def check_dependencies() -> None:
    """事前確認に必要なパッケージが入っていることを確認する。"""
    missing: list[str] = []
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)

    if missing:
        raise RuntimeError(
            f"必要なパッケージが不足しています: {', '.join(missing)}\n"
            "models_handson ディレクトリで `uv sync` を実行してください。"
        )


def resolve_wandb_destination() -> tuple[str, str]:
    """W&B のログイン状態を確認し、保存先を返す。"""
    import wandb

    try:
        entity = os.getenv("WANDB_ENTITY") or wandb.Api(timeout=30).default_entity
    except Exception as error:
        raise RuntimeError(
            "W&B に接続できません。`wandb login` を実行してください。"
        ) from error

    if not entity:
        raise RuntimeError(
            "W&B Entity を特定できません。`wandb login` を実行するか、"
            "WANDB_ENTITY を設定してください。"
        )

    project = os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)
    return entity, project


def create_run(project: str) -> str:
    """1 Run にExperiment、1 Table、1 Artifactを記録する。"""
    import wandb

    rows = [
        {"epoch": 0, "train/loss": 1.00, "val/accuracy": 0.55},
        {"epoch": 1, "train/loss": 0.72, "val/accuracy": 0.68},
        {"epoch": 2, "train/loss": 0.51, "val/accuracy": 0.79},
    ]

    with wandb.init(
        project=project,
        name=RUN_NAME,
        job_type="pre-course-check",
        config={"learning_rate": 0.01, "epochs": len(rows)},
    ) as run:
        # Experiment: 1つのRunへ短い学習曲線を記録する。
        for row in rows:
            run.log(
                {
                    "epoch": row["epoch"],
                    "train/loss": row["train/loss"],
                    "val/accuracy": row["val/accuracy"],
                }
            )

        # Table: 上と同じ結果を1つのTableとして記録する。
        table = wandb.Table(
            columns=["epoch", "train/loss", "val/accuracy"],
            data=[
                [row["epoch"], row["train/loss"], row["val/accuracy"]]
                for row in rows
            ],
        )
        run.log({"evaluation/table": table})

        # Artifact: 結果JSONを1つのArtifactとして記録する。
        artifact = wandb.Artifact(
            name=ARTIFACT_NAME,
            type="dataset",
            description="受講前確認用の最小データ",
            metadata={"rows": len(rows)},
        )
        with artifact.new_file("metrics.json", mode="w", encoding="utf-8") as file:
            json.dump(rows, file, ensure_ascii=False, indent=2)
        run.log_artifact(artifact)

        run.summary["best/val_accuracy"] = max(
            row["val/accuracy"] for row in rows
        )
        run_url = run.url

    return run_url


def create_report(entity: str, project: str, run_url: str) -> str:
    """事前確認Runのグラフを1枚だけ含む簡素なDraft Reportを作成する。"""
    import wandb_workspaces.reports.v2 as wr

    runs = wr.Runset(
        entity=entity,
        project=project,
        name="Pre-course check run",
        filters="Metric('jobType') == 'pre-course-check'",
    )
    report = wr.Report(
        entity=entity,
        project=project,
        title="W&B Models Pre-course Check",
        description="Experiment、Table、Artifactの作成確認",
        width="readable",
        blocks=[
            wr.MarkdownBlock(
                text=(
                    "事前確認用の最小Runです。"
                    f"[作成したRunを開く]({run_url})"
                )
            ),
            wr.PanelGrid(
                runsets=[runs],
                panels=[
                    wr.LinePlot(
                        title="Experiment metrics",
                        x="epoch",
                        y=["train/loss", "val/accuracy"],
                    )
                ],
            ),
        ],
    )
    report.save(draft=True)
    return report.url


def main() -> None:
    check_dependencies()
    entity, project = resolve_wandb_destination()

    print("W&B Models 事前確認を開始します。")
    print(f"Python:  {sys.executable}")
    print(f"Entity:  {entity}")
    print(f"Project: {project}")
    print("1 Run、1 Table、1 Artifact、1 Draft Reportを作成します。")

    started_at = time.monotonic()
    run_url = create_run(project)
    report_url = create_report(entity, project, run_url)
    elapsed = time.monotonic() - started_at

    print("\n" + "=" * 72)
    print("ALL CHECKS PASSED")
    print("=" * 72)
    print(f"Run:    {run_url}")
    print(f"Report: {report_url}")
    print(f"Total:  {elapsed:.1f}秒")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\n[FAILED] {error}", file=sys.stderr)
        raise SystemExit(1) from error
