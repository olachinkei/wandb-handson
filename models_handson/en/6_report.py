"""
6: Reports - Visualizing and Sharing Experiment Results

Setup (run from the models_handson directory):
    uv sync

The Report and Workspace API is in Public Preview. See the latest documentation:
https://docs.wandb.ai/models/reports/create-a-report

Basic UI workflow:
1. Open the W&B Project Workspace.
2. Select Create report and choose the initial Panels.
3. Add or edit text, headings, Panel Grids, Run sets, and charts.
4. Select Publish to project, then use Share to collaborate.

Key available elements:
- Content: Heading, Markdown, List, Code, Image, Media, Table of contents
- Run organization: Runset, PanelGrid, Filter, Group, RunComparer, CodeComparer
- Charts: LinePlot, BarPlot, ScatterPlot, ScalarChart, CustomChart
- Sweep analysis: ParallelCoordinatesPlot, ParameterImportancePlot
- Data/Artifacts: Summary Table, Artifact, Artifact File Panel

To keep this example focused, it uses only:
- LinePlot: training and validation metrics logged in chapters 1, 3, and 4
- ParameterImportancePlot: chapter 4 Sweep settings versus val/accuracy

Example Reports:
- Nejumi LLM Leaderboard 4:
  https://wandb.ai/llm-leaderboard/nejumi-leaderboard4/reports/Nejumi-LLM-4--VmlldzoxMzc1OTk1MA
- OpenPI and W&B for Physical AI (EN):
  https://wandb.ai/wandb-smle/openpi-aloha-wandb-integration/reports/OpenPI-and-W-B-for-Physical-AI-Experiment-tracking-guide--VmlldzoxNjQyMzc4Mg
- OpenPI x W&B (JP):
  https://wandb.ai/wandb-smle/openpi-aloha-wandb-integration/reports/OpenPI-x-W-B--VmlldzoxNjQxNjczNQ
"""

from __future__ import annotations

import os

import wandb


DEFAULT_PROJECT = "wandb-models-handson"
DEFAULT_REGISTRY_TARGET_PATH = "wandb-registry-models_handson/handson"


def main() -> None:
    try:
        import wandb_workspaces.reports.v2 as wr
    except ImportError as error:
        raise RuntimeError(
            "wandb-workspaces is required. Run `uv sync` in models_handson."
        ) from error

    entity = wandb.Api().default_entity
    project = os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)
    registry_target_path = os.getenv(
        "WANDB_REGISTRY_TARGET_PATH",
        DEFAULT_REGISTRY_TARGET_PATH,
    )
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
        description="Summary of Runs, Tables, Artifacts, Sweeps, and Registry from chapters 1-5",
        width="readable",
        blocks=[
            wr.TableOfContents(),
            wr.H2(text="Experiment and model training progress"),
            wr.MarkdownBlock(
                text=(
                    "Compare chapter 1 simulated experiments with chapter 3 "
                    "Artifact-backed model training. Reusing metric names makes "
                    "it possible to overlay multiple Runs in one chart."
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
            wr.H2(text="Sweep parameter importance"),
            wr.PanelGrid(
                runsets=[sweep_runs],
                panels=[
                    wr.ParameterImportancePlot(with_respect_to="val/accuracy")
                ],
            ),
            wr.H2(text="Table・Artifacts・Registry"),
            wr.MarkdownBlock(
                text=(
                    f"- Inspect chapter 2 `examples/table` in the [Project Workspace]({project_url})\n"
                    f"- Inspect the Lineage of "
                    "`models-handson-dataset`, `models-handson-processed-dataset`, and "
                    f"`models-handson-model` in [Project Artifacts]({project_url}/artifacts)\n"
                    f"- Inspect the candidate Version in `{registry_target_path}` "
                    f"in [Registry]({registry_url})"
                )
            ),
            wr.H2(text="Example Reports"),
            wr.MarkdownBlock(
                text=(
                    "- [Nejumi LLM Leaderboard 4]"
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
    print("Review the draft, then select Publish to project in the W&B App.")


if __name__ == "__main__":
    main()
