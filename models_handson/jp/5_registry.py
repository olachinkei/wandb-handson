"""
5: Registry - 組織で利用するArtifactのキュレーション

環境構築（models_handson ディレクトリで実行）:
    uv sync

Registry は、Projectで作成したArtifact Versionを組織全体で管理するための
中央リポジトリです。「Link」は元Artifactへの参照を作る操作であり、ファイルを
複製する操作ではありません。

GUIでの基本手順:
1. https://wandb.ai/registry/ を開く。
2. 既存Registryを選ぶか、Create registryで名前、Visibility、Artifact typeを設定する。
3. Create collectionでCollection名と受け入れるArtifact typeを設定する。
4. Link versionからProject、Artifact、Versionを選んでリンクする。
5. 必要に応じてAlias、Tags、Collection card、Registry accessを設定する。
6. VersionのLineageタブとCollectionのAction Historyで系譜・監査履歴を確認する。

このプログラム例:
- 3_artifacts.py が作成した models-handson-model:latest を取得
- Registry Collectionへcandidate Alias付きでリンク
- CollectionへTagsと説明を付与
- Registry経由でArtifactを再取得して一時ディレクトリへダウンロード

主な公式ドキュメント:
- Overview: https://docs.wandb.ai/models/registry
- Create registry: https://docs.wandb.ai/models/registry/create_registry
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
DEFAULT_REGISTRY = "Models"
DEFAULT_COLLECTION = "models-handson-model"
MODEL_ARTIFACT = "models-handson-model"


def get_wandb_settings() -> tuple[str, str, str, str]:
    entity = os.getenv("WANDB_ENTITY")
    if not entity:
        raise RuntimeError(
            "WANDB_ENTITY が未設定です。RegistryへアクセスできるTeam Entityを設定してください。"
        )
    return (
        entity,
        os.getenv("WANDB_PROJECT", DEFAULT_PROJECT),
        os.getenv("WANDB_REGISTRY", DEFAULT_REGISTRY),
        os.getenv("WANDB_REGISTRY_COLLECTION", DEFAULT_COLLECTION),
    )


def create_registry_example(api: wandb.Api, registry_name: str) -> None:
    """権限を持つ管理者が新規Registryを作る場合の任意例。main()からは呼ばない。"""
    api.create_registry(
        name=registry_name,
        visibility="organization",
        description="W&B Models ハンズオン用Registry",
        artifact_types=["model"],
    )


def main() -> None:
    entity, project, registry_name, collection_name = get_wandb_settings()
    source_artifact_name = f"{entity}/{project}/{MODEL_ARTIFACT}:latest"
    target_path = f"wandb-registry-{registry_name}/{collection_name}"

    # Team Entityを明示すると、複数Organizationへ所属している場合も解決先が明確になる。
    api = wandb.Api(timeout=60, overrides={"entity": entity})
    source_artifact = api.artifact(source_artifact_name)

    with wandb.init(
        entity=entity,
        project=project,
        name="registry-promotion",
        job_type="registry-promotion",
        tags=["handson", "registry"],
    ) as run:
        linked_artifact = run.link_artifact(
            artifact=source_artifact,
            target_path=target_path,
            aliases=["candidate"],
        )
        print(f"Linked: {source_artifact_name} -> {target_path}")
        print(f"Registry artifact: {linked_artifact.name}")

    collection = api.artifact_collection(type_name="model", name=target_path)
    existing_tags = collection.tags or []
    collection.tags = sorted(set([*existing_tags, "handson", "classification"]))
    collection.description = (
        "W&B Modelsハンズオンで作成した軽量モデル。"
        "candidate Aliasは評価・昇格候補を示します。"
    )
    collection.save()

    registry_artifact_name = f"{target_path}:candidate"
    registry_artifact = api.artifact(registry_artifact_name)
    with tempfile.TemporaryDirectory(prefix="wandb-registry-download-") as temp_dir:
        download_path = Path(registry_artifact.download(root=temp_dir))
        files = sorted(path.name for path in download_path.rglob("*") if path.is_file())
        print(f"Downloaded from Registry: {registry_artifact_name}")
        print(f"Files: {files}")

    print("Registry UIでAlias、Tags、Collection card、Lineageを確認してください。")


if __name__ == "__main__":
    main()
