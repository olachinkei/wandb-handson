"""
1_4: Agent Integration - エージェントフレームワークとの統合

このスクリプトで学べること:
================================
1. Weave SDK for Agents の概要（マルチターン・エージェントの計測）
2. Weave が提供する Agent Integration の一覧
3. OpenAI Agents SDK と Weave の連携（自動計測）
4. Agents タブでのマルチターン会話・ツール呼び出しの確認

実行後に確認する場所:
================================
- Agents タブ: 会話（conversation）ごとのマルチターン・タイムライン
- 各ターンの invoke_agent スパンと、その下にネストされた chat / execute_tool
- トークン使用量、ツールの入出力

はじめに（Weave SDK for Agents とは）:
================================
Weave SDK を使うと、マルチターンのエージェント・アプリケーションを計測し、
Agents タブで可視化できます。これはエージェントを構築・統合する開発者が、
会話・ターン・LLM 呼び出し・ツール実行に対して構造化された可視性を得るための
仕組みです。

Weave SDK for Agents は、マルチターン・エージェント会話のライフサイクル全体を
モデル化します。すなわち、
- 多数の会話を保持する「エージェント（agent）」
- ターンをまとめる「会話（conversation）」
- 各ユーザーとエージェントのやり取りである「ターン（turn）」
- ターン内の「LLM 呼び出し（LLM call）」
- LLM がトリガーする「ツール実行（tool execution）」
という階層です。

トレースは Weave プロジェクトの Agents タブに表示され、各会話は
ネストしたツール呼び出し・トークン使用量・フィードバックを含む
マルチターン・タイムラインとして確認できます。

Weave が提供する Agent Integration:
================================
以下のエージェント・フレームワーク／ツールには、Weave との統合が用意されています。
- Google ADK
- OpenAI Agents SDK   ← 本スクリプトでデモ
- Claude Agent SDK
- Claude Code plugin
- Codex plugin
- OpenCode plugin
- Pi extension

これらの統合を使うと、フレームワーク側のエージェント実行・ツール呼び出しが
自動的に Weave の Agents タブへ記録されます。本スクリプトでは
OpenAI Agents SDK を例に、最小構成のマルチターン・エージェントを計測します。

参考ドキュメント:
- https://docs.wandb.ai/weave/guides/integrations/agents/openai-agents-sdk
- https://docs.wandb.ai/weave/guides/tracking/trace-agents
"""

import asyncio

import requests
from dotenv import load_dotenv

from agents import Agent, Runner, function_tool

from config_loader import init_weave

# Load environment variables
load_dotenv()

# Initialize Weave
# init_weave() は内部で weave.init(...) を呼び出します。
# OpenAI Agents SDK の実行は Weave により自動計測されるため、
# Tracing Processor を手動登録する必要はありません。
init_weave()


# =============================================================================
# 1. ツール定義 - function_tool
# =============================================================================
print("\n" + "=" * 60)
print("1. ツール定義 - function_tool")
print("=" * 60)


@function_tool
def wikipedia_search(query: str) -> str:
    """トピックを Wikipedia で検索し、記事タイトルと導入段落を返す。

    OpenAI Agents SDK では、@function_tool を付けた関数がそのまま
    エージェントの「ツール」になります。エージェントが必要と判断すると
    このツールが呼び出され、Weave では execute_tool スパンとして記録されます。
    """
    response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": 1,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "format": "json",
        },
        headers={"User-Agent": "weave-handson-demo"},
        timeout=30,
    ).json()
    page = next(iter(response["query"]["pages"].values()))
    return f"{page['title']}: {page['extract']}"


# =============================================================================
# 2. エージェント定義 - Agent
# =============================================================================
print("\n" + "=" * 60)
print("2. エージェント定義 - Agent")
print("=" * 60)


research_agent = Agent(
    name="Research assistant",
    instructions=(
        "You are a research assistant. Use the wikipedia_search tool to look up "
        "topics when needed, and cite the article titles you used."
    ),
    tools=[wikipedia_search],
)


# =============================================================================
# 3. マルチターン実行 - Runner
# =============================================================================
print("\n" + "=" * 60)
print("3. マルチターン実行 - Runner")
print("=" * 60)

print("""
history を引き回すことで、同じ会話（conversation）の中で複数ターンを実行します。
各ターンは Agents タブで invoke_agent スパンとして表示され、その下に
chat（LLM 呼び出し）や execute_tool（ツール実行）がネストされます。
""")


async def main() -> None:
    """複数の質問を 1 つの会話として順番に処理するマルチターン・ループ。"""
    history: list = []
    questions = [
        "Who founded Anthropic?",
        "What is Claude (the AI assistant)?",
        "Summarize what we discussed in one sentence.",
    ]

    for question in questions:
        history.append({"role": "user", "content": question})
        print(f"\nUSER : {question}")
        result = await Runner.run(research_agent, input=history)
        print(f"AGENT: {result.final_output}")
        # 次のターンのために、これまでの入出力を history として引き継ぐ
        history = result.to_input_list()


asyncio.run(main())


print("\n" + "=" * 60)
print("Agent Integration Demo Complete!")
print("=" * 60)
print("""
まとめ:
- @function_tool でエージェントのツールを定義
- Agent() でエージェント、Runner.run() で実行
- weave.init(...) により OpenAI Agents SDK の実行を自動計測
- history を引き回すことでマルチターン会話を構成

Weave UI で確認:
- Agents タブで会話ごとのマルチターン・タイムラインを確認
- 各ターン（invoke_agent）の下に chat / execute_tool がネスト
- モデル選択・トークン使用量・ツールの入出力を確認
""")
