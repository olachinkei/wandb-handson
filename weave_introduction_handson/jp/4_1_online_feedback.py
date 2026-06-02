"""
4_1: Online Feedback - オンラインフィードバック

このスクリプトで学べること:
================================
1. トレースへのフィードバック追加
2. リアクション、ノート、カスタムフィードバック
3. フィードバックの活用

実行後に確認する場所:
================================
- Traces タブ: フィードバック付きの call
- Feedback 表示: reaction、note、custom feedback
"""

import os
from dotenv import load_dotenv
import weave

from config_loader import chat_completion

# Load environment variables
load_dotenv()

# Initialize Weave
# weave.init("entity/project") で初期化
client_weave = weave.init(f"{os.getenv('WANDB_ENTITY')}/{os.getenv('WANDB_PROJECT', 'weave-handson')}")


# =============================================================================
# 1. Feedback API - トレース済み call へのフィードバック付与
# =============================================================================
print("\n" + "=" * 60)
print("1. Feedback API - トレース済み call へのフィードバック付与")
print("=" * 60)


@weave.op()
def answer_question(question: str) -> str:
    """質問応答を実行し、返された call に後からフィードバックを付与する例。"""
    messages = [
        {"role": "system", "content": "Answer briefly and clearly."},
        {"role": "user", "content": question},
    ]
    return chat_completion(messages, max_tokens=120)


answer, call = answer_question.call("W&B Weave は何をするためのツールですか？")
print(f"Answer: {answer[:80]}...")

# SDK から reaction / note / 任意の structured feedback を追加
reaction_id = call.feedback.add_reaction("👍")
note_id = call.feedback.add_note("簡潔でわかりやすい回答")
score_id = call.feedback.add("quality_score", {"value": 4})
print(f"Feedback IDs: reaction={reaction_id}, note={note_id}, score={score_id}")
print(f"Added feedback to call: {call.id}")


print("\n" + "=" * 60)
print("Online Feedback Demo Complete!")
print("=" * 60)
print("""
まとめ:
- call.feedback.add_reaction() でリアクションを追加
- call.feedback.add_note() でノートを追加
- call.feedback.add() で任意の structured feedback を追加

Weave UI で確認:
- Traces タブでフィードバック付き call を確認
- Feedback 表示で reaction、note、custom feedback を確認
""")
