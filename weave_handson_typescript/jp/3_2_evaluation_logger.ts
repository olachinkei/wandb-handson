/**
 * 3_2: EvaluationLogger - 逐次ログによる柔軟な評価
 *
 * TypeScript 対応: 対応
 * - weave@0.15.1 では EvaluationLogger / ScoreLogger が export されています。
 * - EvaluationLogger は Dataset / Scorer を最初に固定しなくても、prediction と score を逐次記録できます。
 * - TypeScript では logPrediction() / logScore() / finish() の fire-and-forget pattern が使えます。
 * - 最後の logSummary() は pending operation を待って summary を記録します。
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
// SECTION 1: Prepare Dataset
// =============================================================================
printSection("1. Prepare Dataset - 評価データの準備");

const dataset = new weave.Dataset<GrammarEvalRow>({
  name: "grammar_eval_logger_dataset_ts",
  rows: [
    { sentence: "I has a big dog.", expected: "I have a big dog." },
    { sentence: "We runned very fast.", expected: "We ran very fast." },
    { sentence: "He are happy.", expected: "He is happy." },
    { sentence: "She goed to the store.", expected: "She went to the store." },
    { sentence: "They was playing outside.", expected: "They were playing outside." },
  ],
});
await dataset.save();
console.log(`Prepared dataset: ${dataset.length} rows`);

// =============================================================================
// SECTION 2: Initialize EvaluationLogger
// =============================================================================
printSection("2. Initialize EvaluationLogger - 評価ログの開始");

const evalLogger = new weave.EvaluationLogger({
  name: "grammar_eval_logger_v1_ts",
  model: { name: getModelName() },
  dataset,
  scorers: ["exact_match", "similarity"],
  attributes: {
    language: "typescript",
    mode: "incremental",
  },
});

console.log("EvaluationLogger initialized before model calls.");

// =============================================================================
// SECTION 3: Define Prediction Function
// =============================================================================
printSection("3. Define Prediction Function - 推論関数の定義");

const correctGrammar = weave.op(async function correctGrammar(sentence: string): Promise<GrammarOutput> {
  const response = await getOpenAIClient().chat.completions.create({
    model: getModelName(),
    messages: [
      { role: "system", content: "Correct the grammar. Return only the corrected sentence." },
      { role: "user", content: sentence },
    ],
    temperature: 0,
  });
  return { corrected: response.choices[0]?.message?.content?.trim() ?? "" };
});

console.log("Defined: correctGrammar");

// =============================================================================
// SECTION 4: Log Predictions and Scores
// =============================================================================
printSection("4. Log Predictions and Scores - 予測とスコアの逐次記録");

function similarityScore(output: string, expected: string): number {
  const expectedWords = new Set(expected.toLowerCase().split(/\s+/));
  const outputWords = new Set(output.toLowerCase().split(/\s+/));
  const overlap = [...expectedWords].filter((word) => outputWords.has(word)).length;
  return overlap / Math.max(expectedWords.size, 1);
}

const exactMatches: boolean[] = [];

for (let i = 0; i < dataset.length; i++) {
  const sample = dataset.getRow(i);
  const output = await correctGrammar(sample.sentence);
  const exactMatch = output.corrected === sample.expected;
  const similarity = similarityScore(output.corrected, sample.expected);
  exactMatches.push(exactMatch);

  const scoreLogger = evalLogger.logPrediction(
    {
      sentence: sample.sentence,
      expected: sample.expected,
    },
    output
  );

  scoreLogger.logScore("exact_match", exactMatch);
  scoreLogger.logScore("similarity", similarity);
  scoreLogger.finish();

  console.log(
    `  ${exactMatch ? "OK" : "NG"}: ${sample.sentence} -> ${output.corrected} ` +
      `(similarity=${similarity.toFixed(2)})`
  );
}

// =============================================================================
// SECTION 5: Log Summary
// =============================================================================
printSection("5. Log Summary - 評価全体の集計");

const exactMatchAccuracy = exactMatches.filter(Boolean).length / exactMatches.length;

await evalLogger.logSummary({
  exact_match_accuracy: exactMatchAccuracy,
  total: dataset.length,
});

console.log(`Exact Match Accuracy: ${(exactMatchAccuracy * 100).toFixed(1)}%`);

// =============================================================================
// COMPLETE
// =============================================================================
printSection("Evaluation Logger Demo Complete!");
console.log(`
まとめ:
- EvaluationLogger は TypeScript SDK で対応しています。
- logger は LLM 呼び出し前に作成します。
- logPrediction() で input/output を記録します。
- logScore() で prediction ごとの score を記録します。
- finish() で prediction を閉じます。
- logSummary() で pending operation を待ち、評価全体の summary を記録します。
`);
