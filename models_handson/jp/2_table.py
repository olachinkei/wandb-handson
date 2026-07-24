"""
2: Tables and Rich Media - Table とリッチメディア

環境構築（models_handson ディレクトリで実行）:
    uv sync

このスクリプトでは、外部データをダウンロードせずに小さな画像とマスクを生成し、
wandb.Image、セグメンテーションマスク、wandb.Table、時系列 Table を記録します。
"""

from __future__ import annotations

import os

import numpy as np
import wandb


DEFAULT_PROJECT = "wandb-models-handson"
CLASS_LABELS = {0: "background", 1: "foreground"}


def get_wandb_target() -> tuple[str, str]:
    entity = os.getenv("WANDB_ENTITY")
    if not entity:
        raise RuntimeError(
            "WANDB_ENTITY が未設定です。W&B の Team Entity を設定してください。"
        )
    return entity, os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)


def make_example(index: int, size: int = 64) -> tuple[np.ndarray, np.ndarray]:
    """色付きの四角形と、その領域を示す整数マスクを生成する。"""
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
    entity, project = get_wandb_target()

    with wandb.init(
        entity=entity,
        project=project,
        name="table-and-rich-media",
        job_type="table",
        tags=["handson", "table", "rich-media"],
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

        # 同じキーへ複数回 Table を記録すると、UI で step ごとに比較できる。
        for step in range(3):
            run.log({"examples/progression": build_table(step=step)}, step=step + 1)

        print(f"Created: {run.url}")

    print("W&B UI の Workspace で examples/table と examples/progression を確認してください。")


if __name__ == "__main__":
    main()
