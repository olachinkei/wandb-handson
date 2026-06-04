/**
 * 5_5: Saved Views - よく使う Trace / Eval の見方を保存する
 *
 * TypeScript 対応: 主に UI 機能
 * - TypeScript で生成した Trace / Eval の table view を保存できます。
 * - Python SDK の SavedView helper は、この TypeScript 版では扱いません。
 */

// =============================================================================
// SECTION: Saved Views Overview
// =============================================================================
console.log(`
5_5: Saved Views - よく使う Trace / Eval の見方を保存する

Saved Views は、Traces や Evaluations の table 表示について、
filter、sort、columns、表示設定を保存して再利用する機能です。

TypeScript 版での扱い:
- TypeScript script で attributes を付けておくと filter しやすくなります。
- Traces または Evals の table で条件を調整し、Save view で保存します。
- チームで調査条件を共有できます。

Python 版との差分:
- Python SDK の weave.SavedView() による programmatic 作成は、この教材では TypeScript 移植していません。

参考:
https://docs.wandb.ai/weave/guides/tools/saved-views
`);
