"""
7: Extended Capabilities - W&B SDKの拡張機能

環境構築（models_handson ディレクトリで実行）:
    uv sync

実行例:
    python 7_extended_capabilities.py
    python 7_extended_capabilities.py --demo query --run-id <RUN_ID>
    python 7_extended_capabilities.py --demo charts
    python 7_extended_capabilities.py --demo offline
    python 7_extended_capabilities.py --demo alert --enable-alert

--demo の選択肢:
- resume: 中断したRunへ同じRun IDで追記（既定）
- query: Public APIで指定Runの必要な履歴だけを取得
- charts: PR CurveとAudioを記録
- offline: Offline Runを作成し、syncコマンドを表示
- alert: 明示的な--enable-alert指定時だけ通知を送信
- settings: よく使う環境変数とSettingsを表示
- all: alert以外のデモを順番に実行
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import wandb


DEFAULT_PROJECT = "wandb-models-handson"


def get_wandb_target() -> tuple[str, str]:
    entity = os.getenv("WANDB_ENTITY")
    if not entity:
        raise RuntimeError(
            "WANDB_ENTITY が未設定です。W&B の Team Entity を設定してください。"
        )
    return entity, os.getenv("WANDB_PROJECT", DEFAULT_PROJECT)


def demo_resume(entity: str, project: str) -> str:
    """5 step記録したRunを終了し、同じRun IDへさらに5 step追記する。"""
    run_id = wandb.util.generate_id()
    with wandb.init(
        entity=entity,
        project=project,
        id=run_id,
        name="extended-resume-demo",
        resume="allow",
        job_type="extended-resume",
        tags=["handson", "extended", "resume"],
    ) as run:
        for step in range(5):
            run.log({"resume/value": step, "resume/squared": step**2})

    with wandb.init(
        entity=entity,
        project=project,
        id=run_id,
        resume="must",
    ) as resumed_run:
        for step in range(5, 10):
            resumed_run.log({"resume/value": step, "resume/squared": step**2})
        print(f"Resumed run: {resumed_run.url}")

    return run_id


def demo_query(entity: str, project: str, run_id: str) -> None:
    """明示した2メトリクスだけを取得し、巨大な履歴の全列取得を避ける。"""
    api = wandb.Api(timeout=60)
    run = api.run(f"{entity}/{project}/{run_id}")
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


def demo_charts_and_audio(entity: str, project: str) -> None:
    rng = np.random.default_rng(7)
    ground_truth = rng.integers(0, 3, size=80)
    predictions = rng.random((80, 3))
    predictions /= predictions.sum(axis=1, keepdims=True)

    sample_rate = 8_000
    seconds = 1
    time_axis = np.linspace(0, seconds, sample_rate * seconds, endpoint=False)
    waveform = 0.25 * np.sin(2 * np.pi * 440 * time_axis)

    with wandb.init(
        entity=entity,
        project=project,
        name="extended-charts-and-audio",
        job_type="extended-media",
        tags=["handson", "extended", "media"],
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


def demo_offline(entity: str, project: str) -> None:
    offline_root = Path(os.getenv("WANDB_DIR", Path.cwd() / "wandb_offline"))
    offline_root.mkdir(parents=True, exist_ok=True)

    with wandb.init(
        entity=entity,
        project=project,
        name="extended-offline-demo",
        job_type="extended-offline",
        mode="offline",
        dir=str(offline_root),
        tags=["handson", "extended", "offline"],
    ) as run:
        for step in range(5):
            run.log({"offline/value": step})
        run_directory = Path(run.dir).parent

    print(f"Offline run saved: {run_directory}")
    print(f"Onlineへ送信するには実行: wandb sync {run_directory}")


def demo_alert(entity: str, project: str, enabled: bool) -> None:
    if not enabled:
        raise RuntimeError(
            "Alertは外部通知を送ります。実行する場合だけ--enable-alertを追加してください。"
        )
    with wandb.init(
        entity=entity,
        project=project,
        name="extended-alert-demo",
        job_type="extended-alert",
        tags=["handson", "extended", "alert"],
    ) as run:
        run.alert(
            title="W&B Models hands-on alert",
            text="7_extended_capabilities.py から送信したテスト通知です。",
        )
        print(f"Alert sent from: {run.url}")


def demo_settings(entity: str, project: str) -> None:
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
    parser.add_argument("--run-id", help="queryで取得するRun ID")
    parser.add_argument(
        "--enable-alert",
        action="store_true",
        help="alertデモの外部通知を明示的に許可する",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    entity, project = get_wandb_target()

    if args.demo == "resume":
        demo_resume(entity, project)
    elif args.demo == "query":
        if not args.run_id:
            raise RuntimeError("--demo query には--run-idが必要です。")
        demo_query(entity, project, args.run_id)
    elif args.demo == "charts":
        demo_charts_and_audio(entity, project)
    elif args.demo == "offline":
        demo_offline(entity, project)
    elif args.demo == "alert":
        demo_alert(entity, project, args.enable_alert)
    elif args.demo == "settings":
        demo_settings(entity, project)
    else:
        run_id = demo_resume(entity, project)
        demo_query(entity, project, run_id)
        demo_charts_and_audio(entity, project)
        demo_offline(entity, project)
        demo_settings(entity, project)


if __name__ == "__main__":
    main()
