"""
1_5: Agent - Manual instrumentation with the Weave Agent SDK

What you'll learn in this script:
================================
1. The basics of the Weave Agent SDK (conversation / turn / LLM / tool)
2. Instrumenting a multi-turn conversation with the context-manager pattern
3. The manual pattern (without context managers)
4. Helpers to fetch the current span from context

Where to look after running:
================================
- Agents tab: the weather-bot conversation, turns, LLM calls, and tool executions
- chat / execute_tool nested under each turn (invoke_agent), with token usage

Introduction (What is the Weave Agent SDK):
================================
Use the Weave SDK to instrument multi-turn agentic applications and view them
in the Agents tab. You get structured visibility into conversations, turns,
LLM calls, and tool executions.

The Weave Agent SDK models the full lifecycle of a multi-turn agent
conversation: the agent that owns many conversations, the conversation that
groups turns together, each user-agent exchange (turn), the LLM calls within a
turn, and the tool executions that an LLM triggers. Traces appear in the Agents
tab, where each conversation is a multi-turn timeline with nested tool calls,
token usage, and feedback.

Weave is built on OpenTelemetry (OTel), the open standard for distributed
tracing. Every turn, LLM call, and tool call emits an OTel span (a structured
record of one operation). Each span is tagged with GenAI semantic-convention
attributes like gen_ai.agent.name and gen_ai.conversation.id.

Notes:
- If you're tracing individual functions as Ops (the @weave.op decorator), see
  "Trace LLM applications" in 1_1_basic_trace.py instead.
- The API used here (start_conversation / start_turn / start_llm / start_tool)
  requires weave >= 0.53.x.

Reference doc:
- https://docs.wandb.ai/weave/guides/tracking/trace-agents
"""

from dotenv import load_dotenv

import weave
from weave import Message, Usage

from config_loader import get_llm_client, get_model_name, init_weave

# Load environment variables
load_dotenv()

# Initialize Weave
init_weave()

client = get_llm_client()
MODEL = get_model_name()


# =============================================================================
# Helpers: a (mock) tool and an LLM call
# =============================================================================
def get_weather(city: str) -> str:
    """Mock weather tool. In production this would call an external API."""
    fake_db = {"Tokyo": "24°C, sunny", "London": "16°C, cloudy"}
    return fake_db.get(city, "unknown")


def call_openai(messages: list[dict]):
    """Run an OpenAI chat completion and return the response object.

    We pull the body and token usage from the response and record them onto the
    Weave LLM span (llm.output / llm.usage).
    """
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=150,
    )


# =============================================================================
# 1. Context-manager pattern (recommended)
# =============================================================================
print("\n" + "=" * 60)
print("1. Context-manager pattern (recommended)")
print("=" * 60)

# start_conversation opens the agent's conversation. conversation.start_turn
# represents one turn (a single user-agent exchange); inside it, start_llm /
# start_tool record LLM calls and tool executions.
with weave.start_conversation(agent_name="weather-bot", model=MODEL) as conversation:
    print(f"conversation_id: {conversation.conversation_id}")

    # --- Turn 1: ask about the weather ---
    user_msg = "What is the weather in Tokyo?"
    with conversation.start_turn(user_message=user_msg) as turn:
        print(f"\n[Turn 1] USER: {user_msg}")

        # LLM call 1: let the model decide which tool to use
        messages = [
            {"role": "system", "content": "You are a weather assistant. Decide whether to look up the weather."},
            {"role": "user", "content": user_msg},
        ]
        with weave.start_llm(model=MODEL, provider_name="openai") as llm:
            resp = call_openai(messages)
            llm.input_messages = [Message(role=m["role"], content=m["content"]) for m in messages]
            llm.output(resp.choices[0].message.content)
            llm.usage = Usage(
                input_tokens=resp.usage.prompt_tokens,
                output_tokens=resp.usage.completion_tokens,
            )

        # Tool execution: get_weather("Tokyo")
        with weave.start_tool(name="get_weather", arguments='{"city": "Tokyo"}') as tool:
            weather = get_weather("Tokyo")
            tool.result = weather
            print(f"[Turn 1] TOOL get_weather -> {weather}")

        # LLM call 2: compose the final answer using the tool result
        messages2 = [
            {"role": "system", "content": "You are a weather assistant."},
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": f"The weather in Tokyo is {weather}."},
            {"role": "user", "content": "Please answer the original question in one friendly sentence."},
        ]
        with weave.start_llm(model=MODEL, provider_name="openai") as llm:
            resp = call_openai(messages2)
            final = resp.choices[0].message.content
            llm.input_messages = [Message(role=m["role"], content=m["content"]) for m in messages2]
            llm.output(final)
            llm.usage = Usage(
                input_tokens=resp.usage.prompt_tokens,
                output_tokens=resp.usage.completion_tokens,
            )
        print(f"[Turn 1] AGENT: {final}")

    # =========================================================================
    # 2. Multi-turn: continue with a second turn in the same conversation
    # =========================================================================
    print("\n" + "=" * 60)
    print("2. Multi-turn - a second turn in the same conversation")
    print("=" * 60)

    user_msg2 = "Given that weather, what should I wear?"
    with conversation.start_turn(user_message=user_msg2) as turn:
        print(f"\n[Turn 2] USER: {user_msg2}")
        messages3 = [
            {"role": "system", "content": "You are a helpful assistant. The weather in Tokyo is 24°C and sunny."},
            {"role": "user", "content": user_msg2},
        ]
        with weave.start_llm(model=MODEL, provider_name="openai") as llm:
            resp = call_openai(messages3)
            answer = resp.choices[0].message.content
            llm.input_messages = [Message(role=m["role"], content=m["content"]) for m in messages3]
            llm.output(answer)
            llm.usage = Usage(
                input_tokens=resp.usage.prompt_tokens,
                output_tokens=resp.usage.completion_tokens,
            )
        print(f"[Turn 2] AGENT: {answer}")


# =============================================================================
# 3. Manual pattern (without context managers)
# =============================================================================
print("\n" + "=" * 60)
print("3. Manual pattern (without context managers)")
print("=" * 60)

# For callbacks, queue workers, and other places where a with block is awkward,
# open with start_* and close explicitly with .end(). Mind the ordering.
conversation = weave.start_conversation(agent_name="weather-bot", model=MODEL)
turn = conversation.start_turn(user_message="What is the weather in London?")

llm = weave.start_llm(model=MODEL, provider_name="openai")
resp = call_openai([
    {"role": "system", "content": "You are a weather assistant."},
    {"role": "user", "content": "What is the weather in London?"},
])
llm.output(resp.choices[0].message.content)
llm.usage = Usage(
    input_tokens=resp.usage.prompt_tokens,
    output_tokens=resp.usage.completion_tokens,
)

tool = weave.start_tool(name="get_weather", arguments='{"city": "London"}')
tool.result = get_weather("London")
tool.end()

llm.end()
turn.end()
conversation.end()
print("Logged a manual-pattern turn (conversation_id:", conversation.conversation_id, ")")


# =============================================================================
# 4. Fetch the current span from context
# =============================================================================
print("\n" + "=" * 60)
print("4. Fetch the current span from context")
print("=" * 60)

# Inside async contexts or nested functions, you can retrieve the current
# conversation / turn / llm without threading them through explicitly.
with weave.start_conversation(agent_name="context-demo", model=MODEL) as conv:
    with conv.start_turn(user_message="hello") as t:
        current_conv = weave.get_current_conversation()
        current_turn = weave.get_current_turn()
        print("get_current_conversation():", current_conv.conversation_id if current_conv else None)
        print("get_current_turn() is not None:", current_turn is not None)
        with weave.start_llm(model=MODEL, provider_name="openai") as llm:
            print("get_current_llm() is not None:", weave.get_current_llm() is not None)
            llm.output("hi")
            llm.usage = Usage(input_tokens=1, output_tokens=1)


print("\n" + "=" * 60)
print("Agent SDK Demo Complete!")
print("=" * 60)
print("""
Summary:
- Instrument a conversation with start_conversation / start_turn / start_llm / start_tool
- Record input_messages / output() / usage on the LLM span
- Both the context-manager (with) and manual (.end()) patterns work
- Fetch the current span from context via get_current_conversation(), etc.

Check in the Weave UI:
- Agents tab shows the weather-bot conversation, turns, LLMs, and tools
- chat / execute_tool nested under each turn (invoke_agent), with token usage
""")
