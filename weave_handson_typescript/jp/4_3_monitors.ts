/**
 * 4_3: Custom Monitors - TypeScript trace を Monitor 対象にする
 *
 * TypeScript 対応: 一部対応
 * - Monitor 対象の weave.op は TypeScript で実装できます。
 * - Custom Monitor の作成、scorer prompt、judge model、sampling rate の設定は Weave UI で行います。
 * - Monitor は passive scoring です。アプリの挙動をその場で止めたい場合は guardrails を使います。
 *
 * 参考:
 * https://docs.wandb.ai/weave/guides/evaluation/custom-monitors
 */

import * as weave from "weave";

import { getModelName, getOpenAIClient, initWeave, printSection } from "../src/config.js";

await initWeave();

type StatementCase = {
  groundTruth: string;
  makeIncorrect: boolean;
};

// =============================================================================
// SECTION 1: Define Monitor Target Op
// =============================================================================
printSection("1. Define Monitor Target Op - Monitor 対象の op を定義");

const generateStatement = weave.op(
  async function generateStatement({
    groundTruth,
    makeIncorrect,
  }: StatementCase): Promise<string> {
    if (!makeIncorrect) {
      return groundTruth;
    }

    const response = await getOpenAIClient().chat.completions.create({
      model: getModelName(),
      messages: [
        {
          role: "user",
          content: `Generate one concise statement that is incorrect based on this fact: ${groundTruth}`,
        },
      ],
      temperature: 0.7,
    });

    return response.choices[0]?.message?.content?.trim() ?? "";
  },
  { name: "generate_statement_ts" }
);

console.log("Defined op: generate_statement_ts");

// =============================================================================
// SECTION 2: Generate Traces
// =============================================================================
printSection("2. Generate Traces - Monitor 用の Trace を作成");

const cases: StatementCase[] = [
  {
    groundTruth: "The Earth revolves around the Sun.",
    makeIncorrect: false,
  },
  {
    groundTruth: "Water freezes at 0 degrees Celsius.",
    makeIncorrect: true,
  },
  {
    groundTruth: "The Great Wall of China was built over several centuries.",
    makeIncorrect: false,
  },
  {
    groundTruth: "Tokyo is the capital city of Japan.",
    makeIncorrect: true,
  },
];

for (const item of cases) {
  const statement = await generateStatement(item);
  console.log(`${item.makeIncorrect ? "Incorrect" : "Truthful"} case: ${statement}`);
}

// =============================================================================
// SECTION 3: Configure Monitor in Weave UI
// =============================================================================
printSection("3. Configure Monitor - Weave UI で設定");

console.log(`
Custom Monitor の作成は TypeScript SDK ではなく Weave UI で行います。

UI での設定例:
1. Weave project を開く
2. 左ナビの Monitors を開く
3. + New Monitor を選択
4. Operations で generate_statement_ts を選ぶ
   - この op は一度 trace を出してから候補に表示されます
5. Sampling rate を設定する
   - 例: 100%
6. Scorer name を設定する
   - 例: truthfulness_scorer
7. Judge model を選ぶ
8. System prompt を設定する
   - You are an impartial AI judge. Evaluate whether a generated statement is truthful.
9. Response format を json_object にする
10. Scoring prompt を設定する

Scoring prompt 例:
Evaluate whether the output statement is accurate based on the input fact.

Input fact:
{groundTruth}

Generated statement:
{output}

Return a JSON object with:
- is_true: boolean
- reasoning: string
`);

// =============================================================================
// COMPLETE
// =============================================================================
printSection("Custom Monitors Demo Complete!");
console.log(`
まとめ:
- TypeScript では monitor 対象の op と trace を作成できます。
- Custom Monitor 自体の作成、judge model、prompt、sampling rate は Weave UI で設定します。
- Monitor は passive scoring です。実行時にブロックしたい場合は guardrails を使います。
`);
