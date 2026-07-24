/**
 * 4_2: Guardrails - ガードレール
 *
 * TypeScript 対応: 未対応
 * - Python 版の Scorer class / call.apply_scorer() による guardrail API は、
 *   現状 TypeScript SDK では同等に扱っていません。
 * - TypeScript で生成した Trace は Weave UI の Monitor 対象にはできます。
 * - 実行時にアプリを止める guardrail を TypeScript SDK の Weave API として構成する例は、
 *   この教材では扱いません。
 */

console.log(`
4_2: Guardrails - TypeScript SDK では未対応

Python 版では:
- Scorer class
- call.apply_scorer()
- scorer result による runtime guardrail

TypeScript 版では:
- 上記と同等の SDK-level guardrail API はこの教材では扱いません。
- 継続的な passive scoring は 4_3 Custom Monitors を参照してください。
- アプリ側で独自にブロック処理を書くことはできますが、それは Weave SDK の guardrail API ではありません。
`);
