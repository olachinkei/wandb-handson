"""
1_2: OpenAI Agent SDK - エージェント構築

このスクリプトで学べること:
================================
1. OpenAI Agent SDK の基本的な使い方
2. function_tool を使ったツール定義
3. WeaveTracingProcessor によるトレーシング

実行後に確認する場所:
================================
- Traces タブ: エージェント実行とツール呼び出し
- Code タブ: トレースされた関数と Agent SDK 連携

補足:
================================
このスクリプトでは、OpenAI Agents SDK と Weave の基本的な連携を扱います。
Agent アプリケーションでは、LLM 呼び出しだけでなく、ツール実行や複数ステップの
意思決定をまとめて追跡できることが重要です。

Weave では Agent 向け Trace の新機能が開発されており、現時点では
Public Preview として提供されています。最新の仕様は以下を確認してください。
https://docs.wandb.ai/weave/guides/tracking/trace-agents
"""

import asyncio
from dotenv import load_dotenv
import weave
from agents import Agent, Runner, function_tool, set_trace_processors
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

from config_loader import init_weave

# Load environment variables
load_dotenv()

# Initialize Weave
init_weave()

# WeaveTracingProcessor を設定してトレーシングを有効化
set_trace_processors([WeaveTracingProcessor()])


# =============================================================================
# 1. Agent with Multiple Tools - 複数ツールを持つエージェント
# =============================================================================
print("\n" + "=" * 60)
print("1. Agent with Multiple Tools - 複数ツールを持つエージェント")
print("=" * 60)


@function_tool
def search_database(query: str) -> list:
    """Search the database for relevant information."""
    # モックのデータベース検索
    return [
        {"id": 1, "title": f"Result 1 for: {query}", "score": 0.95},
        {"id": 2, "title": f"Result 2 for: {query}", "score": 0.87},
    ]


@function_tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
    # モックのメール送信
    return f"Email sent to {to} with subject: {subject}"


research_agent = Agent(
    name="ResearchAssistant",
    instructions="""You are a research assistant. You can:
    - Search the database for information
    - Send emails with findings
    Help the user with their research tasks.""",
    tools=[search_database, send_email],
)


async def run_research(input: str) -> str:
    """Research Agent を実行"""
    response = await Runner.run(research_agent, input)
    return response.final_output


result = asyncio.run(run_research("Search for information about machine learning and email the results to user@example.com"))
print(f"Result: {result[:100]}...")


print("\n" + "=" * 60)
print("Agent SDK Demo Complete!")
print("=" * 60)
print("""
まとめ:
- @function_tool で Agent SDK のツールを定義
- Agent() と Runner.run() でエージェントを実行
- WeaveTracingProcessor でエージェント実行を Weave に記録

Weave UI で確認:
- Traces タブでエージェント実行とツール呼び出しを確認
- Inputs/Outputs で各ツールの入出力を確認
""")
