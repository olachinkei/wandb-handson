"""4_4: Agent Signals - User Frustration detection demo.

This script is based on W&B's official OpenAI Agents SDK integration example.
It records a multi-turn conversation designed to trigger the User Frustration
Signal.

Official example:
https://docs.wandb.ai/weave/guides/integrations/agents/openai-agents-sdk

Agent Signals:
https://docs.wandb.ai/weave/guides/tracking/view-agent-signals

Prerequisites:
1. Open the Agents view in your W&B Project.
2. Select "+ New signal" in the Signals tab.
3. Create the "User Frustration" preset under Tags.
4. Run this script.

After running:
1. Open Agents > Signals.
2. Filter the Scorer column to "User Frustration".
3. Inspect turns 2 and 3, especially turn 3 with explicit dissatisfaction.

The User Frustration preset detects signs of frustration, anger, confusion,
or dissatisfaction. Tag Signals display only matching turns in the Signals
table, so the normal first turn is not expected to appear.
"""

from __future__ import annotations

import asyncio

import requests
import weave
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv

from config_loader import get_weave_project_name


load_dotenv()

# As in the official example, weave.init(...) automatically instruments the
# OpenAI Agents SDK. No manual Tracing Processor registration is needed.
weave.init(get_weave_project_name())


@function_tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for a topic and return its title and introduction."""
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


# Turn 1 is a normal request. Turn 2 expresses dissatisfaction with the answer,
# and turn 3 explicitly expresses strong frustration and a repeated request.
# This makes non-matching and matching User Frustration turns easy to compare.
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
    """Run three user turns as one conversation."""
    history: list = []

    print("\nStarting the User Frustration conversation demo...")

    for turn, question in enumerate(QUESTIONS, start=1):
        history.append({"role": "user", "content": question})
        print(f"\nTURN {turn}")
        print(f"USER : {question}")

        result = await Runner.run(agent, input=history)
        print(f"AGENT: {result.final_output}")

        # As in the official example, pass prior history into the next Runner.run.
        history = result.to_input_list()

    print("\n" + "=" * 72)
    print("User Frustration demo complete")
    print("=" * 72)
    print(
        "Open Agents > Signals in the Weave UI and inspect the User Frustration "
        "Signal. Signal evaluation may take a short time to complete."
    )


if __name__ == "__main__":
    asyncio.run(main())
