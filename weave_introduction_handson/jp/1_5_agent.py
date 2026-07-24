"""
1_5: Agent - Weave Agent SDK による手動インストルメンテーション

このスクリプトで学べること:
================================
1. Weave Agent SDK の基本（conversation / turn / LLM / tool）
2. context manager パターンでのマルチターン会話の計測
3. context manager を使わない manual パターン
4. コンテキストから現在のスパンを取得するヘルパー

実行後に確認する場所:
================================
- Agents タブ: weather-bot の会話・ターン・LLM 呼び出し・ツール実行
- 各ターン（invoke_agent）配下の chat / execute_tool とトークン使用量

はじめに（Weave Agent SDK とは）:
================================
Weave SDK を使うと、マルチターンのエージェント・アプリケーションを計測し、
Agents タブで可視化できます。会話・ターン・LLM 呼び出し・ツール実行に対して
構造化された可視性を得られます。

Weave Agent SDK は、マルチターン・エージェント会話のライフサイクル全体を
モデル化します。多数の会話を保持する「エージェント」、ターンをまとめる
「会話（conversation）」、各やり取りである「ターン（turn）」、ターン内の
「LLM 呼び出し」、LLM がトリガーする「ツール実行」という階層です。
トレースは Agents タブに表示され、各会話はネストしたツール呼び出し・
トークン使用量・フィードバックを含むマルチターン・タイムラインになります。

Weave は OpenTelemetry (OTel) の上に構築されています。すべてのターン・
LLM 呼び出し・ツール呼び出しは OTel スパン（1 つの操作を表す構造化レコード）を
emit し、各スパンには gen_ai.agent.name や gen_ai.conversation.id といった
GenAI セマンティック規約の属性が付与されます。

補足:
- 個々の関数を Op として計測したい場合（@weave.op デコレータ）は、
  1_1_basic_trace.py の「LLM アプリケーションのトレース」を参照してください。
- 本スクリプトの API（start_conversation / start_turn / start_llm / start_tool）は
  weave >= 0.53.x が必要です。

参考ドキュメント:
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
# ヘルパー: ツール（モック）と LLM 呼び出し
# =============================================================================
def get_weather(city: str) -> str:
    """天気を返すモックツール。実運用では外部 API を呼ぶ想定。"""
    fake_db = {"Tokyo": "24°C, sunny", "London": "16°C, cloudy"}
    return fake_db.get(city, "unknown")


def call_openai(messages: list[dict]):
    """OpenAI chat completion を実行し、レスポンスオブジェクトを返す。

    レスポンスから本文とトークン使用量を取り出し、Weave の LLM スパンへ
    記録します（llm.output / llm.usage）。
    """
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=150,
    )


# =============================================================================
# 1. Context manager パターン（推奨）
# =============================================================================
print("\n" + "=" * 60)
print("1. Context manager パターン（推奨）")
print("=" * 60)

# start_conversation でエージェントの会話を開始します。
# conversation.start_turn で 1 ターン（ユーザーとの 1 往復）を表現し、
# その中で start_llm / start_tool を使って LLM 呼び出しとツール実行を記録します。
with weave.start_conversation(agent_name="weather-bot", model=MODEL) as conversation:
    print(f"conversation_id: {conversation.conversation_id}")

    # --- ターン 1: 天気を尋ねる ---
    user_msg = "What is the weather in Tokyo?"
    with conversation.start_turn(user_message=user_msg) as turn:
        print(f"\n[Turn 1] USER: {user_msg}")

        # LLM 呼び出し 1: どのツールを使うか判断させる
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

        # ツール実行: get_weather("Tokyo")
        with weave.start_tool(name="get_weather", arguments='{"city": "Tokyo"}') as tool:
            weather = get_weather("Tokyo")
            tool.result = weather
            print(f"[Turn 1] TOOL get_weather -> {weather}")

        # LLM 呼び出し 2: ツール結果を踏まえて最終応答を作る
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
    # 2. Multi-turn: 同じ会話の中で 2 ターン目を続ける
    # =========================================================================
    print("\n" + "=" * 60)
    print("2. Multi-turn - 同じ会話で 2 ターン目")
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
# 3. Manual パターン（context manager を使わない）
# =============================================================================
print("\n" + "=" * 60)
print("3. Manual パターン（context manager を使わない）")
print("=" * 60)

# コールバックやキューワーカーなど、with ブロックを使いにくい場面では
# start_* で開始し、明示的に .end() で終了します。呼び出し順に注意してください。
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
print("Manual パターンの turn を記録しました（conversation_id:", conversation.conversation_id, "）")


# =============================================================================
# 4. コンテキストから現在のスパンを取得する
# =============================================================================
print("\n" + "=" * 60)
print("4. コンテキストから現在のスパンを取得する")
print("=" * 60)

# 非同期コンテキストやネストした関数の中で、現在の conversation / turn / llm を
# 明示的に引き回さずに取得できます。
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
まとめ:
- start_conversation / start_turn / start_llm / start_tool で会話を計測
- LLM スパンには input_messages / output() / usage を記録
- context manager（with）と manual（.end()）の両パターンが使える
- get_current_conversation() などでコンテキストから現在のスパンを取得

Weave UI で確認:
- Agents タブで weather-bot の会話・ターン・LLM・ツールを確認
- 各ターン（invoke_agent）配下の chat / execute_tool とトークン使用量
""")
