/**
 * 5_6: Playground - プロンプト実験
 *
 * TypeScript 対応: UI 機能
 * - TypeScript で生成した OpenAI Trace も Playground で再実験できます。
 */

// =============================================================================
// SECTION: Playground Overview
// =============================================================================
console.log(`
5_6: Playground - プロンプト実験

Weave Playground は、Weave UI 上でプロンプトやモデル設定を直接編集し、
過去の Trace をもとに再実験できる機能です。

TypeScript 版での使い方:
1. npm run run:1_1 などで OpenAI Trace を作ります。
2. Weave UI を開きます。
   https://wandb.ai/<entity>/<project>/weave
3. Traces タブから任意の OpenAI call を選択します。
4. Playground で開き、system prompt / user prompt / model / temperature などを変更します。
5. 良い設定が見つかったら、2_1_assets.ts の Prompt / config 管理につなげます。

参考:
https://docs.wandb.ai/weave/guides/tools/playground
`);
