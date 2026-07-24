"""Run the core W&B Models hands-on workflow as a pre-course check.

This script executes the Japanese reference implementations in this order:

1. Experiment Tracking
2. Tables and Rich Media
3. Artifacts
4. Reports

The check creates real W&B Runs, Artifacts, and a draft Report in the selected
Entity and Project. It does not run Sweeps, Registry, or Extended Capabilities.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path
import runpy
import sys
import time


ROOT = Path(__file__).resolve().parent
DEFAULT_PROJECT = "wandb-models-handson"
REQUIRED_PACKAGES = ("numpy", "wandb", "wandb_workspaces")
STEPS = (
    ("Experiment Tracking", ROOT / "jp" / "1_experiment.py"),
    ("Tables and Rich Media", ROOT / "jp" / "2_table.py"),
    ("Artifacts", ROOT / "jp" / "3_artifacts.py"),
    ("Reports", ROOT / "jp" / "6_report.py"),
)


def check_dependencies() -> None:
    """Fail early when a package required by the workflow is unavailable."""
    missing: list[str] = []
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)

    if missing:
        names = ", ".join(missing)
        raise RuntimeError(
            f"Missing required packages: {names}\n"
            "Run `uv sync` in the models_handson directory and try again."
        )


def resolve_wandb_destination() -> tuple[str, str]:
    """Verify W&B authentication and return the resolved Entity and Project."""
    import wandb

    try:
        entity = wandb.Api(timeout=30).default_entity
    except Exception as error:
        raise RuntimeError(
            "Could not authenticate with W&B. Run `wandb login`, then try again."
        ) from error

    if not entity:
        raise RuntimeError(
            "W&B could not resolve a destination Entity. Set WANDB_ENTITY or "
            "log in with `wandb login`."
        )

    return entity, os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)


def run_step(index: int, name: str, script: Path) -> float:
    """Execute one chapter and return its elapsed time."""
    print(f"\n{'=' * 72}")
    print(f"[{index}/{len(STEPS)}] {name}")
    print(f"Script: {script.relative_to(ROOT)}")
    print("=" * 72)

    started_at = time.monotonic()
    try:
        runpy.run_path(str(script), run_name="__main__")
    except Exception as error:
        elapsed = time.monotonic() - started_at
        print(f"\nFAILED: {name} ({elapsed:.1f}s)", file=sys.stderr)
        print(
            "Fix the error shown above, then run `python test.py` again.",
            file=sys.stderr,
        )
        raise

    elapsed = time.monotonic() - started_at
    print(f"\nPASSED: {name} ({elapsed:.1f}s)")
    return elapsed


def main() -> None:
    os.chdir(ROOT)
    check_dependencies()
    entity, project = resolve_wandb_destination()

    print("W&B Models pre-course check")
    print(f"Python:  {sys.executable}")
    print(f"Entity:  {entity}")
    print(f"Project: {project}")
    print(f"URL:     https://wandb.ai/{entity}/{project}")
    print()
    print("This check creates real Runs, Artifacts, and a draft Report.")

    total_started_at = time.monotonic()
    timings = [
        (name, run_step(index, name, script))
        for index, (name, script) in enumerate(STEPS, start=1)
    ]
    total_elapsed = time.monotonic() - total_started_at

    print(f"\n{'=' * 72}")
    print("ALL CHECKS PASSED")
    print("=" * 72)
    for name, elapsed in timings:
        print(f"- {name}: {elapsed:.1f}s")
    print(f"Total: {total_elapsed:.1f}s")
    print(f"Project: https://wandb.ai/{entity}/{project}")
    print("Open the Project and confirm the Runs, Tables, Artifacts, and draft Report.")


if __name__ == "__main__":
    main()
