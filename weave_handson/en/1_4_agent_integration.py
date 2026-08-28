"""
1_4: Agent Integration - Integrating with agent frameworks

What you'll learn in this script:
================================
1. Overview of the Weave SDK for Agents (instrumenting multi-turn agents)
2. The list of Agent Integrations Weave provides
3. Connecting the OpenAI Agents SDK with Weave (automatic instrumentation)
4. Inspecting multi-turn conversations and tool calls in the Agents tab

Where to look after running:
================================
- Agents tab: a multi-turn timeline per conversation
- Each turn's invoke_agent span, with nested chat / execute_tool underneath
- Token usage and tool inputs/outputs

Introduction (What is the Weave SDK for Agents):
================================
Use the Weave SDK to instrument multi-turn agentic applications and view them
in the Agents tab. This is for developers who build or integrate agents and
want structured visibility into conversations, turns, LLM calls, and tool
executions.

The Weave SDK for Agents models the full lifecycle of a multi-turn agent
conversation:
- the agent that owns many conversations,
- the conversation that groups turns together,
- each user-agent exchange (turn),
- the LLM calls within a turn,
- and the tool executions that an LLM triggers.

Traces appear in the Agents tab of your Weave project. Each conversation shows
a multi-turn timeline with nested tool calls, token usage, and feedback.

Agent Integrations Weave provides:
================================
The following agent frameworks/tools ship with a Weave integration:
- Google ADK
- OpenAI Agents SDK   <- demoed in this script
- Claude Agent SDK
- Claude Code plugin
- Codex plugin
- OpenCode plugin
- Pi extension

With these integrations, the framework's agent runs and tool calls are recorded
automatically into the Weave Agents tab. This script uses the OpenAI Agents SDK
to instrument a minimal multi-turn agent.

Reference docs:
- https://docs.wandb.ai/weave/guides/integrations/agents/openai-agents-sdk
- https://docs.wandb.ai/weave/guides/tracking/trace-agents
"""

import asyncio

import requests
from dotenv import load_dotenv
import weave

from agents import Agent, Runner, function_tool

from config_loader import get_weave_project_name

# Load environment variables
load_dotenv()

# Initialize Weave
# Weave automatically instruments OpenAI Agents SDK runs, so no manual
# Tracing Processor registration is needed.
weave.init(get_weave_project_name())


# =============================================================================
# 1. Tool definition - function_tool
# =============================================================================
print("\n" + "=" * 60)
print("1. Tool definition - function_tool")
print("=" * 60)


@function_tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for a topic and return its title and intro paragraph.

    In the OpenAI Agents SDK, a function decorated with @function_tool becomes
    a "tool" for the agent. When the agent decides it is needed, the tool is
    called and Weave records it as an execute_tool span.
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
# 2. Agent definition - Agent
# =============================================================================
print("\n" + "=" * 60)
print("2. Agent definition - Agent")
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
# 3. Multi-turn execution - Runner
# =============================================================================
print("\n" + "=" * 60)
print("3. Multi-turn execution - Runner")
print("=" * 60)

print("""
By carrying the history forward, multiple turns run within the same
conversation. Each turn appears in the Agents tab as an invoke_agent span,
with chat (LLM call) and execute_tool (tool execution) nested underneath.
""")


async def main() -> None:
    """A multi-turn loop that handles several questions as one conversation."""
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
        # Carry the accumulated inputs/outputs forward as history for the next turn.
        history = result.to_input_list()


asyncio.run(main())


print("\n" + "=" * 60)
print("Agent Integration Demo Complete!")
print("=" * 60)
print("""
Summary:
- Define agent tools with @function_tool
- Build the agent with Agent(), run it with Runner.run()
- Automatically instrument OpenAI Agents SDK runs through weave.init(...)
- Carry history forward to compose a multi-turn conversation

Check in the Weave UI:
- Agents tab shows a multi-turn timeline per conversation
- chat / execute_tool are nested under each turn (invoke_agent)
- Inspect model selection, token usage, and tool inputs/outputs
""")
