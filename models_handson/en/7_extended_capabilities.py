"""
7: Extended W&B SDK Capabilities

Setup (run from the models_handson directory):
    uv sync

Examples:
    python 7_extended_capabilities.py
    python 7_extended_capabilities.py --demo query --run-id <RUN_ID>
    python 7_extended_capabilities.py --demo charts
    python 7_extended_capabilities.py --demo offline
    python 7_extended_capabilities.py --demo alert --enable-alert

--demo choices:
- resume: append to an interrupted Run using the same Run ID (default)
- query: retrieve only selected history fields through the Public API
- charts: log a PR Curve and Audio
- offline: create an Offline Run and print its sync command
- alert: send a notification only when --enable-alert is explicitly supplied
- settings: display commonly used environment variables and Settings
- all: run every demo except alert
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import wandb


DEFAULT_PROJECT = "wandb-models-handson"


def demo_resume(project: str) -> str:
    """Finish a five-step Run, then append five steps using the same Run ID."""
    run_id = wandb.util.generate_id()
    with wandb.init(
        project=project,
        id=run_id,
        name="extended-resume-demo",
        resume="allow",
        job_type="extended-resume",
        tags=["extended", "resume"],
    ) as run:
        for step in range(5):
            run.log({"resume/value": step, "resume/squared": step**2})

    with wandb.init(
        project=project,
        id=run_id,
        resume="must",
    ) as resumed_run:
        for step in range(5, 10):
            resumed_run.log({"resume/value": step, "resume/squared": step**2})
        print(f"Resumed run: {resumed_run.url}")

    return run_id


def demo_query(project: str, run_id: str) -> None:
    """Fetch only two metrics instead of downloading every history column."""
    api = wandb.Api(timeout=60)
    run = api.run(f"{api.default_entity}/{project}/{run_id}")
    rows = list(
        run.scan_history(
            keys=["resume/value", "resume/squared"],
            page_size=100,
        )
    )
    print(f"Run: {run.name} ({run.state}), rows={len(rows)}")
    for row in rows[:10]:
        print(
            f"step={row.get('_step')}, value={row.get('resume/value')}, "
            f"squared={row.get('resume/squared')}"
        )


def demo_charts_and_audio(project: str) -> None:
    rng = np.random.default_rng(7)
    ground_truth = rng.integers(0, 3, size=80)
    predictions = rng.random((80, 3))
    predictions /= predictions.sum(axis=1, keepdims=True)

    sample_rate = 8_000
    seconds = 1
    time_axis = np.linspace(0, seconds, sample_rate * seconds, endpoint=False)
    waveform = 0.25 * np.sin(2 * np.pi * 440 * time_axis)

    with wandb.init(
        project=project,
        name="extended-charts-and-audio",
        job_type="extended-media",
        tags=["extended", "media"],
    ) as run:
        run.log(
            {
                "charts/pr_curve": wandb.plot.pr_curve(
                    ground_truth,
                    predictions,
                    labels=["class-0", "class-1", "class-2"],
                ),
                "media/audio": wandb.Audio(
                    waveform,
                    sample_rate=sample_rate,
                    caption="440Hz sine wave",
                ),
            }
        )
        print(f"Created: {run.url}")


def demo_offline(project: str) -> None:
    offline_root = Path(os.getenv("WANDB_DIR", Path.cwd() / "wandb_offline"))
    offline_root.mkdir(parents=True, exist_ok=True)

    with wandb.init(
        project=project,
        name="extended-offline-demo",
        job_type="extended-offline",
        mode="offline",
        dir=str(offline_root),
        tags=["extended", "offline"],
    ) as run:
        for step in range(5):
            run.log({"offline/value": step})
        run_directory = Path(run.dir).parent

    print(f"Offline run saved: {run_directory}")
    print(f"To upload this Run, execute: wandb sync {run_directory}")


def demo_alert(project: str, enabled: bool) -> None:
    if not enabled:
        raise RuntimeError(
            "Alerts send external notifications. Add --enable-alert only when "
            "you intend to send one."
        )
    with wandb.init(
        project=project,
        name="extended-alert-demo",
        job_type="extended-alert",
        tags=["extended", "alert"],
    ) as run:
        run.alert(
            title="W&B Models hands-on alert",
            text="Test notification sent from 7_extended_capabilities.py.",
        )
        print(f"Alert sent from: {run.url}")


def demo_settings(project: str) -> None:
    entity = wandb.Api().default_entity
    print("Current safe settings:")
    print(f"  WANDB_ENTITY={entity}")
    print(f"  WANDB_PROJECT={project}")
    print(f"  WANDB_BASE_URL={os.getenv('WANDB_BASE_URL', '(W&B Cloud)')}")
    print(f"  WANDB_API_KEY configured={bool(os.getenv('WANDB_API_KEY'))}")
    print("\nOther useful variables: WANDB_DIR, WANDB_CACHE_DIR, WANDB_DATA_DIR")
    print("Per-run settings example: wandb.Settings(save_code=False, console='off')")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--demo",
        choices=["resume", "query", "charts", "offline", "alert", "settings", "all"],
        default="resume",
    )
    parser.add_argument("--run-id", help="Run ID to retrieve with the query demo")
    parser.add_argument(
        "--enable-alert",
        action="store_true",
        help="explicitly allow the alert demo to send an external notification",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project = os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)

    if args.demo == "resume":
        demo_resume(project)
    elif args.demo == "query":
        if not args.run_id:
            raise RuntimeError("--demo query requires --run-id.")
        demo_query(project, args.run_id)
    elif args.demo == "charts":
        demo_charts_and_audio(project)
    elif args.demo == "offline":
        demo_offline(project)
    elif args.demo == "alert":
        demo_alert(project, args.enable_alert)
    elif args.demo == "settings":
        demo_settings(project)
    else:
        run_id = demo_resume(project)
        demo_query(project, run_id)
        demo_charts_and_audio(project)
        demo_offline(project)
        demo_settings(project)


if __name__ == "__main__":
    main()
