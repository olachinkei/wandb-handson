/**
 * 3_3: Annotation Queue - アノテーションキュー
 *
 * TypeScript 対応: UI 機能
 * - TypeScript で生成した Trace も Annotation Queue の対象にできます。
 * - この章は SDK コードではなく、Weave UI 上のレビュー workflow の説明です。
 */

// =============================================================================
// SECTION: Annotation Queue Overview
// =============================================================================
console.log(`
3_3: Annotation Queue - アノテーションキュー

Annotation Queue は、Weave に記録された Trace やモデル出力を人間のレビュアーが確認し、
structured feedback を付けるための機能です。

TypeScript 版での扱い:
- jp/1_1_basic_trace.ts や jp/3_1_evaluation.ts で Trace / Evaluation を作成します。
- Weave UI で対象 Trace を選び、Annotation Queue を作成します。
- レビュアーは UI 上で評価を入力します。
- 収集した feedback は Dataset、Scorer、Prompt、Guardrail の改善に使います。

参考:
https://docs.wandb.ai/weave/guides/tracking/annotation-review#annotation-workflow
`);
