"""
6: Reports - 実験結果の可視化と共有

環境構築（models_handson ディレクトリで実行）:
    uv sync

Report and Workspace APIはPublic Previewです。最新仕様:
https://docs.wandb.ai/models/reports/create-a-report

GUIでの基本手順:
1. W&B ProjectのWorkspaceを開く。
2. 右上のCreate reportを選び、開始時に含めるPanelを選択する。
3. 本文、見出し、Panel Grid、Run set、グラフを追加・編集する。
4. Publish to projectで公開し、Shareから共同利用者へ共有する。

利用できる主な要素:
- 文章: Heading、Markdown、List、Code、Image、Media、Table of contents
- Run整理: Runset、PanelGrid、Filter、Group、RunComparer、CodeComparer
- 基本グラフ: LinePlot、BarPlot、ScatterPlot、ScalarChart、CustomChart
- Sweep分析: ParallelCoordinatesPlot、ParameterImportancePlot
- データ/Artifact: Summary Table、Artifact、Artifact File Panel

この例では作り過ぎないよう、次の2種類だけを使用します:
- LinePlot: 1・3・4章で記録した学習・検証メトリクス
- ParameterImportancePlot: 4章のSweep設定とval/accuracyの関係

参考Report:
- Nejumi LLMリーダーボード4:
  https://wandb.ai/llm-leaderboard/nejumi-leaderboard4/reports/Nejumi-LLM-4--VmlldzoxMzc1OTk1MA
- OpenPI and W&B for Physical AI (EN):
  https://wandb.ai/wandb-smle/openpi-aloha-wandb-integration/reports/OpenPI-and-W-B-for-Physical-AI-Experiment-tracking-guide--VmlldzoxNjQyMzc4Mg
- OpenPI x W&B (JP):
  https://wandb.ai/wandb-smle/openpi-aloha-wandb-integration/reports/OpenPI-x-W-B--VmlldzoxNjQxNjczNQ
"""

from __future__ import annotations

import os


DEFAULT_PROJECT = "wandb-models-handson"
DEFAULT_REGISTRY = "Models"
DEFAULT_COLLECTION = "models-handson-model"


def get_wandb_settings() -> tuple[str, str, str, str]:
    entity = os.getenv("WANDB_ENTITY")
    if not entity:
        raise RuntimeError(
            "WANDB_ENTITY が未設定です。W&B の Team Entity を設定してください。"
        )
    return (
        entity,
        os.getenv("WANDB_PROJECT", DEFAULT_PROJECT),
        os.getenv("WANDB_REGISTRY", DEFAULT_REGISTRY),
        os.getenv("WANDB_REGISTRY_COLLECTION", DEFAULT_COLLECTION),
    )


def main() -> None:
    try:
        import wandb_workspaces.reports.v2 as wr
    except ImportError as error:
        raise RuntimeError(
            "wandb-workspaces が必要です。models_handson で `uv sync` を実行してください。"
        ) from error

    entity, project, registry_name, collection_name = get_wandb_settings()
    project_url = f"https://wandb.ai/{entity}/{project}"
    registry_url = "https://wandb.ai/registry/"

    experiment_runs = wr.Runset(
        entity=entity,
        project=project,
        name="Experiment and model training runs",
        filters="Metric('jobType') in ['experiment', 'model-training']",
    )
    sweep_runs = wr.Runset(
        entity=entity,
        project=project,
        name="Sweep trials",
        filters="Metric('jobType') in ['sweep-trial']",
    )

    report = wr.Report(
        entity=entity,
        project=project,
        title="W&B Models Hands-on Results",
        description="1〜5章で作成したRun、Table、Artifact、Sweep、Registryのまとめ",
        width="readable",
        blocks=[
            wr.TableOfContents(),
            wr.H2(text="実験とモデル学習の推移"),
            wr.MarkdownBlock(
                text=(
                    "1章の模擬実験と3章のArtifact付きモデル学習を比較します。"
                    "同じメトリクス名を使うことで、複数Runを一つのグラフへ重ねられます。"
                )
            ),
            wr.PanelGrid(
                runsets=[experiment_runs],
                panels=[
                    wr.LinePlot(
                        title="Training and validation metrics",
                        x="Step",
                        y=["train/loss", "val/loss", "val/accuracy"],
                        title_x="Step",
                        title_y="Metric value",
                    )
                ],
            ),
            wr.H2(text="Sweepのパラメータ重要度"),
            wr.PanelGrid(
                runsets=[sweep_runs],
                panels=[
                    wr.ParameterImportancePlot(with_respect_to="val/accuracy")
                ],
            ),
            wr.H2(text="Table・Artifacts・Registry"),
            wr.MarkdownBlock(
                text=(
                    f"- [Project Workspace]({project_url}) で2章の `examples/table` を確認\n"
                    f"- [Project Artifacts]({project_url}/artifacts) で "
                    "`models-handson-dataset`、`models-handson-processed-dataset`、"
                    "`models-handson-model` のLineageを確認\n"
                    f"- [Registry]({registry_url}) の `{registry_name}/{collection_name}` で"
                    "candidate Versionを確認"
                )
            ),
            wr.H2(text="参考Report"),
            wr.MarkdownBlock(
                text=(
                    "- [Nejumi LLMリーダーボード4]"
                    "(https://wandb.ai/llm-leaderboard/nejumi-leaderboard4/reports/"
                    "Nejumi-LLM-4--VmlldzoxMzc1OTk1MA)\n"
                    "- [OpenPI and W&B for Physical AI (EN)]"
                    "(https://wandb.ai/wandb-smle/openpi-aloha-wandb-integration/reports/"
                    "OpenPI-and-W-B-for-Physical-AI-Experiment-tracking-guide--VmlldzoxNjQyMzc4Mg)\n"
                    "- [OpenPI x W&B (JP)]"
                    "(https://wandb.ai/wandb-smle/openpi-aloha-wandb-integration/reports/"
                    "OpenPI-x-W-B--VmlldzoxNjQxNjczNQ)"
                )
            ),
        ],
    )

    report.save(draft=True)
    print(f"Draft report saved: {report.url}")
    print("内容を確認後、W&B UIからPublish to projectを実行してください。")


if __name__ == "__main__":
    main()
