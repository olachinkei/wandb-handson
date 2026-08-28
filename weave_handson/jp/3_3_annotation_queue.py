"""
3_3: Annotation Queue - アノテーションキュー

==========================================================
Annotation Queue とは
==========================================================

Annotation Queue は、Weave に記録された Trace やモデル出力を、
人間のレビュアーが確認し、structured feedback を付けるための機能です。

LLM アプリケーションでは、完全に自動スコアだけで品質を判断するのが難しい
ケースがあります。たとえば、専門家の判断が必要な回答、微妙なニュアンスの評価、
安全性や正確性の確認などです。

Annotation Queue を使うと、レビュー対象をキューとして用意し、
レビュアーは 1 件ずつ内容を確認して評価を送信できます。

==========================================================
何に使うか
==========================================================

1. 人手評価の収集
   - 回答が正しいか
   - 回答が十分に役立つか
   - 回答に危険な内容や不適切な内容がないか

2. Evaluation Dataset の改善
   - 失敗例を見つける
   - 追加すべきテストケースを探す
   - 評価基準を見直す

3. Scorer / Guardrail の改善
   - 自動スコアと人間の判断がずれている例を確認する
   - Scorer の基準を調整する
   - Guardrail で検知できていないケースを見つける

4. 専門家レビュー
   - ドメインエキスパートにレビューを依頼する
   - レビュアーは Trace システムの詳細を知らなくても評価できる

==========================================================
基本的な流れ
==========================================================

1. レビュー対象の Trace や出力を選ぶ
2. Annotation Queue を作成する
3. レビュー項目や評価フォームを設定する
4. レビュアーがキューを開き、1 件ずつ確認して評価を送信する
5. structured feedback として結果を保存する
6. 保存された feedback を Evaluation や改善作業に利用する

==========================================================
このハンズオンとの関係
==========================================================

3_1 と 3_2 では、Scorer を使った自動評価を扱います。

Annotation Queue は、その次のステップです。自動評価だけでは判断しづらい
サンプルを人間がレビューし、より信頼できる評価データを集めます。

収集した feedback は、Dataset の改善、Scorer の調整、Prompt の改善、
Guardrail の設計に活用できます。

==========================================================
参考リンク
==========================================================

Annotation workflow:
https://docs.wandb.ai/ja/weave/guides/tracking/annotation-review#annotation-workflow

==========================================================
Note
==========================================================

- Annotation Queue の作成とレビュー操作は Weave UI で行います
- 下のサンプルコードでは、レビュー対象 Trace、AnnotationSpec、
  structured feedback の作成と読み戻しを SDK で確認します
- 実際のレビュー作業では、Weave UI でキューを作成・共有します
- 人手評価は、LLM アプリケーション改善の重要なフィードバック源になります
"""

from dotenv import load_dotenv
import weave

from config_loader import get_weave_project_name

load_dotenv()
weave.init(get_weave_project_name())

print(__doc__)


@weave.op()
def answer_for_review(question: str) -> dict:
    """アノテーション対象になる再現可能な回答を記録する。"""
    return {
        "answer": "Weave はLLMアプリのトレース、評価、監視を支援します。",
        "sources": ["https://docs.wandb.ai/weave"],
    }


print("\n1. レビュー対象のTraceを作成")
output, call = answer_for_review.call("W&B Weaveで何ができますか？")
print(f"call_id={call.id}")
print(f"output={output}")

print("\n2. AnnotationSpecを公開")
quality_spec = weave.AnnotationSpec(
    name="answer_quality",
    description="回答の品質を人手でレビューするためのフォーム",
    field_schema={
        "type": "object",
        "properties": {
            "score": {"type": "integer", "minimum": 1, "maximum": 5},
            "approved": {"type": "boolean"},
            "comment": {"type": "string"},
        },
        "required": ["score", "approved"],
    },
)
spec_ref = weave.publish(quality_spec)
print(f"annotation_spec={spec_ref.uri()}")

print("\n3. structured feedbackを送信して読み戻す")
feedback_id = call.feedback.add(
    "wandb.annotation.answer_quality",
    payload={
        "value": {"score": 5, "approved": True, "comment": "簡潔で根拠もある"}
    },
    annotation_ref=spec_ref.uri(),
)
# Feedbackはバックグラウンド送信されるため、読み戻す前にキューをflushする。
weave.finish()
weave.init(get_weave_project_name())
feedbacks = list(call.feedback)
assert any(item.id == feedback_id for item in feedbacks)
print(f"feedback_id={feedback_id}")
print(f"feedback_count={len(feedbacks)}")
print("\nAnnotation workflow demo: OK")
