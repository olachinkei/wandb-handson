/**
 * 5_1: W&B Skills / MCP - AI エージェントから W&B を使う
 *
 * TypeScript 対応: 外部機能
 * - TypeScript SDK のコードというより、AI エージェントが W&B / Weave を参照するための環境設定です。
 */

// =============================================================================
// SECTION: W&B Skills / MCP Overview
// =============================================================================
console.log(`
5_1: W&B Skills / MCP - AI エージェントから W&B を使う

W&B Skills:
AI コーディングエージェントに、W&B / Weave の調査方法や実験結果の読み方を
教えるためのスキル集です。

W&B MCP Server:
IDE、コーディングエージェント、チャットエージェントから
Runs、Traces、Evaluations、Artifacts、ドキュメントなどを自然言語で参照しやすくします。

TypeScript 版での扱い:
- TypeScript アプリが生成した Weave Trace / Evaluation も MCP 経由の調査対象になります。
- MCP Server 側では WANDB_API_KEY と、必要に応じて WANDB_BASE_URL を設定します。
- Dedicated Cloud / self-managed の場合は接続先 URL を管理者に確認してください。

参考:
https://github.com/wandb/skills
https://docs.wandb.ai/platform/mcp-server
`);
