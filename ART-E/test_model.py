"""
===========================================
ART-E Email Search Agent - モデルテスト (W&B Inference)
===========================================

このモジュールは、トレーニング済みモデルをW&B Inference APIを使用してテストします。
art_e.pyでトレーニングした後に使用します。

使い方:
    # 基本的な使用法（artifact_pathは必須）
    python test_model.py --artifact-path "wandb-artifact:///agent-lab/ARTE-Email-Search-Agent/email-agent-003:v160"
    
    # 特定のシナリオ数でテスト
    python test_model.py --artifact-path "wandb-artifact:///..." --num-scenarios 10
    
    # デモモード（小さいパラメータ）
    python test_model.py --artifact-path "wandb-artifact:///..." --demo
"""

import argparse
import asyncio
import json
import logging
import os
import random
from dataclasses import asdict
from textwrap import dedent

import openai
import weave
from dotenv import load_dotenv
from langchain_core.utils.function_calling import convert_to_openai_tool
from litellm import acompletion
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt

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

# Weaveのログレベルを抑制
logging.getLogger("weave").setLevel(logging.CRITICAL)


# ===========================================
# RULER評価用モデル
# ===========================================

class CorrectnessJudgeResponse(BaseModel):
    """
    回答の正確性を判定するLLMジャッジの応答モデル
    """
    reasoning: str = Field(description="判断プロセスの説明")
    accept: bool = Field(description="AI回答を受け入れるかどうか")


# ===========================================
# グローバル設定
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

@weave.op
@retry(stop=stop_after_attempt(3))
async def judge_correctness(
    scenario: Scenario, answer: str
) -> CorrectnessJudgeResponse:
    """
    LLMジャッジを使用して回答の正確性を評価
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
# テスト結果クラス
# ===========================================

class TestResult:
    """テスト結果を保持するクラス"""
    def __init__(self):
        self.messages = []
        self.final_answer: FinalAnswer | None = None
        self.metrics = {}
        self.tools = []


# ===========================================
# ロールアウト関数（W&B Inference使用）
# ===========================================

@weave.op
async def rollout_test(
    client: openai.OpenAI,
    artifact_path: str,
    scenario: Scenario,
    config: Config,
) -> TestResult:
    """
    エージェントのロールアウト（1エピソードの実行）
    
    W&B Inference APIを使用してモデルを実行します。
    
    Args:
        client: OpenAIクライアント（W&B Inference用）
        artifact_path: W&Bアーティファクトパス
        scenario: 実行するシナリオ
        config: 設定オブジェクト
    
    Returns:
        TestResult: 実行結果
    """
    max_turns = config.training.max_turns
    result = TestResult()

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

    result.messages = [
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
    result.tools = [convert_to_openai_tool(t) for t in tools]

    # ===========================================
    # エージェントループ
    # ===========================================
    for _ in range(max_turns):
        # モデルからの応答を取得
        response = client.chat.completions.create(
            model=artifact_path,
            temperature=1,
            messages=result.messages,
            tools=result.tools,
        )

        response_message = response.choices[0].message
        
        # メッセージを辞書形式で保存
        assistant_msg = {
            "role": "assistant",
            "content": response_message.content or "",
        }
        if response_message.tool_calls:
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in response_message.tool_calls
            ]
        result.messages.append(assistant_msg)

        # ツール呼び出しがなければ終了
        if not response_message.tool_calls:
            return result

        try:
            # 各ツール呼び出しを実行
            for tool_call in response_message.tool_calls:
                tool_name: str = tool_call.function.name
                if tool_name in tools_by_name:
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_to_call = tools_by_name[tool_name]
                    tool_result = tool_to_call(**tool_args)
                    
                    # ツール結果をメッセージに追加
                    result.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": str(tool_result),
                        }
                    )

                    # 最終回答の場合はスコアリング
                    if tool_name == "return_final_answer":
                        result.final_answer = tool_result
                        if result.final_answer:
                            # RULER評価を実行
                            correctness_judge_response = await judge_correctness(
                                scenario, result.final_answer.answer
                            )
                            result.metrics["correct"] = float(
                                correctness_judge_response.accept
                            )
                        return result
        except Exception as e:
            print(f"ツール呼び出しエラー: {e}")
            return result

    return result


# ===========================================
# テスト関数
# ===========================================

async def test_single_scenario(
    client: openai.OpenAI,
    artifact_path: str,
    scenario: Scenario,
    config: Config,
    step: int = 0
):
    """
    単一のシナリオでモデルをテスト
    """
    print(f"\n{'='*60}")
    print(f"シナリオ ID: {scenario.id}")
    print(f"{'='*60}")
    print(f"質問: {scenario.question}")
    print(f"期待される回答: {scenario.answer}")
    print(f"参照メッセージID: {scenario.message_ids}")
    print(f"メールボックス: {scenario.inbox_address}")
    print(f"クエリ日付: {scenario.query_date}")
    print("-" * 50)

    # ロールアウト実行
    result = await rollout_test(client, artifact_path, scenario, config)

    # 結果を表示
    print("\n【エージェントの軌跡】")
    print("-" * 40)

    for msg in result.messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        tool_calls = msg.get("tool_calls", [])

        if role == "system":
            # システムプロンプトは短縮表示
            print(
                f"[SYSTEM]: {content[:100]}..."
                if len(content) > 100
                else f"[SYSTEM]: {content}"
            )
        elif role == "user":
            print(f"[USER]: {content}")
        elif role == "assistant":
            if tool_calls:
                # ツール呼び出しを見やすく表示
                for tc in tool_calls:
                    if isinstance(tc, dict):
                        func = tc.get("function", {})
                        print(f"[ASSISTANT → {func.get('name', '?')}]: {func.get('arguments', '{}')}")
                    else:
                        print(f"[ASSISTANT → {tc.function.name}]: {tc.function.arguments}")
            if content:
                print(f"[ASSISTANT]: {content}")
        elif role == "tool":
            tool_name = msg.get("name", "unknown_tool")
            # ツール結果は短縮表示
            print(
                f"[TOOL - {tool_name}]: {content[:200]}..."
                if len(content) > 200
                else f"[TOOL - {tool_name}]: {content}"
            )

        print()

    # 最終結果
    print("-" * 50)
    print("\n【結果】")
    if result.final_answer:
        print(f"✅ エージェントの回答: {result.final_answer.answer}")
        print(f"   使用したソースID: {result.final_answer.source_ids}")
        
        # 正解判定
        correct = result.metrics.get("correct", 0)
        if correct > 0:
            print(f"\n🎉 正解！")
        else:
            print(f"\n❌ 不正解")
    else:
        print("⚠️ エージェントは最終回答を提供しませんでした")

    print(f"\n📝 期待される回答: {scenario.answer}")
    print(f"   期待されるソースID: {scenario.message_ids}")
    
    return result


async def test_model(
    config: Config,
    artifact_path: str,
    num_scenarios: int = 5,
    api_key: str | None = None,
):
    """
    トレーニング済みモデルをテスト（W&B Inference使用）
    
    Args:
        config: 設定オブジェクト
        artifact_path: W&Bアーティファクトパス
        num_scenarios: テストするシナリオ数
        api_key: W&B APIキー（省略時は環境変数から取得）
    """
    # ===========================================
    # 設定をグローバルにセット
    # ===========================================
    set_config(config)
    
    # ===========================================
    # Weaveの初期化
    # ===========================================
    weave.init(
        config.model.project,
        settings={"print_call_link": False},
    )
    
    # ===========================================
    # APIキーの取得
    # ===========================================
    if api_key is None:
        api_key = os.environ.get("WANDB_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError(
            "APIキーが設定されていません。\n"
            "環境変数 WANDB_API_KEY または --api-key オプションで指定してください。\n"
            "APIキーは https://wandb.ai/authorize から取得できます。"
        )
    
    # ===========================================
    # OpenAIクライアント設定（W&B Inference用）
    # ===========================================
    client = openai.OpenAI(
        base_url="https://api.inference.wandb.ai/v1",
        api_key=api_key,
        # 使用状況トラッキング用のプロジェクト設定
        default_headers={
            "X-Wandb-Project": config.model.project,
        }
    )
    
    # ===========================================
    # モデル情報表示
    # ===========================================
    print("=" * 60)
    print("ART-E Email Search Agent - モデルテスト (W&B Inference)")
    print("=" * 60)
    print()
    print(f"プロジェクト: {config.model.project}")
    print(f"アーティファクトパス: {artifact_path}")
    print(f"テストシナリオ数: {num_scenarios}")
    print()
    
    # ===========================================
    # シナリオの読み込み
    # ===========================================
    print("テストシナリオを読み込み中...")
    test_scenarios = load_scenarios(
        split="train",
        limit=num_scenarios,
        max_messages=config.dataset.max_messages,
        shuffle=config.dataset.shuffle,
        seed=config.dataset.seed,
    )
    
    print(f"読み込んだシナリオ数: {len(test_scenarios)}")
    
    # ===========================================
    # テスト実行
    # ===========================================
    correct_count = 0
    total_count = 0
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n\n{'#'*60}")
        print(f"# テスト {i+1}/{len(test_scenarios)}")
        print(f"{'#'*60}")
        
        result = await test_single_scenario(
            client, artifact_path, scenario, config, step=i
        )
        
        total_count += 1
        if result.metrics.get("correct", 0) > 0:
            correct_count += 1
    
    # ===========================================
    # 結果サマリー
    # ===========================================
    print("\n")
    print("=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    print(f"正解数: {correct_count}/{total_count}")
    print(f"正解率: {correct_count/total_count*100:.1f}%")
    print()
    print("🎉 テスト完了！")


# ===========================================
# コマンドライン引数の解析
# ===========================================

def parse_args():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="ART-E Email Search Agent モデルテスト (W&B Inference)"
    )
    
    parser.add_argument(
        "--artifact-path",
        type=str,
        required=True,
        help=(
            "W&Bアーティファクトパス（必須）\n"
            "例: wandb-artifact:///agent-lab/ARTE-Email-Search-Agent/email-agent-003:v160"
        )
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        help="デモモード（小さいパラメータで実行）"
    )
    
    parser.add_argument(
        "--project",
        type=str,
        default=None,
        help="Weave/W&Bプロジェクト名を上書き"
    )
    
    parser.add_argument(
        "--num-scenarios",
        type=int,
        default=5,
        help="テストするシナリオ数（デフォルト: 5）"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="乱数シードを上書き"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="W&B APIキー（省略時は環境変数 WANDB_API_KEY から取得）"
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
    
    # 設定を取得
    config = get_config(use_demo=args.demo)
    
    # コマンドライン引数で上書き
    if args.project:
        config.model.project = args.project
    if args.seed is not None:
        config.dataset.seed = args.seed
    
    # テスト実行
    await test_model(
        config,
        artifact_path=args.artifact_path,
        num_scenarios=args.num_scenarios,
        api_key=args.api_key,
    )


if __name__ == "__main__":
    asyncio.run(main())
# python test_model.py --artifact-path "wandb-artifact:///agent-lab/ARTE-Email-Search-Agent/email-agent-003:v160" --num-scenarios 10
