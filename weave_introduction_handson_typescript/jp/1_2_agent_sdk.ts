/**
 * 1_2: OpenAI Agents SDK Integration - エージェント構築
 *
 * TypeScript 対応: 対応
 * - weave@0.15.1 以降では OpenAI Agents SDK integration が export されています。
 * - `node --import=weave/instrument ...` で起動すると、@openai/agents が自動計装されます。
 * - このスクリプトでは `instrumentOpenAIAgents()` も呼び、hook が効かない環境でも登録を試みます。
 */

import { Agent, run, tool } from "@openai/agents";
import { z } from "zod";
import * as weave from "weave";

import { getModelName, initWeave, printSection } from "../src/config.js";

await initWeave();

const agentsInstrumented = await weave.instrumentOpenAIAgents();
console.log(`OpenAI Agents instrumentation: ${agentsInstrumented ? "enabled" : "not available"}`);

// =============================================================================
// SECTION 1: Agent SDK Integration Status
// =============================================================================
printSection("1. Agent SDK Integration Status - Agent SDK 連携の状態");

console.log(`
この章では @openai/agents と Weave の TypeScript integration を扱います。

確認ポイント:
- Agent run が Weave Trace として記録される
- tool call が子 span / 子 call として見える
- underlying OpenAI model call も trace される

Python 版と同じく、Agent アプリケーションでは LLM call だけでなく、
tool execution や multi-step workflow の流れを追えることが重要です。
`);

// =============================================================================
// SECTION 2: Define Tools
// =============================================================================
printSection("2. Define Tools - ツール定義");

const searchDatabase = tool({
  name: "search_database",
  description: "Search a mock internal database for relevant research notes.",
  parameters: z.object({
    query: z.string().describe("Search query"),
  }),
  async execute({ query }) {
    return [
      { id: 1, title: `Result 1 for: ${query}`, score: 0.95 },
      { id: 2, title: `Result 2 for: ${query}`, score: 0.87 },
    ];
  },
});

const sendEmail = tool({
  name: "send_email",
  description: "Send a mock email to a recipient.",
  parameters: z.object({
    to: z.string().email().describe("Recipient email address"),
    subject: z.string().describe("Email subject"),
    body: z.string().describe("Email body"),
  }),
  async execute({ to, subject, body }) {
    return {
      status: "sent",
      to,
      subject,
      bodyPreview: body.slice(0, 80),
    };
  },
});

console.log("Defined tools: search_database, send_email");

// =============================================================================
// SECTION 3: Run Agent
// =============================================================================
printSection("3. Run Agent - エージェント実行");

const researchAgent = new Agent({
  name: "ResearchAssistant",
  model: getModelName(),
  instructions: `You are a research assistant.
Use search_database to find relevant information.
If the user asks to email results, call send_email with a concise summary.`,
  tools: [searchDatabase, sendEmail],
});

const result = await run(
  researchAgent,
  "Search for information about machine learning and email the results to user@example.com."
);

console.log(`Final output: ${String(result.finalOutput).slice(0, 300)}...`);

// =============================================================================
// COMPLETE
// =============================================================================
printSection("Agent SDK Integration Demo Complete!");
console.log(`
まとめ:
- @openai/agents の Agent / tool / run を使った workflow を実行
- weave.instrumentOpenAIAgents() で OpenAI Agents integration を有効化
- Weave UI で agent trace、tool call、underlying model call を確認

補足:
- Python では OpenAI Agents SDK、CrewAI、AutoGen、LlamaIndex、LangChain などの integration も利用できます。
- TypeScript で特定の Agent SDK integration が必要な場合は、W&B までご連絡ください。
`);
