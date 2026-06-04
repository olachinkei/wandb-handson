"""
5_2: Automations - 条件に応じた通知やアクション

==========================================================
Automations とは
==========================================================

Automations は、Weave project 内の monitor metrics や trace activity に
基づいて、条件を満たしたときにアクションを実行するための機能です。

たとえば、人が毎回ダッシュボードを見に行かなくても、
スコアの悪化、エラー率の増加、レイテンシの悪化などをきっかけに
Slack 通知や Webhook を実行できます。

==========================================================
何に使うか
==========================================================

1. Threshold alert
   - monitor の平均スコアがしきい値を超えたら通知する
   - toxicity や hallucination の増加を検知する

2. Regression detection
   - 新しい変更後に品質スコアが落ちたら通知する
   - 正確性や安全性の悪化を早めに見つける

3. Deployment gate
   - rolling window で一定以上の品質を満たしたら Webhook を実行する
   - リリース判断や運用フローに組み込む

4. Operational monitoring
   - エラー率、レイテンシ、rate limit などの変化を通知する

==========================================================
基本的な流れ
==========================================================

1. Weave project で対象となる Op や Monitor を用意する
2. Slack integration や Webhook など、実行したい action を設定する
3. Automations ページで Create automation を選ぶ
4. Event configuration で metric、threshold、window、aggregation を設定する
5. Action configuration で Slack 通知や Webhook を設定する
6. Summary を確認して automation を作成する

==========================================================
このハンズオンとの関係
==========================================================

3_4 Monitors で継続評価の仕組みを理解したあとに、
Automations を使うと「問題を検知する」だけでなく
「検知したら通知する / action を起こす」流れまで作れます。

==========================================================
参考リンク
==========================================================

Set up automations:
https://docs.wandb.ai/weave/guides/evaluation/automations

==========================================================
Note
==========================================================

- Automations は UI 上で設定する機能なので、このスクリプトでは説明のみを表示します
- Slack や Webhook を使う場合は、Team Settings 側の integration 設定が必要です
"""

print(__doc__)
