"""
1_6: Agent Advanced - Advanced agent instrumentation

What you'll learn in this script:
================================
1. Attributes - attaching custom metadata to spans
2. Batch logging - recording a completed conversation after the fact
3. Sub-agents - nested instrumentation of delegated (sub) agents

Where to look after running:
================================
- Agents tab: filter by attributes, batch-logged conversations, sub-agent nesting
- chat / execute_tool nested under each invoke_agent span

Introduction:
================================
Building on the Weave Agent SDK from 1_5 (conversation / turn / LLM / tool),
this script covers three advanced topics useful in production. These APIs
require weave >= 0.53.x.

Reference docs:
- Attributes:      https://docs.wandb.ai/weave/guides/tracking/trace-agents-attributes
- Batch logging:   https://docs.wandb.ai/weave/guides/tracking/trace-agents-batch
- Sub-agents:      https://docs.wandb.ai/weave/guides/tracking/trace-sub-agents
"""

from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

import weave
from weave import LLM, Message, Tool, Turn, Usage

from config_loader import get_weave_project_name

# Load environment variables
load_dotenv()

# Initialize Weave
weave.init(get_weave_project_name())


# =============================================================================
# 1. Attributes - attaching custom metadata to spans
# =============================================================================
print("\n" + "=" * 60)
print("1. Attributes - attaching custom metadata to spans")
print("=" * 60)

print("""
Attributes are "key-value properties of a span as a whole." Once stamped, you
can filter and group agent activity by them in the Agents tab.

Notes:
- Call set_attributes while the span is actively recording (inside the with block).
- Avoid the reserved prefixes weave.* / gen_ai.* and use your own custom keys.
  (Set semantic-convention fields via the start_* parameters instead.)
- The old add_event is deprecated. Record marker-like data with set_attributes too.
""")

# Attributes on individual spans
with weave.start_conversation(agent_name="support-bot") as conversation:
    with conversation.start_turn(user_message="What is the weather in Tokyo?") as turn:
        # Stamp custom attributes on the turn span as a whole
        turn.set_attributes({"user_id": "12345", "tenant": "acme", "env": "production"})

        # You can also attach attributes to a tool span individually
        with weave.start_tool(name="get_weather", arguments='{"city": "Tokyo"}') as tool:
            tool.set_attributes({"tool.category": "weather", "cache_hit": False})
            tool.result = "24°C, sunny"

        # And to an LLM span
        with weave.start_llm(model="gpt-4o-mini", provider_name="openai") as llm:
            llm.set_attributes({"prompt_version": "v3", "temperature_bucket": "low"})
            llm.output("It is 24°C and sunny in Tokyo.")
            llm.usage = Usage(input_tokens=40, output_tokens=12)

print("Stamped user_id / tenant / env, etc. on individual spans.")


# Conversation-wide attributes (stamped on every span it emits)
with weave.start_conversation(
    agent_name="support-bot",
    attributes={"weave.integration.name": "my-harness", "env": "production"},
) as conversation:
    with conversation.start_turn(user_message="hello") as turn:
        with weave.start_llm(model="gpt-4o-mini", provider_name="openai") as llm:
            llm.output("Hi there!")
            llm.usage = Usage(input_tokens=5, output_tokens=3)

print("Stamped weave.integration.name / env on the whole conversation.")


# =============================================================================
# 2. Batch logging - recording a completed conversation after the fact
# =============================================================================
print("\n" + "=" * 60)
print("2. Batch logging - recording a completed conversation after the fact")
print("=" * 60)

print("""
When the LLM calls are already finished and you only need to record them
(stateless containers, callbacks, queue workers), don't keep context managers
open: build the span objects and emit them at once with log_turn / log_conversation.

Pass any stable string that uniquely identifies the conversation as conversation_id.
Set started_at / ended_at on each span so those values become the OTel span timestamps.
""")

now = datetime.now(timezone.utc)


def _span_times(offset_s: float, dur_s: float) -> dict:
    """Helper to build started_at / ended_at."""
    start = now + timedelta(seconds=offset_s)
    return {"started_at": start, "ended_at": start + timedelta(seconds=dur_s)}


# --- 2-1. Log a single turn with log_turn ---
llm_span_1 = LLM(
    model="gpt-4o",
    provider_name="openai",
    input_messages=[Message(role="user", content="What is the weather in Tokyo?")],
    output_messages=[Message(role="assistant", content="Let me check the weather.")],
    usage=Usage(input_tokens=100, output_tokens=20),
    **_span_times(0.0, 0.4),
)
tool_span = Tool(
    name="get_weather",
    arguments='{"city": "Tokyo"}',
    result="24°C, sunny",
    **_span_times(0.4, 0.1),
)
llm_span_2 = LLM(
    model="gpt-4o",
    provider_name="openai",
    output_messages=[Message(role="assistant", content="It is 24°C and sunny in Tokyo today.")],
    usage=Usage(input_tokens=150, output_tokens=30),
    **_span_times(0.5, 0.4),
)

result = weave.log_turn(
    conversation_id="batch-conversation-abc",
    agent_name="weather-bot",
    messages=[Message(role="user", content="What is the weather in Tokyo?")],
    spans=[llm_span_1, tool_span, llm_span_2],
)
print(f"log_turn: conversation_id={result.conversation_id}, span_count={result.span_count}")


# --- 2-2. Log multiple turns at once with log_conversation ---
turn_1 = Turn(
    agent_name="weather-bot",
    messages=[Message(role="user", content="What is the weather in Tokyo?")],
    spans=[
        LLM(
            model="gpt-4o",
            provider_name="openai",
            output_messages=[Message(role="assistant", content="It is 24°C and sunny.")],
            usage=Usage(input_tokens=100, output_tokens=20),
            **_span_times(0.0, 0.5),
        ),
    ],
    **_span_times(0.0, 0.6),
)
turn_2 = Turn(
    agent_name="weather-bot",
    messages=[Message(role="user", content="What about tomorrow?")],
    spans=[
        LLM(
            model="gpt-4o",
            provider_name="openai",
            output_messages=[Message(role="assistant", content="Tomorrow will be 22°C, partly cloudy.")],
            usage=Usage(input_tokens=120, output_tokens=25),
            **_span_times(1.0, 0.5),
        ),
    ],
    **_span_times(1.0, 0.6),
)

conv_result = weave.log_conversation(
    conversation_id="batch-conversation-xyz",
    agent_name="weather-bot",
    turns=[turn_1, turn_2],
)
print(f"log_conversation: conversation_id={conv_result.conversation_id}, span_count={conv_result.span_count}")


# =============================================================================
# 3. Sub-agents - nested instrumentation of delegated (sub) agents
# =============================================================================
print("\n" + "=" * 60)
print("3. Sub-agents - nested instrumentation of delegated (sub) agents")
print("=" * 60)

print("""
Use sub-agents when one agent hands off to another (e.g. a supervisor dispatches
a specialist). Sub-agents emit nested invoke_agent spans that preserve the
parent-child relationship.

Expected nesting:
    turn (invoke_agent)               <- the parent agent's turn
    ├── chat                          <- parent's reasoning
    └── research-specialist (invoke_agent)  <- delegation happens here
        ├── chat                      <- sub-agent's own LLM call
        └── execute_tool              <- sub-agent's tool execution
""")

with weave.start_conversation(agent_name="supervisor", model="gpt-4o") as conversation:
    with conversation.start_turn(user_message="Research the founders of Anthropic.") as turn:

        # Supervisor LLM call: decide which specialist to delegate to
        with weave.start_llm(model="gpt-4o", provider_name="openai") as llm:
            llm.input_messages = [Message(role="user", content="Research the founders of Anthropic.")]
            llm.output("Delegating to the research specialist.")
            llm.usage = Usage(input_tokens=80, output_tokens=10)

        # Delegate to the research-specialist sub-agent
        with weave.start_subagent(name="research-specialist", model="gpt-4o") as sub:
            with sub.start_llm(model="gpt-4o", provider_name="openai") as sub_llm:
                sub_llm.input_messages = [Message(role="user", content="Find founders of Anthropic.")]
                sub_llm.output("I should search for this.")
                sub_llm.usage = Usage(input_tokens=120, output_tokens=15)

            with sub.start_tool(name="wikipedia_search", arguments='{"query": "Anthropic"}') as tool:
                tool.result = "Anthropic was founded by Dario and Daniela Amodei in 2021."

            with sub.start_llm(model="gpt-4o", provider_name="openai") as sub_llm:
                sub_llm.output("Anthropic was founded by Dario and Daniela Amodei in 2021.")
                sub_llm.usage = Usage(input_tokens=200, output_tokens=25)

        # Back in the supervisor turn: synthesize the final answer
        with weave.start_llm(model="gpt-4o", provider_name="openai") as llm:
            llm.output("Anthropic was founded by Dario and Daniela Amodei in 2021.")
            llm.usage = Usage(input_tokens=300, output_tokens=20)

print("Logged a supervisor -> research-specialist sub-agent delegation.")


print("\n" + "=" * 60)
print("Agent Advanced Demo Complete!")
print("=" * 60)
print("""
Summary:
- set_attributes: attach custom metadata to individual spans or a whole conversation
- log_turn / log_conversation: batch-log a completed conversation after the fact
- start_subagent: instrument sub-agents as nested invoke_agent spans

Check in the Weave UI:
- Filter and group by attributes in the Agents tab
- Batch-logged conversations (identified by conversation_id)
- The sub-agent nesting structure
""")
