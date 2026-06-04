/**
 * 5_2: Automations - 条件に応じた通知やアクション
 *
 * TypeScript 対応: UI 機能
 * - TypeScript で生成した Trace / Monitor metrics も Automation の条件にできます。
 */

// =============================================================================
// SECTION: Automations Overview
// =============================================================================
console.log(`
5_2: Automations - 条件に応じた通知やアクション

Automations は、Weave project 内の monitor metrics や trace activity に基づいて、
条件を満たしたときに Slack 通知や Webhook などのアクションを実行する機能です。

TypeScript 版での扱い:
- jp/1_x や jp/4_2 を実行して Trace を作成します。
- Weave UI の Monitors / Automations で metric、threshold、window、action を設定します。
- TypeScript コード側に特別な Automation SDK 実装は不要です。

参考:
https://docs.wandb.ai/weave/guides/evaluation/automations
`);
