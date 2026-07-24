/**
 * 3_1: Offline Evaluation - Evaluation による系統的な評価
 *
 * TypeScript 対応: 対応
 * - Dataset と Evaluation を使用します。
 * - Scorer は weave.op で作る function-based scorer です。
 */

import * as weave from "weave";

import { getModelName, getOpenAIClient, initWeave, printSection } from "../src/config.js";

type GrammarEvalRow = {
  sentence: string;
  expected: string;
};

type GrammarOutput = {
  corrected: string;
};

await initWeave();

// =============================================================================
// SECTION 1: Create Dataset
// =============================================================================
printSection("1. Create Dataset - 評価用データセットの作成");

const dataset = new weave.Dataset<GrammarEvalRow>({
  name: "grammar_eval_ts",
  rows: [
    { sentence: "He no likes ice cream.", expected: "He doesn't like ice cream." },
    { sentence: "She goed to the store.", expected: "She went to the store." },
    { sentence: "They was playing outside.", expected: "They were playing outside." },
    { sentence: "I has a big dog.", expected: "I have a big dog." },
    { sentence: "We runned very fast.", expected: "We ran very fast." },
  ],
});
await dataset.save();
console.log(`Created dataset: ${dataset.length} rows`);

// =============================================================================
// SECTION 2: Define Models
// =============================================================================
printSection("2. Define Models - 評価対象モデルを 2 種類定義");

const weakGrammarModel = weave.op(
  async function weakGrammarModel({ datasetRow }: { datasetRow: GrammarEvalRow }): Promise<GrammarOutput> {
    const response = await getOpenAIClient().chat.completions.create({
      model: getModelName(),
      messages: [
        {
          role: "system",
          content:
            "You are a careless grammar checker. Make only a tiny edit, and if unsure, return the original sentence. Return only one sentence.",
        },
        { role: "user", content: datasetRow.sentence },
      ],
      temperature: 0.7,
    });
    return { corrected: response.choices[0]?.message?.content?.trim() ?? "" };
  },
  { name: "grammar_model_ts" }
);

const strongGrammarModel = weave.op(
  async function strongGrammarModel({ datasetRow }: { datasetRow: GrammarEvalRow }): Promise<GrammarOutput> {
    const response = await getOpenAIClient().chat.completions.create({
      model: getModelName(),
      messages: [
        {
          role: "system",
          content:
            "Correct grammar while preserving meaning. Return only the corrected sentence, with no explanation.",
        },
        { role: "user", content: "He are happy." },
        { role: "assistant", content: "He is happy." },
        { role: "user", content: "I has a big dog." },
        { role: "assistant", content: "I have a big dog." },
        { role: "user", content: datasetRow.sentence },
      ],
      temperature: 0,
    });
    return { corrected: response.choices[0]?.message?.content?.trim() ?? "" };
  },
  { name: "grammar_model_ts" }
);

type GrammarModelFn = (args: { datasetRow: GrammarEvalRow }) => Promise<GrammarOutput>;
type GrammarModelOp = ReturnType<typeof weave.op<GrammarModelFn>>;

console.log(`Created model ops with model: ${getModelName()}`);
console.log("Both model ops use the same OpenAI model name.");
console.log("Weave model op name: grammar_model_ts");

// =============================================================================
// SECTION 3: Define Scorers
// =============================================================================
printSection("3. Define Scorers - 評価関数の定義");

const exactMatch = weave.op(
  function exactMatch({
    modelOutput,
    datasetRow,
  }: {
    modelOutput: GrammarOutput;
    datasetRow: GrammarEvalRow;
  }) {
    return { match: datasetRow.expected.trim() === modelOutput.corrected.trim() };
  },
  { name: "exact_match_ts" }
);

const similarity = weave.op(
  function similarity({
    modelOutput,
    datasetRow,
  }: {
    modelOutput: GrammarOutput;
    datasetRow: GrammarEvalRow;
  }) {
    const expectedWords = new Set(datasetRow.expected.toLowerCase().split(/\s+/));
    const correctedWords = new Set(modelOutput.corrected.toLowerCase().split(/\s+/));
    const overlap = [...expectedWords].filter((word) => correctedWords.has(word)).length;
    return { similarity: overlap / Math.max(expectedWords.size, 1) };
  },
  { name: "similarity_ts" }
);

console.log("Defined: exactMatch, similarity");

// =============================================================================
// SECTION 4: Run Evaluation
// =============================================================================
printSection("4. Run Evaluations - 2 種類のモデルを評価");

async function runGrammarEvaluation({
  evaluationName,
  model,
}: {
  evaluationName: string;
  model: GrammarModelOp;
}) {
  const evaluation = new weave.Evaluation({
    name: evaluationName,
    dataset,
    scorers: [exactMatch, similarity],
  });

  console.log(`Running evaluation: ${evaluationName}`);
  const summary = await evaluation.evaluate({ model });
  console.log(`${evaluationName} summary: ${JSON.stringify(summary, null, 2)}`);
  return summary;
}

const weakSummary = await runGrammarEvaluation({
  evaluationName: "grammar_eval_prompt_comparison_ts",
  model: weakGrammarModel,
});

const strongSummary = await runGrammarEvaluation({
  evaluationName: "grammar_eval_prompt_comparison_ts",
  model: strongGrammarModel,
});

console.log(
  `Evaluation summaries: ${JSON.stringify(
    {
      weakPrompt: weakSummary,
      strongPrompt: strongSummary,
    },
    null,
    2
  )}`
);

// =============================================================================
// COMPLETE
// =============================================================================
printSection("Offline Evaluation Demo Complete!");
console.log(`
まとめ:
- Dataset、model op、function-based scorer を Evaluation に渡す
- 同じ OpenAI model name を使い、弱い prompt / 強い prompt の 2 種類の model op を比較
- Evals タブで評価結果、各サンプルのスコア、集計を確認
`);
