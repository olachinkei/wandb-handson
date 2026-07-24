/**
 * 1_1: Basic Trace - 基本的なトレーシング
 *
 * TypeScript 対応: 対応
 * - Python の @weave.op() は、TypeScript では weave.op(fn, options) として書きます。
 * - OpenAI の自動計装は ESM 実行時に node --import=weave/instrument を使います。
 */

import * as weave from "weave";

import { chatCompletion, getOpenAIClient, initWeave, printSection } from "../src/config.js";

await initWeave();

// =============================================================================
// SECTION 1: Basic Function Tracing
// =============================================================================
printSection("1. Basic Function Tracing - 基本的な関数トレーシング");

function echoRaw(userInput: string): string {
  return `${userInput} ${userInput}`;
}

const rawEchoResult = echoRaw("hello");
console.log(`Raw echo result: ${rawEchoResult}`);

const echo = weave.op(echoRaw, { name: "echo" });

// Trace だけなら echo("hello") でも開始されますが、ここでは戻り値を表示するため await します。
const echoResult = await echo("hello");
console.log(`Traced echo result: ${echoResult}`);

// =============================================================================
// SECTION 2: Library Integration
// =============================================================================
printSection("2. Library Integration - LLM API の自動トラッキング");

console.log(`
Weave は OpenAI などの LLM ライブラリを自動的にトラッキングできます。
この TypeScript/ESM 版では node --import=weave/instrument で起動することで、
OpenAI SDK の呼び出しを自動計装します。
`);

const openai = getOpenAIClient();
const response = await openai.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [
    { role: "system", content: "You are a helpful assistant." },
    { role: "user", content: "Tell me a short joke." },
  ],
  max_tokens: 100,
});
console.log(`OpenAI response: ${response.choices[0]?.message?.content ?? ""}`);

// =============================================================================
// SECTION 3: Nested Function Tracing
// =============================================================================
printSection("3. Nested Function Tracing - ネストした関数呼び出し");

const extractDinos = weave.op(async function extractDinos(sentence: string): Promise<string> {
  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      {
        role: "system",
        content:
          "Extract any dinosaur name, common_name, and whether its diet is herbivore or carnivore. Return JSON only.",
      },
      { role: "user", content: sentence },
    ],
    response_format: { type: "json_object" },
  });
  return response.choices[0]?.message?.content ?? "{}";
});

const countDinos = weave.op(function countDinos(dinoData: string): number {
  const parsed = JSON.parse(dinoData) as Record<string, unknown>;
  return Object.keys(parsed).length;
});

const dinoTracker = weave.op(async function dinoTracker(sentence: string): Promise<{
  nDinos: number;
  dinoData: string;
}> {
  const dinoData = await extractDinos(sentence);
  const nDinos = await countDinos(dinoData);
  return { nDinos, dinoData };
});

const dinoSentence = `I watched as a Tyrannosaurus rex chased after a Triceratops,
both carnivore and herbivore locked in an ancient dance. Meanwhile, a gentle giant
Brachiosaurus calmly munched on treetops, blissfully unaware of the chaos below.`;

const dinoResult = await dinoTracker(dinoSentence);
console.log(`Dinosaur count: ${dinoResult.nDinos}`);
console.log(`Dinosaur data: ${dinoResult.dinoData}`);

// =============================================================================
// SECTION 4: Error Tracking
// =============================================================================
printSection("4. Error Tracking - エラートラッキング");

const parseJsonResponse = weave.op(async function parseJsonResponse(userInput: string): Promise<unknown> {
  // OpenAI の message content に渡す前に Promise を解決します。
  const echoed = await echo(userInput);
  const llmOutput = await chatCompletion([
    { role: "system", content: "Create a song. Return as plain text." },
    { role: "user", content: echoed },
  ]);
  return JSON.parse(llmOutput);
});

try {
  const parsed = await parseJsonResponse("hello world");
  console.log(`Parsed JSON: ${JSON.stringify(parsed)}`);
} catch (error) {
  console.log(`JSON parse error (expected): ${(error as Error).message}`);
}

// =============================================================================
// COMPLETE
// =============================================================================
printSection("Basic Trace Demo Complete!");
console.log(`
まとめ:
- weave.op(fn) で関数の入出力とエラーをトレース
- LLM API 呼び出しは Library Integration で自動記録
- ネストした呼び出しは親子関係として確認可能

Weave UI で確認:
- Traces タブで各 call の入出力、エラー、親子関係を確認
- Code タブでトラッキングされた関数定義を確認
`);
