"""
5: Registry - Curating Artifacts for Organization-Wide Use

Setup (run from the models_handson directory):
    uv sync

Registry is a central repository for managing Artifact Versions created in
Projects across an organization. Linking creates a reference to the original
Artifact; it does not duplicate its files.

Required preparation:
1. Open https://wandb.ai/registry/.
2. Select the `models_handson` Registry. Create it in the UI if needed.
3. Select Create collection, set its name to `handson`, and its Artifact type
   to `model`.
4. Confirm the Target path is `wandb-registry-models_handson/handson`.

This script does not create Collections. Create the Collection manually first:
https://docs.wandb.ai/models/registry/create_collection#python-sdk-beta

After running:
1. Configure Aliases, Tags, the Collection card, and Registry access as needed.
2. Inspect the Version's Lineage and the Collection's Action History.

This example:
- Retrieves models-handson-model:latest created by 3_artifacts.py
- Verifies that the pre-created Collection exists
- Links the Artifact to the Collection with the candidate Alias
- Adds Tags and a description to the Collection
- Downloads the Artifact through Registry into a temporary directory

Target path:
- Default: wandb-registry-models_handson/handson
- To change it: set the WANDB_REGISTRY_TARGET_PATH environment variable

Official documentation:
- Overview: https://docs.wandb.ai/models/registry
- Create registry: https://docs.wandb.ai/models/registry/create_registry
- Create collection: https://docs.wandb.ai/models/registry/create_collection#python-sdk-beta
- Link version: https://docs.wandb.ai/models/registry/link_version
- Aliases: https://docs.wandb.ai/models/registry/aliases
- Download: https://docs.wandb.ai/models/registry/download_use_artifact
- Tags: https://docs.wandb.ai/models/registry/organize-with-tags
- Cards: https://docs.wandb.ai/models/registry/registry_cards
- Lineage: https://docs.wandb.ai/models/registry/lineage
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile

import wandb


DEFAULT_PROJECT = "wandb-models-handson"
DEFAULT_TARGET_PATH = "wandb-registry-models_handson/handson"
MODEL_ARTIFACT = "models-handson-model"
CREATE_COLLECTION_DOCS = (
    "https://docs.wandb.ai/models/registry/create_collection#python-sdk-beta"
)


def get_target_path() -> str:
    target_path = os.getenv("WANDB_REGISTRY_TARGET_PATH", DEFAULT_TARGET_PATH)
    if not target_path.startswith("wandb-registry-") or target_path.count("/") != 1:
        raise ValueError(
            "WANDB_REGISTRY_TARGET_PATH must use the format "
            "`wandb-registry-<registry>/<collection>`."
        )
    return target_path


def main() -> None:
    project = os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)
    target_path = get_target_path()

    api = wandb.Api(timeout=60)
    entity = api.default_entity
    source_artifact_name = f"{entity}/{project}/{MODEL_ARTIFACT}:latest"

    if not api.artifact_collection_exists(name=target_path, type="model"):
        raise RuntimeError(
            f"The pre-created Model Collection `{target_path}` was not found.\n"
            "Open the Registry in the W&B App, manually create a Collection "
            "with Artifact type `model`, and run this script again.\n"
            f"Instructions: {CREATE_COLLECTION_DOCS}"
        )
    collection = api.artifact_collection(type_name="model", name=target_path)

    source_artifact = api.artifact(source_artifact_name)

    with wandb.init(
        project=project,
        name="registry-promotion",
        job_type="registry-promotion",
        tags=["registry"],
    ) as run:
        linked_artifact = run.link_artifact(
            artifact=source_artifact,
            target_path=target_path,
            aliases=["candidate"],
        )
        print(f"Linked: {source_artifact_name} -> {target_path}")
        print(f"Registry artifact: {linked_artifact.name}")

    existing_tags = collection.tags or []
    collection.tags = sorted(
        {
            *(tag for tag in existing_tags if tag != "handson"),
            "classification",
        }
    )
    collection.description = (
        "Lightweight model created in the W&B Models hands-on. "
        "The candidate Alias marks a version for evaluation or promotion."
    )
    collection.save()

    registry_artifact_name = f"{target_path}:candidate"
    registry_artifact = api.artifact(registry_artifact_name)
    with tempfile.TemporaryDirectory(prefix="wandb-registry-download-") as temp_dir:
        download_path = Path(registry_artifact.download(root=temp_dir))
        files = sorted(path.name for path in download_path.rglob("*") if path.is_file())
        print(f"Downloaded from Registry: {registry_artifact_name}")
        print(f"Files: {files}")

    print("Open Registry and inspect the Alias, Tags, Collection card, and Lineage.")


if __name__ == "__main__":
    main()
