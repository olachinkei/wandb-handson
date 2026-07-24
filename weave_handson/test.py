"""Weave ハンズオンの主要機能を一括で事前確認する。

このスクリプトは実際に OpenAI API を呼び出し、Weave にトレースと
アセットを記録します。マルチモーダル確認では PNG/JPG 画像だけを実行します。
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent
DEFAULT_PROJECT = "weave-handson"
REQUIRED_PACKAGES = {
    "agents": "openai-agents",
    "dotenv": "python-dotenv",
    "openai": "openai",
    "PIL": "pillow",
    "requests": "requests",
    "wandb": "wandb",
    "weave": "weave",
    "yaml": "pyyaml",
}
STEPS = [
    ("Basic Trace", Path("jp/1_1_basic_trace.py"), {}),
    ("Agent Integration", Path("jp/1_4_agent_integration.py"), {}),
    ("Assets and Scorers", Path("jp/2_1_assets.py"), {}),
    (
        "Multimodal Images (PNG/JPG only)",
        Path("jp/1_3_multimodal_openai.py"),
        {"WEAVE_MULTIMODAL_IMAGE_ONLY": "1"},
    ),
]


def check_dependencies() -> None:
    """必要なパッケージが現在の Python 環境に入っていることを確認する。"""
    missing = []
    for module_name, package_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(package_name)

    if missing:
        packages = " ".join(sorted(set(missing)))
        raise RuntimeError(
            "必要なパッケージが不足しています。\n"
            f"次を実行してください: uv add {packages}\n"
            "その後、uv run python test.py を再実行してください。"
        )


def load_environment() -> None:
    """プロジェクト直下の .env を現在のプロセスへ読み込む。"""
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY が未設定です。.env に設定してから再実行してください。"
        )


def resolve_weave_destination() -> tuple[str, str]:
    """W&B ログイン状態を確認し、Weave の保存先を返す。"""
    import wandb

    entity = os.getenv("WANDB_ENTITY") or wandb.Api(timeout=30).default_entity
    if not entity:
        raise RuntimeError(
            "W&B Entity を特定できません。wandb login を実行するか、"
            ".env に WANDB_ENTITY を設定してください。"
        )
    project = os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)
    return entity, project


def run_step(
    index: int,
    name: str,
    script: Path,
    extra_env: dict[str, str],
) -> None:
    """サンプルを独立した Python プロセスで実行する。"""
    script_path = ROOT / script
    if not script_path.exists():
        raise FileNotFoundError(f"サンプルが見つかりません: {script_path}")

    print("\n" + "=" * 72, flush=True)
    print(f"[{index}/{len(STEPS)}] {name}", flush=True)
    print(f"実行: {script}", flush=True)
    print("=" * 72, flush=True)

    env = os.environ.copy()
    env.update(extra_env)
    started_at = time.monotonic()
    try:
        subprocess.run(
            [sys.executable, str(script_path)],
            cwd=ROOT,
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"{name} の確認に失敗しました（終了コード: {exc.returncode}）。"
        ) from exc

    elapsed = time.monotonic() - started_at
    print(f"[OK] {name} ({elapsed:.1f}秒)", flush=True)


def main() -> None:
    os.chdir(ROOT)
    check_dependencies()
    load_environment()
    entity, project = resolve_weave_destination()

    print("Weave ハンズオン事前確認を開始します。")
    print(f"保存先: https://wandb.ai/{entity}/{project}")
    print("OpenAI API を実際に呼び出すため、利用料金が発生する場合があります。")

    for index, (name, script, extra_env) in enumerate(STEPS, start=1):
        run_step(index, name, script, extra_env)

    print("\n" + "=" * 72)
    print("ALL CHECKS PASSED")
    print(f"Weave UI: https://wandb.ai/{entity}/{project}")
    print("=" * 72)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n[FAILED] {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
