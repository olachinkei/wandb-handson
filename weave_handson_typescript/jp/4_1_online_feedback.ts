/**
 * 4_1: Online Feedback - オンラインフィードバック
 *
 * TypeScript 対応: Python API 中心
 * - Python 版の call.feedback.add_reaction() / add_note() / add() に相当する
 *   高水準 TypeScript API は、この教材では扱いません。
 */

import * as weave from "weave";

import { chatCompletion, initWeave, printSection } from "../src/config.js";

await initWeave();

// =============================================================================
// SECTION 1: Feedback API Notes
// =============================================================================
printSection("1. Feedback API - TypeScript 版での扱い");

const answerQuestion = weave.op(async function answerQuestion(question: string): Promise<string> {
  return chatCompletion(
    [
      { role: "system", content: "Answer briefly and clearly." },
      { role: "user", content: question },
    ],
    { maxTokens: 120 }
  );
});

const answer = await answerQuestion("W&B Weave は何をするためのツールですか？");
console.log(`Answer: ${answer.slice(0, 120)}...`);

console.log(`
Python 版では:
- call.feedback.add_reaction()
- call.feedback.add_note()
- call.feedback.add()

を使って Trace に reaction / note / structured feedback を追加します。

この TypeScript 版では同等の高水準 API を実装対象外にし、
Trace を生成したあと Weave UI の Feedback 表示や Annotation Queue で扱う flow を推奨します。
`);
