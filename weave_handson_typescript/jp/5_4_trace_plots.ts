/**
 * 5_4: Trace Plots - Trace の cost / latency / token を可視化
 *
 * TypeScript 対応: UI 機能
 * - TypeScript SDK で記録した Trace も Trace Plots の対象です。
 */

// =============================================================================
// SECTION: Trace Plots Overview
// =============================================================================
console.log(`
5_4: Trace Plots - Trace の cost / latency / token を可視化

Trace Plots は、Weave の Traces ページで Trace-level metrics を
インタラクティブなチャートとして可視化する機能です。

TypeScript 版での扱い:
- jp/1_1_basic_trace.ts などで OpenAI call を記録します。
- Traces ページで Show Metrics を開き、latency、cost、token usage を確認します。
- operation や attributes で filter すると、特定の TypeScript service の傾向を見やすくなります。

参考:
https://docs.wandb.ai/weave/guides/tracking/trace-plots
`);
