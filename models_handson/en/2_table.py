"""
2: Tables and Rich Media

Setup (run from the models_handson directory):
    uv sync

This script generates small images and masks without downloading external data,
then logs wandb.Image objects, segmentation masks, wandb.Table objects, and
Tables over time.
"""

from __future__ import annotations

import os

import numpy as np
import wandb


DEFAULT_PROJECT = "wandb-models-handson"
CLASS_LABELS = {0: "background", 1: "foreground"}


def make_example(index: int, size: int = 64) -> tuple[np.ndarray, np.ndarray]:
    """Generate a colored square and an integer mask covering its area."""
    rng = np.random.default_rng(2_000 + index)
    image = rng.integers(15, 70, size=(size, size, 3), dtype=np.uint8)
    mask = np.zeros((size, size), dtype=np.uint8)

    width = 15 + index % 4 * 3
    x0 = 5 + (index * 7) % (size - width - 5)
    y0 = 6 + (index * 9) % (size - width - 6)
    mask[y0 : y0 + width, x0 : x0 + width] = 1

    color = np.array(
        [80 + (index * 35) % 170, 210 - (index * 20) % 130, 140],
        dtype=np.uint8,
    )
    image[mask == 1] = color
    return image, mask


def masked_image(image: np.ndarray, mask: np.ndarray, caption: str) -> wandb.Image:
    return wandb.Image(
        image,
        caption=caption,
        masks={
            "prediction": {
                "mask_data": mask,
                "class_labels": CLASS_LABELS,
            }
        },
    )


def build_table(step: int, rows: int = 4) -> wandb.Table:
    table = wandb.Table(columns=["id", "original", "segmentation"])
    for row_index in range(rows):
        example_id = step * rows + row_index
        image, mask = make_example(example_id)
        table.add_data(
            example_id,
            wandb.Image(image, caption=f"sample-{example_id}"),
            masked_image(image, mask, caption=f"mask-{example_id}"),
        )
    return table


def main() -> None:
    project = os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)

    with wandb.init(
        project=project,
        name="table-and-rich-media",
        job_type="table",
        tags=["table", "rich-media"],
    ) as run:
        image, mask = make_example(0)
        run.log(
            {
                "examples/single_image": wandb.Image(image, caption="generated input"),
                "examples/single_mask": masked_image(
                    image,
                    mask,
                    caption="generated segmentation",
                ),
                "examples/table": build_table(step=0, rows=6),
            }
        )

        # Logging Tables repeatedly under one key enables step-by-step comparison.
        for step in range(3):
            run.log({"examples/progression": build_table(step=step)}, step=step + 1)

        print(f"Created: {run.url}")

    print("Open the W&B Workspace and inspect examples/table and examples/progression.")


if __name__ == "__main__":
    main()
