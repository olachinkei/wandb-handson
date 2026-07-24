/**
 * 2_1: Assets and Scorers - アセット管理と評価関数
 *
 * TypeScript 対応: 一部対応
 * - Dataset / StringPrompt / MessagesPrompt / publish は TypeScript SDK で扱います。
 * - weave.Model は現状 Python SDK の API です。TypeScript SDK には public export されていません。
 * - Python の weave.Model / weave.Scorer 継承は、TypeScript では設定 object と function-based scorer に置き換えます。
 * - Built-in scorers は公式ドキュメント上、Python SDK のみです。
 */

import * as weave from "weave";

import {
  chatCompletion,
  getModelName,
  getOpenAIClient,
  initWeave,
  printSection,
} from "../src/config.js";

type GrammarRow = {
  id: string;
  sentence: string;
  correction: string;
};

type GrammarOutput = {
  corrected: string;
};

const client = await initWeave();

// =============================================================================
// SECTION 1: Model Config + Traced Function
// =============================================================================
printSection("1. Model Config + traced function - LLM ラッパーのバージョン管理");
console.log(`
weave.Model は現状 Python SDK の API です。
TypeScript SDK には public export されていないため、この教材では
model config object と traced function の組み合わせで表現します。
`);

const grammarCorrectorConfigV2 = {
  objectType: "grammar_corrector_config",
  systemMessage: "You are an expert grammar checker. Return only the corrected sentence, no explanation.",
  modelName: getModelName(),
  temperature: 0,
};

const correctGrammar = weave.op(async function correctGrammar(sentence: string): Promise<GrammarOutput> {
  const response = await getOpenAIClient().chat.completions.create({
    model: grammarCorrectorConfigV2.modelName,
    messages: [
      { role: "system", content: grammarCorrectorConfigV2.systemMessage },
      { role: "user", content: sentence },
    ],
    temperature: grammarCorrectorConfigV2.temperature,
  });
  return { corrected: response.choices[0]?.message?.content?.trim() ?? "" };
});

const modelResult = await correctGrammar("I has a big dog.");
console.log(`Corrected: ${JSON.stringify(modelResult)}`);
console.log(`
注意:
- この config object はローカルの設定値です。
- TypeScript SDK には weave.Model がないため、これを Weave の Model asset として publish していません。
- correctGrammar(...) の実行内容は Weave の Traces に記録されます。
`);

// =============================================================================
// SECTION 2: Prompt Assets
// =============================================================================
printSection("2. StringPrompt / MessagesPrompt - プロンプト管理");

const systemPrompt = new weave.StringPrompt({
  content: "You speak like a friendly pirate.",
});
const promptRef = await client.publish(systemPrompt, "pirate_prompt_ts");
console.log(`Published StringPrompt: ${promptRef.uri()}`);

const pirateResponse = await chatCompletion(
  [
    { role: "system", content: systemPrompt.format() },
    { role: "user", content: "What is machine learning?" },
  ],
  { maxTokens: 80 }
);
console.log(`StringPrompt response: ${pirateResponse.slice(0, 100)}...`);

const messagesPrompt = new weave.MessagesPrompt({
  messages: [
    { role: "system", content: "You are a helpful assistant specializing in {domain}." },
    { role: "user", content: "{question}" },
  ],
});
const messagesPromptRef = await client.publish(messagesPrompt, "domain_expert_prompt_ts");
console.log(`Published MessagesPrompt: ${messagesPromptRef.uri()}`);

const formattedMessages = messagesPrompt.format({
  domain: "machine learning",
  question: "What is overfitting?",
});
const promptResponse = await chatCompletion(formattedMessages as any, { maxTokens: 80 });
console.log(`MessagesPrompt response: ${promptResponse.slice(0, 100)}...`);

// =============================================================================
// SECTION 3: Dataset Asset
// =============================================================================
printSection("3. Dataset - データセットの作成・保存");

const grammarDataset = new weave.Dataset<GrammarRow>({
  name: "grammar_benchmark_ts",
  rows: [
    { id: "0", sentence: "He no likes ice cream.", correction: "He doesn't like ice cream." },
    { id: "1", sentence: "She goed to the store.", correction: "She went to the store." },
    { id: "2", sentence: "They was playing outside.", correction: "They were playing outside." },
    { id: "3", sentence: "I has a big dog.", correction: "I have a big dog." },
    { id: "4", sentence: "We runned very fast.", correction: "We ran very fast." },
  ],
});
const datasetRef = await grammarDataset.save();
console.log(`Published dataset: ${datasetRef.uri()}`);
console.log(`Dataset rows: ${grammarDataset.length}`);
console.log(`First row: ${JSON.stringify(grammarDataset.getRow(0))}`);

// =============================================================================
// SECTION 4: Function-based Scorers
// =============================================================================
printSection("4. Function-based Scorers - 関数ベース");

const exactMatchScorer = weave.op(
  function exactMatchScorer({
    modelOutput,
    datasetRow,
  }: {
    modelOutput: GrammarOutput;
    datasetRow: GrammarRow;
  }) {
    return {
      exact_match: modelOutput.corrected.toLowerCase().trim() === datasetRow.correction.toLowerCase().trim(),
    };
  },
  { name: "exact_match_scorer_ts" }
);

const containsAnswerScorer = weave.op(
  function containsAnswerScorer({
    modelOutput,
    datasetRow,
  }: {
    modelOutput: GrammarOutput;
    datasetRow: GrammarRow;
  }) {
    return {
      contains_answer: modelOutput.corrected.toLowerCase().includes(datasetRow.correction.toLowerCase()),
    };
  },
  { name: "contains_answer_scorer_ts" }
);

console.log(
  `Exact match sample: ${JSON.stringify(
    await exactMatchScorer({
      modelOutput: { corrected: "I have a big dog." },
      datasetRow: grammarDataset.getRow(3),
    })
  )}`
);
console.log(
  `Contains sample: ${JSON.stringify(
    await containsAnswerScorer({
      modelOutput: { corrected: "I have a big dog." },
      datasetRow: grammarDataset.getRow(3),
    })
  )}`
);

// =============================================================================
// SECTION 5: Built-in Scorers Notes
// =============================================================================
printSection("5. Built-in Scorers - TypeScript 版での扱い");
console.log(`
Weave の Built-in / local scorers は Python SDK のみです。
TypeScript では上の exactMatchScorer のように function-based scorer を作り、
Evaluation に渡します。
`);

// =============================================================================
// COMPLETE
// =============================================================================
printSection("Assets and Scorers Demo Complete!");
console.log(`
まとめ:
- Dataset / Prompt は TypeScript SDK で保存可能
- weave.Model は現状 Python SDK のみ。TypeScript では Model asset として保存せず、traced function で実行を記録
- Python の weave.Scorer class / built-in scorers は function-based scorer に置換
`);
