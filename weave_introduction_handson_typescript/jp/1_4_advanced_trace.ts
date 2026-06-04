/**
 * 1_4: Advanced Trace - 高度なトレーシング
 *
 * TypeScript 対応: 一部対応
 * - display name: weave.op(fn, { name }) で対応
 * - attributes: init(..., { globalAttributes }) と withAttributes() で対応
 * - custom cost / Presidio PII redaction / tracing_sample_rate は
 *   Python 版と同じ高水準 API としては扱いません
 */

import { randomUUID } from "node:crypto";
import * as weave from "weave";

import { chatCompletion, initWeave, printSection } from "../src/config.js";

const weaveClient = await initWeave({
  globalAttributes: {
    env: process.env.NODE_ENV ?? "development",
    app_version: "typescript-handson",
    language: "typescript",
  },
});

// =============================================================================
// SECTION 1: Custom Display Name
// =============================================================================
printSection("1. Custom Display Name - トレースの表示名をカスタマイズ");

const analyzeSentiment = weave.op(
  async function analyzeSentiment(text: string): Promise<string> {
    return chatCompletion([
      { role: "system", content: "Analyze sentiment. Return: positive/negative/neutral" },
      { role: "user", content: text },
    ]);
  },
  { name: "sentiment_analyzer" }
);

const sentiment = await analyzeSentiment("I love this product!");
console.log(`Sentiment: ${sentiment.slice(0, 60)}...`);

// =============================================================================
// SECTION 2: Custom Cost Tracking
// =============================================================================
printSection("2. Custom Cost Tracking - TypeScript 版での扱い");
console.log(`
Python 版では client.query_costs() / client.add_cost() を使っています。
TypeScript SDK の公開 reference では同等の高水準 API の用意はまだございません。
`);

// =============================================================================
// SECTION 3: Attributes
// =============================================================================
printSection("3. Attributes - globalAttributes / withAttributes");

const processRequest = weave.op(async function processRequest(text: string): Promise<string> {
  console.log("Attributes inside op:", weaveClient.getCurrentAttributes());
  return chatCompletion([
    { role: "system", content: "Summarize briefly." },
    { role: "user", content: text },
  ]);
});

console.log("Global attributes:", weaveClient.getCurrentAttributes());

const attributeResult = await weave.withAttributes(
  {
    tenant: "demo-customer",
    experiment: "attributes-typescript",
    request_id: randomUUID(),
  },
  async () => {
    console.log("Per-call attributes:", weaveClient.getCurrentAttributes());
    return processRequest("This is a test message.");
  }
);
console.log(`Result: ${attributeResult.slice(0, 80)}...`);

const nestedAttributeResult = await weave.withAttributes(
  {
    tenant: "demo-customer",
    experiment: "attributes-typescript",
    version: "1.0.0",
  },
  async () =>
    weave.withAttributes(
      {
        version: "1.1.0",
        cohort: "nested-attributes",
      },
      async () => processRequest("This message is traced with nested attributes.")
    )
);
console.log(`Nested result: ${nestedAttributeResult.slice(0, 80)}...`);

// =============================================================================
// SECTION 4: PII Redaction
// =============================================================================
printSection("4. PII Redaction - TypeScript SDK-level API は未対応");

console.log(`
TypeScript SDK の weave.op options には、Python 版の postprocess_inputs /
postprocess_output や Microsoft Presidio redaction と同等の API はありません。

Python 版:
- weave.init(..., settings={"redact_pii": True})
- @weave.op(postprocess_inputs=..., postprocess_output=...)
- weave.utils.sanitize.add_redact_key(...)

TypeScript 版:
- 上記と同等の SDK-level redaction API はありません。
- raw な PII や password を traced op に渡さないでください。
`);

// =============================================================================
// SECTION 5: Threads
// =============================================================================
printSection("5. Threads - TypeScript 版での扱い");
console.log(`
Python 版の weave.thread(session_id) と同じ high-level helper は、TypeScript 版では提供されていません。
会話 ID を attributes として付与すると、TypeScript でも filter / grouping の足がかりにできます。
`);

const sendMessage = weave.op(async function sendMessage(userMessage: string): Promise<string> {
  return chatCompletion([
    { role: "system", content: "You are helpful." },
    { role: "user", content: userMessage },
  ]);
});

const sessionId = randomUUID();
console.log(`Session ID example: ${sessionId}`);
const turn1 = await weave.withAttributes(
  { session_id: sessionId, turn: 1 },
  async () => sendMessage("What is AI?")
);
console.log(`Turn 1: ${turn1.slice(0, 80)}...`);
const turn2 = await weave.withAttributes(
  { session_id: sessionId, turn: 2 },
  async () => sendMessage("Give an example.")
);
console.log(`Turn 2: ${turn2.slice(0, 80)}...`);

// =============================================================================
// SECTION 6: Sampling Rate
// =============================================================================
printSection("6. Sampling Rate - TypeScript SDK-level API は未対応");

console.log(`
Python 版では @weave.op(tracing_sample_rate=0.1) のように、op 自体に
sampling rate を指定できます。

TypeScript SDK の OpOptions / SettingsInit には tracing_sample_rate や
sampling rate 相当の公開 API はありません。
`);

// =============================================================================
// COMPLETE
// =============================================================================
printSection("Advanced Trace Demo Complete!");
console.log(`
まとめ:
- name: weave.op(fn, { name }) で表示名をカスタマイズ
- attributes: globalAttributes と withAttributes() で trace に metadata を付与
- thread: session_id などを attributes として付与して filter / grouping に使う
- PII redaction は TypeScript SDK-level API なし
- sampling は TypeScript SDK-level API なし
`);
