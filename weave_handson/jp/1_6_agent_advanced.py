"""
1_6: Agent Advanced - エージェント計測の応用

このスクリプトで学べること:
================================
1. Attributes - スパンへのカスタムメタデータ付与
2. Batch logging - 完了済み会話を事後にまとめて記録
3. Sub-agents - サブエージェント（委譲）のネスト計測

実行後に確認する場所:
================================
- Agents タブ: 属性でのフィルタ、バッチ記録された会話、サブエージェントのネスト
- 各 invoke_agent スパン配下の chat / execute_tool

はじめに:
================================
1_5 で学んだ Weave Agent SDK（conversation / turn / LLM / tool）を土台に、
本スクリプトでは実運用で役立つ 3 つの応用トピックを扱います。
これらの API は weave >= 0.53.x が必要です。

参考ドキュメント:
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
# 1. Attributes - スパンへのカスタムメタデータ付与
# =============================================================================
print("\n" + "=" * 60)
print("1. Attributes - スパンへのカスタムメタデータ付与")
print("=" * 60)

print("""
属性（attributes）は「スパン全体のキー・バリュー属性」です。付与しておくと
Agents タブでその値によるフィルタやグループ化ができます。

注意点:
- set_attributes はスパンが記録中（with ブロックの中）に呼ぶ必要があります。
- 予約プレフィックス weave.* / gen_ai.* は避け、独自のキーを使ってください。
  （セマンティック規約のフィールドは start_* の引数で設定します）
- 以前の add_event は deprecated です。マーカー的なデータも set_attributes で
  記録してください。
""")

# 個別スパンへの属性付与
with weave.start_conversation(agent_name="support-bot") as conversation:
    with conversation.start_turn(user_message="What is the weather in Tokyo?") as turn:
        # ターン・スパン全体にカスタム属性をスタンプ
        turn.set_attributes({"user_id": "12345", "tenant": "acme", "env": "production"})

        # ツール・スパンにも個別に属性を付与できる
        with weave.start_tool(name="get_weather", arguments='{"city": "Tokyo"}') as tool:
            tool.set_attributes({"tool.category": "weather", "cache_hit": False})
            tool.result = "24°C, sunny"

        # LLM スパンにも属性を付与できる
        with weave.start_llm(model="gpt-4o-mini", provider_name="openai") as llm:
            llm.set_attributes({"prompt_version": "v3", "temperature_bucket": "low"})
            llm.output("It is 24°C and sunny in Tokyo.")
            llm.usage = Usage(input_tokens=40, output_tokens=12)

print("個別スパンに user_id / tenant / env などの属性を付与しました。")


# 会話全体への属性付与（emit される全スパンにスタンプされる）
with weave.start_conversation(
    agent_name="support-bot",
    attributes={"weave.integration.name": "my-harness", "env": "production"},
) as conversation:
    with conversation.start_turn(user_message="hello") as turn:
        with weave.start_llm(model="gpt-4o-mini", provider_name="openai") as llm:
            llm.output("Hi there!")
            llm.usage = Usage(input_tokens=5, output_tokens=3)

print("会話全体に weave.integration.name / env を付与しました。")


# =============================================================================
# 2. Batch logging - 完了済み会話を事後にまとめて記録
# =============================================================================
print("\n" + "=" * 60)
print("2. Batch logging - 完了済み会話を事後にまとめて記録")
print("=" * 60)

print("""
LLM 呼び出しがすでに完了しており、記録だけを行いたい場合（ステートレスな
コンテナ、コールバック、キューワーカーなど）は、context manager を開いたまま
にせず、スパンを構築して log_turn / log_conversation で一括 emit します。

conversation_id には「その会話を一意に識別する安定した文字列」を渡します。
各スパンには started_at / ended_at を設定しておくと、その値が OTel スパンの
タイムスタンプになります。
""")

now = datetime.now(timezone.utc)


def _span_times(offset_s: float, dur_s: float) -> dict:
    """started_at / ended_at を作るヘルパー。"""
    start = now + timedelta(seconds=offset_s)
    return {"started_at": start, "ended_at": start + timedelta(seconds=dur_s)}


# --- 2-1. 単一ターンを log_turn で記録 ---
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


# --- 2-2. 複数ターンを log_conversation で一括記録 ---
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
# 3. Sub-agents - サブエージェント（委譲）のネスト計測
# =============================================================================
print("\n" + "=" * 60)
print("3. Sub-agents - サブエージェント（委譲）のネスト計測")
print("=" * 60)

print("""
あるエージェントが別のエージェントへ処理を委譲する場合（例: スーパーバイザーが
専門エージェントを起動する）に sub-agent を使います。サブエージェントは
ネストした invoke_agent スパンを emit し、親子関係が保たれます。

想定されるネスト構造:
    turn (invoke_agent)               ← 親エージェントのターン
    ├── chat                          ← 親の判断
    └── research-specialist (invoke_agent)  ← サブエージェントへ委譲
        ├── chat                      ← サブエージェントの LLM 呼び出し
        └── execute_tool              ← サブエージェントのツール実行
""")

with weave.start_conversation(agent_name="supervisor", model="gpt-4o") as conversation:
    with conversation.start_turn(user_message="Research the founders of Anthropic.") as turn:

        # 親（スーパーバイザー）の LLM 呼び出し: どの専門家に委譲するか判断
        with weave.start_llm(model="gpt-4o", provider_name="openai") as llm:
            llm.input_messages = [Message(role="user", content="Research the founders of Anthropic.")]
            llm.output("Delegating to the research specialist.")
            llm.usage = Usage(input_tokens=80, output_tokens=10)

        # research-specialist サブエージェントへ委譲
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

        # 親のターンに戻り、最終回答を合成
        with weave.start_llm(model="gpt-4o", provider_name="openai") as llm:
            llm.output("Anthropic was founded by Dario and Daniela Amodei in 2021.")
            llm.usage = Usage(input_tokens=300, output_tokens=20)

print("supervisor -> research-specialist のサブエージェント委譲を記録しました。")


print("\n" + "=" * 60)
print("Agent Advanced Demo Complete!")
print("=" * 60)
print("""
まとめ:
- set_attributes: 個別スパン／会話全体にカスタムメタデータを付与
- log_turn / log_conversation: 完了済みの会話を事後に一括記録
- start_subagent: サブエージェントをネストした invoke_agent として計測

Weave UI で確認:
- Agents タブで属性によるフィルタ・グループ化
- バッチ記録された会話（conversation_id で識別）
- サブエージェントのネスト構造
""")
