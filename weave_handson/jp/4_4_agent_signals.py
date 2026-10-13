"""4_4: Agent Signals - User Frustration の検出デモ。

このスクリプトは、W&B公式のOpenAI Agents SDK連携例をもとに、
User Frustration Signalが検出しやすいマルチターン会話を記録します。

公式例:
https://docs.wandb.ai/weave/guides/integrations/agents/openai-agents-sdk

Agent Signals:
https://docs.wandb.ai/weave/guides/tracking/view-agent-signals

事前準備:
1. W&B ProjectのAgents viewを開く。
2. Signalsタブで「+ New signal」を選択する。
3. Tagsプリセットの「User Frustration」を選択して作成する。
4. このスクリプトを実行する。

実行後:
1. Agents > Signalsを開く。
2. Scorerを「User Frustration」で絞り込む。
3. 2・3ターン目、特に明示的な不満を含む3ターン目を確認する。

User Frustrationプリセットは、ユーザーの frustration、anger、confusion、
dissatisfaction の兆候を検出します。Tag Signalは条件に一致したターンだけを
Signalsテーブルに表示するため、正常な1ターン目が表示されないのは想定どおりです。
"""

from __future__ import annotations

import asyncio

import requests
import weave
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv



load_dotenv()

# 公式例と同じく、weave.init(...)だけでOpenAI Agents SDKを自動計測します。
weave.init()


@function_tool
def wikipedia_search(query: str) -> str:
    """トピックをWikipediaで検索し、記事タイトルと導入段落を返す。"""
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
        headers={"User-Agent": "weave-agent-signals-demo"},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return f"No Wikipedia article found for: {query}"

    page = next(iter(pages.values()))
    return f"{page['title']}: {page.get('extract', '')}"


agent = Agent(
    name="Frustration demo research assistant",
    instructions=(
        "You are a concise research assistant. Use the wikipedia_search tool "
        "when factual research is needed. Cite the Wikipedia article title you used. "
        "Respond calmly and helpfully even when the user expresses frustration."
    ),
    tools=[wikipedia_search],
)


# 1ターン目は通常の質問です。
# 2ターン目は回答への不満、3ターン目は強い苛立ちと反復要求を明示します。
# これにより、User Frustration Signalの非一致・一致を比較しやすくなります。
QUESTIONS = [
    "Who founded Anthropic? Use Wikipedia and cite the article title.",
    (
        "That answer was too vague and did not clearly list every founder. "
        "Please answer the question again with just the names."
    ),
    (
        "This is extremely frustrating. I have asked twice and still do not have "
        "a clear answer. I am unhappy with these responses. Just list the founders "
        "and cite the Wikipedia article you used."
    ),
]


async def main() -> None:
    """3つのユーザーターンを1つの会話として実行する。"""
    history: list = []

    print("\nStarting the User Frustration conversation demo...")

    for turn, question in enumerate(QUESTIONS, start=1):
        history.append({"role": "user", "content": question})
        print(f"\nTURN {turn}")
        print(f"USER : {question}")

        result = await Runner.run(agent, input=history)
        print(f"AGENT: {result.final_output}")

        # 公式例と同様に、前ターンまでの履歴を次のRunner.runへ渡します。
        history = result.to_input_list()

    print("\n" + "=" * 72)
    print("User Frustration demo complete")
    print("=" * 72)
    print(
        "Weave UIの Agents > Signals を開き、User Frustration Signalの結果を"
        "確認してください。Signalの評価完了まで少し時間がかかる場合があります。"
    )


if __name__ == "__main__":
    asyncio.run(main())
