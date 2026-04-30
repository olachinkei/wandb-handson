"""
===========================================
ART-E Email Search Agent - メインモジュール
===========================================

このモジュールには以下が含まれます：
- モデルの初期化
- Rollout（エージェント実行）関数
- RULER評価関数
- トレーニングループ

使い方:
    # トレーニング（Serverless Backend）
    python art_e.py

    # ローカル GPU を使用
    python art_e.py --local
"""

import argparse
import asyncio
import json
import logging
import random
from dataclasses import asdict
from textwrap import dedent

import art
import weave
from art.rewards.ruler import ruler_score_group
from art.serverless.backend import ServerlessBackend
from art.utils import iterate_dataset
from art.utils.strip_logprobs import strip_logprobs
from dotenv import load_dotenv
from langchain_core.utils.function_calling import convert_to_openai_tool
from litellm import acompletion
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

# ローカルモジュール
from config import Config, get_config
from utils import (
    FinalAnswer,
    Scenario,
    load_scenarios,
    read_email,
    search_emails,
)

# ===========================================
# 環境変数の読み込み
# ===========================================
load_dotenv()

# Weaveのログレベルを抑制（検証エラーの抑制）
logging.getLogger("weave").setLevel(logging.CRITICAL)


# ===========================================
# RULER評価用モデル
# ===========================================

class CorrectnessJudgeResponse(BaseModel):
    """
    回答の正確性を判定するLLMジャッジの応答モデル
    
    Attributes:
        reasoning: 判断の理由説明
        accept: 回答を受け入れるかどうか
    """
    reasoning: str = Field(description="判断プロセスの説明")
    accept: bool = Field(description="AI回答を受け入れるかどうか")


# ===========================================
# Trajectory（軌跡）クラス
# ===========================================

class ProjectTrajectory(art.Trajectory):
    """
    プロジェクト固有のTrajectoryクラス
    
    ARTのTrajectoryを拡張し、最終回答を保持できるようにしています。
    
    Attributes:
        final_answer: エージェントが返した最終回答（オプション）
    """
    final_answer: FinalAnswer | None = None


class EmailScenario(BaseModel):
    """
    メールシナリオのラッパーモデル
    
    Attributes:
        step: 現在のステップ番号
        scenario: シナリオデータ
    """
    step: int
    scenario: Scenario


# ===========================================
# グローバル設定（トレーニング中に参照）
# ===========================================
_config: Config = None


def get_current_config() -> Config:
    """現在の設定を取得"""
    global _config
    if _config is None:
        _config = get_config()
    return _config


def set_config(config: Config):
    """設定をセット"""
    global _config
    _config = config


# ===========================================
# RULER評価関数
# ===========================================

@weave.op  # Weaveでトレースを記録
@retry(stop=stop_after_attempt(3))
async def judge_correctness(
    scenario: Scenario, answer: str
) -> CorrectnessJudgeResponse:
    """
    LLMジャッジを使用して回答の正確性を評価
    
    RULER手法の一部として、エージェントの回答が参照回答と一致するかを判定します。
    
    Args:
        scenario: 評価対象のシナリオ
        answer: エージェントが生成した回答
    
    Returns:
        CorrectnessJudgeResponse: 判定結果（reasoning と accept）
    """
    config = get_current_config()
    
    system_prompt = dedent(
        """
        あなたには質問、参照回答（**Reference answer**）、AIアシスタントが生成した回答（**AI answer**）が与えられます。

        あなたのタスクは、AI回答が正しいかどうかを判断することです。AI回答に参照回答からの関連情報が含まれている場合、その回答を受け入れてください。質問に関連する情報が欠けている場合、または参照回答と矛盾する場合は、回答を受け入れないでください。
        """
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"Question: {scenario.question}\n"
                f"Reference answer: {scenario.answer}\n"
                f"AI answer: {answer}"
            ),
        },
    ]

    # 設定から正確性判定モデルを取得
    response = await acompletion(
        model=config.ruler.correctness_judge_model,
        messages=messages,
        response_format=CorrectnessJudgeResponse,
    )

    first_choice = response.choices[0]
    raw_content = first_choice.message.content or "{}"

    try:
        return CorrectnessJudgeResponse.model_validate_json(raw_content)
    except Exception as e:
        return CorrectnessJudgeResponse(
            reasoning=f"パースエラー: {e}\n生データ: {raw_content}", accept=False
        )


# ===========================================
# Rollout関数
# ===========================================

@weave.op
async def rollout(model: art.Model, email_scenario: EmailScenario) -> ProjectTrajectory:
    """
    エージェントのロールアウト（1エピソードの実行）
    
    この関数は以下の処理を行います：
    1. エージェントにメール検索シナリオを提示
    2. エージェントがツールを使用してメールを検索
    3. 最終回答を生成
    4. RULER評価で正確性をスコアリング
    
    Args:
        model: 使用するARTモデル
        email_scenario: 実行するシナリオ
    
    Returns:
        ProjectTrajectory: 実行軌跡（メッセージ履歴、報酬、メトリクス含む）
    """
    config = get_current_config()
    scenario = email_scenario.scenario
    max_turns = config.training.max_turns

    # Trajectoryの初期化
    traj = ProjectTrajectory(
        reward=0.0,
        messages_and_choices=[],
        metadata={
            "scenario_id": scenario.id,
            "step": email_scenario.step,
        },
    )

    # ===========================================
    # システムプロンプト設定
    # ===========================================
    system_prompt = dedent(
        f"""
        あなたはメール検索エージェントです。ユーザーのクエリと、ユーザーのメールを検索するためのツールが与えられます。ツールを使用してユーザーのメールを検索し、クエリへの回答を見つけてください。回答を見つけるために最大{max_turns}ターンまで使用できるので、最初の検索で回答が見つからない場合は、異なるキーワードで再試行できます。

        ユーザーのメールアドレス: {scenario.inbox_address}
        今日の日付: {scenario.query_date}
        """
    )

    traj.messages_and_choices = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": scenario.question},
    ]

    # ===========================================
    # ツール定義
    # ===========================================
    
    def search_inbox(keywords: list[str]) -> list[dict]:
        """
        キーワードでメールボックスを検索
        
        Args:
            keywords: 検索キーワードのリスト
        
        Returns:
            list[dict]: 検索結果の辞書リスト
        """
        results = search_emails(
            inbox=scenario.inbox_address,
            keywords=keywords,
            sent_before=scenario.query_date,
        )
        return [asdict(result) for result in results]

    def return_final_answer(
        answer: str, reference_message_ids: list[str]
    ) -> FinalAnswer:
        """
        最終回答と参照メールIDを返す
        
        Args:
            answer: 回答テキスト
            reference_message_ids: 回答生成に使用したメールID
        
        Returns:
            FinalAnswer: 最終回答オブジェクト
        """
        return FinalAnswer(answer=answer, source_ids=reference_message_ids)

    # ツールリストとマッピング
    tools = [search_inbox, read_email, return_final_answer]
    tools_by_name = {t.__name__: t for t in tools}
    traj.tools = [convert_to_openai_tool(t) for t in tools]

    # ===========================================
    # OpenAIクライアント設定
    # ===========================================
    client = AsyncOpenAI(
        base_url=model.inference_base_url,
        api_key=model.inference_api_key,
    )

    # ===========================================
    # エージェントループ
    # ===========================================
    for _ in range(max_turns):
        # モデルからの応答を取得
        response = await client.chat.completions.create(
            model=model.get_inference_name(),
            temperature=1,
            messages=traj.messages(),
            tools=traj.tools,
        )

        response_message = response.choices[0].message
        traj.messages_and_choices.append(response.choices[0])

        # ツール呼び出しがなければ終了
        if not response_message.tool_calls:
            return traj

        try:
            # 各ツール呼び出しを実行
            for tool_call in response_message.tool_calls:
                tool_name: str = tool_call.function.name
                if tool_name in tools_by_name:
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_to_call = tools_by_name[tool_name]
                    result = tool_to_call(**tool_args)
                    
                    # ツール結果をメッセージに追加
                    traj.messages_and_choices.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": str(result),
                        }
                    )

                    # 最終回答の場合はスコアリング
                    if tool_name == "return_final_answer":
                        traj.final_answer = result
                        if traj.final_answer:
                            # RULER評価を実行
                            correctness_judge_response = await judge_correctness(
                                scenario, traj.final_answer.answer
                            )
                            traj.metrics["correct"] = float(
                                correctness_judge_response.accept
                            )
                        return traj
        except Exception as e:
            print(f"ツール呼び出しエラー: {e}")
            return traj

    return traj


# ===========================================
# モデル初期化関数
# ===========================================

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=10, max=120),
    reraise=True,
)
async def _register_model_with_retry(model: art.TrainableModel, backend: ServerlessBackend):
    """
    リトライ付きでモデルを登録
    
    W&Bサーバーがタイムアウトすることがあるため、
    最大5回、指数バックオフでリトライします。
    """
    print("  モデルをバックエンドに登録中...")
    await model.register(backend)
    print("  ✅ モデル登録完了")


async def initialize_model(config: Config) -> art.TrainableModel:
    """
    ARTモデルを初期化してバックエンドに登録

    Args:
        config: 設定オブジェクト

    Returns:
        art.TrainableModel: 初期化済みのモデル
    """
    # 再現性のためのシード設定
    if config.dataset.seed is not None:
        random.seed(config.dataset.seed)

    # モデルの宣言
    internal_config = None
    if config.backend.use_local:
        internal_config = {"engine_args": {"gpu_memory_utilization": 0.7}}
    model = art.TrainableModel(
        name=config.model.name,
        project=config.model.project_name,
        entity=config.model.entity,
        base_model=config.model.base_model,
        _internal_config=internal_config,
    )

    # バックエンドの初期化
    if config.backend.use_local:
        from art.local import LocalBackend
        print(f"  LocalBackend を使用（パス: {config.backend.local_path}）")
        backend = LocalBackend(path=config.backend.local_path)
    else:
        print("  ServerlessBackend を使用（CoreWeave GPU）")
        backend = ServerlessBackend()

    # モデルをバックエンドに登録（リトライ付き）
    try:
        await _register_model_with_retry(model, backend)
    except Exception as e:
        print(f"\n❌ モデル登録に失敗しました: {e}")
        print("\n💡 対処法:")
        print("  1. 数分待って再実行")
        print("  2. Google Colabで実行")
        print("  3. W&Bステータス確認: https://status.wandb.ai/")
        raise

    return model


# ===========================================
# トレーニングループ
# ===========================================

async def train(config: Config):
    """
    トレーニングループを実行
    
    GRPOとRULERを使用してエージェントをトレーニングします。
    
    処理の流れ:
    1. 各ステップで複数のシナリオに対してロールアウトを実行
    2. RULERで各軌跡に相対スコアを付与
    3. GRPOでモデルを更新
    4. 定期的にバリデーションを実行
    
    Args:
        config: 設定オブジェクト
    """
    # ===========================================
    # 設定をグローバルにセット（rollout関数から参照）
    # ===========================================
    set_config(config)
    
    # ===========================================
    # Weaveの初期化
    # ===========================================
    weave.init(
        config.model.project,
        settings={"print_call_link": False},
        global_postprocess_output=strip_logprobs
    )
    
    # ===========================================
    # モデル初期化
    # ===========================================
    print("=" * 60)
    print("ART-E Email Search Agent - トレーニング開始")
    print("=" * 60)
    print()
    print("【設定】")
    print(f"  プロジェクト: {config.model.project}")
    print(f"  モデル名: {config.model.name}")
    print(f"  ベースモデル: {config.model.base_model}")
    print()
    print("【トレーニングパラメータ】")
    print(f"  groups_per_step: {config.training.groups_per_step}")
    print(f"  rollouts_per_group: {config.training.rollouts_per_group}")
    print(f"  num_epochs: {config.training.num_epochs}")
    print(f"  learning_rate: {config.training.learning_rate}")
    print(f"  max_steps: {config.training.max_steps}")
    print(f"  validation_step_interval: {config.training.validation_step_interval}")
    print()
    print("【データセット】")
    print(f"  トレーニングシナリオ数: {config.dataset.train_limit}")
    print(f"  バリデーションシナリオ数: {config.dataset.val_limit}")
    print()
    
    model = await initialize_model(config)
    
    # ===========================================
    # シナリオの読み込み
    # ===========================================
    print("シナリオを読み込み中...")
    training_scenarios = load_scenarios(
        split="train",
        limit=config.dataset.train_limit,
        max_messages=config.dataset.max_messages,
        shuffle=config.dataset.shuffle,
        seed=config.dataset.seed,
    )
    
    validation_scenarios = load_scenarios(
        split="test",
        limit=config.dataset.val_limit,
        max_messages=config.dataset.max_messages,
        shuffle=config.dataset.shuffle,
        seed=config.dataset.seed,
    )
    
    print(f"トレーニングシナリオ: {len(training_scenarios)} 件")
    print(f"バリデーションシナリオ: {len(validation_scenarios)} 件")
    print()
    
    # ===========================================
    # トレーニングイテレータの設定
    # ===========================================
    current_step = await model.get_step()
    if current_step >= config.training.max_steps:
        print(f"⚠️ モデルは既にステップ {current_step} まで学習済みです（max_steps={config.training.max_steps}）")
        print(f"   続きからトレーニングするには --max-steps {current_step + config.training.max_steps} を指定してください")
        print(f"   新規にトレーニングするにはモデル名を変更してください（config.py の ModelConfig.name）")
        return

    training_iterator = iterate_dataset(
        training_scenarios,
        groups_per_step=config.training.groups_per_step,
        num_epochs=config.training.num_epochs,
        initial_step=current_step,
    )

    # ===========================================
    # メイントレーニングループ
    # ===========================================
    print(f"開始ステップ: {current_step}")
    print("=" * 60)
    print("トレーニングループ開始")
    print("=" * 60)
    print()
    
    for batch in training_iterator:
        print(f"\n{'='*60}")
        print(f"ステップ {batch.step} | エポック {batch.epoch} | エポック内ステップ {batch.epoch_step}")
        print(f"バッチサイズ: {len(batch.items)} シナリオ")
        print(f"{'='*60}")
        
        # ===========================================
        # トレーニンググループの作成
        # ===========================================
        train_groups = []
        for scenario in batch.items:
            # 各シナリオに対して複数のロールアウトを生成
            train_groups.append(
                art.TrajectoryGroup(
                    (
                        rollout(model, EmailScenario(step=batch.step, scenario=scenario))
                        for _ in range(config.training.rollouts_per_group)
                    )
                )
            )
        
        # ===========================================
        # ロールアウトの収集
        # ===========================================
        print(f"ロールアウトを収集中...")
        finished_train_groups = await art.gather_trajectory_groups(
            train_groups,
            pbar_desc="gather",
            max_exceptions=config.training.rollouts_per_group * len(batch.items),
        )
        
        # ===========================================
        # RULERによるスコアリング（リトライ付き）
        # ===========================================
        print(f"RULERでスコアリング中...")
        judged_groups = []
        for i, group in enumerate(finished_train_groups):
            # RULERを使用して各軌跡に相対スコアを付与
            # LLMジャッジが不完全な出力を返すことがあるのでリトライ
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    judged_group = await ruler_score_group(
                        group,
                        config.ruler.judge_model,
                        debug=config.ruler.debug
                    )
                    judged_groups.append(judged_group)
                    break  # 成功したらループを抜ける
                except ValueError as e:
                    if "scores" in str(e) and attempt < max_retries - 1:
                        print(f"  ⚠️ RULERスコアリング失敗 (グループ {i+1}, 試行 {attempt+1}/{max_retries}): {e}")
                        print(f"  → リトライします...")
                        continue
                    else:
                        print(f"  ❌ RULERスコアリング失敗 (グループ {i+1}): {e}")
                        raise
        
        # ===========================================
        # バリデーション（指定間隔で実行）
        # ===========================================
        if batch.step % config.training.validation_step_interval == 0:
            print(f"\nバリデーションを実行中（ステップ {batch.step}）...")
            validation_groups = []
            for scenario in validation_scenarios:
                validation_groups.append(
                    art.TrajectoryGroup([
                        rollout(model, EmailScenario(step=batch.step, scenario=scenario))
                    ])
                )
            
            finished_validation_groups = await art.gather_trajectory_groups(
                validation_groups,
                pbar_desc="validation",
                max_exceptions=len(validation_scenarios),
            )
            
            # バリデーション結果をログ
            await model.log(
                finished_validation_groups,
                split="val"
            )
            print(f"バリデーション完了")
        
        # ===========================================
        # チェックポイント削除とトレーニング
        # ===========================================
        print(f"モデルをトレーニング中...")
        await model.delete_checkpoints()
        await model.train(
            judged_groups,
            config=art.TrainConfig(learning_rate=config.training.learning_rate),
        )
        
        print(f"✅ ステップ {batch.step} 完了")
        
        # ===========================================
        # 最大ステップ数に達したら終了
        # ===========================================
        if batch.step >= config.training.max_steps:
            print(f"\n最大ステップ数 ({config.training.max_steps}) に達しました。トレーニング終了。")
            break
    
    print()
    print("=" * 60)
    print("🎉 トレーニング完了！")
    print("=" * 60)
    print()
    print("次のステップ:")
    print("  1. W&B/Weaveダッシュボードでメトリクスを確認")
    print("  2. python eval_model.py でモデルをテスト")


# ===========================================
# コマンドライン引数の解析
# ===========================================

def parse_args():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="ART-E Email Search Agent トレーニング"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="デモモード（小さいパラメータで実行）"
    )

    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="モデル名を上書き（新規トレーニング時に使用）"
    )

    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Weave/W&Bプロジェクト名を上書き"
    )
    
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="最大トレーニングステップ数を上書き"
    )
    
    parser.add_argument(
        "--groups-per-step",
        type=int,
        default=None,
        help="ステップあたりのグループ数を上書き"
    )
    
    parser.add_argument(
        "--rollouts-per-group",
        type=int,
        default=None,
        help="グループあたりのロールアウト数を上書き"
    )
    
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=None,
        help="学習率を上書き"
    )

    parser.add_argument(
        "--local",
        action="store_true",
        help="ローカル GPU を使用（LocalBackend）"
    )

    parser.add_argument(
        "--local-path",
        type=str,
        default="./.art",
        help="LocalBackend のデータ保存先パス（デフォルト: ./.art）"
    )

    return parser.parse_args()


# ===========================================
# メイン実行
# ===========================================

async def main():
    """
    メイン実行関数
    """
    args = parse_args()
    
    # 設定を取得（デモモードかどうかで切り替え）
    config = get_config(use_demo=args.demo)
    
    # コマンドライン引数で上書き
    if args.name:
        config.model.name = args.name
    if args.project:
        config.model.project = args.project
    if args.max_steps:
        config.training.max_steps = args.max_steps
    if args.groups_per_step:
        config.training.groups_per_step = args.groups_per_step
    if args.rollouts_per_group:
        config.training.rollouts_per_group = args.rollouts_per_group
    if args.learning_rate:
        config.training.learning_rate = args.learning_rate
    if args.local:
        config.backend.use_local = True
        config.backend.local_path = args.local_path

    # トレーニング実行
    await train(config)


if __name__ == "__main__":
    asyncio.run(main())
