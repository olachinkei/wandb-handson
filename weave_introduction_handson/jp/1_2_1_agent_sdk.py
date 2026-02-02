"""
1_2_1: OpenAI Agent SDK - エージェント構築

このスクリプトで学べること:
================================
1. OpenAI Agent SDK の基本的な使い方
2. function_tool を使ったツール定義
3. WeaveTracingProcessor によるトレーシング

事前準備:
--------
pip install openai-agents

参考:
----
- OpenAI Agent SDK: https://github.com/openai/openai-agents-python
- Weave Integration: https://docs.wandb.ai/weave/guides/integrations/openai-agents
"""

import os
import asyncio
from dotenv import load_dotenv
import weave
from agents import Agent, Runner, function_tool, set_trace_processors
from weave.integrations.openai_agents.openai_agents import WeaveTracingProcessor

# Load environment variables
load_dotenv()

# Initialize Weave
# weave.init("entity/project") で初期化
weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")

# WeaveTracingProcessor を設定してトレーシングを有効化
set_trace_processors([WeaveTracingProcessor()])


# =============================================================================
# Agent with Multiple Tools
# =============================================================================
print("\n" + "=" * 60)
print("Agent with Multiple Tools")
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


@weave.op()
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
ポイント:
- @function_tool でツールを定義
- Agent() でエージェントを作成
- Runner.run() でエージェントを実行
- set_trace_processors([WeaveTracingProcessor()]) でトレーシングを有効化
""")
