# Weave Introduction Hands-on TypeScript

W&B Weave を TypeScript / Node.js から使うためのハンズオンです。元の Python 版 `weave_introduction_handson` をベースに、TypeScript SDK で実行できる章と、Python SDK 専用または UI 操作中心の章を分けています。

詳しい対応状況は [docs/typescript-support.md](docs/typescript-support.md) を確認してください。

## セットアップ

```bash
cd /Users/keisuke/Project/wandb-handson/weave_introduction_handson_typescript
npm install
cp .env.example .env
```

`.env` に `WANDB_API_KEY` と `OPENAI_API_KEY` を設定します。Team を使う場合は `WANDB_ENTITY`、Dedicated Cloud / self-managed を使う場合は `WANDB_BASE_URL` も設定してください。

## 実行方法

TypeScript のソースコードは `jp/*.ts` にあります。Node.js はそのまま `.ts` を実行しないため、まず `npm run build` で JavaScript に変換します。変換後のファイルは `dist/jp/*.js` に出力されます。

Weave の TypeScript SDK では、OpenAI SDK などを自動でトレースするために、アプリ本体より先に Weave の計装コードを読み込む必要があります。そのため、ビルド後の JavaScript は `node --import=weave/instrument ...` で起動します。

たとえば `jp/1_1_basic_trace.ts` は、ビルド後に `dist/jp/1_1_basic_trace.js` になり、次のように実行されます。

```bash
npm run build
node --import=weave/instrument dist/jp/1_1_basic_trace.js
```

`--import=weave/instrument` は、OpenAI SDK が読み込まれる前に Weave の自動計装を有効化するための Node.js オプションです。これを付けることで、`weave.op(...)` で囲んだ関数だけでなく、OpenAI SDK の呼び出しも Weave の Trace として記録されやすくなります。

## OpenAI integration のバージョン注意

この教材では **通常の OpenAI SDK integration を優先** しています。検証時点では、次の最新系の組み合わせで OpenAI SDK の呼び出しが Library Integration として trace されることを確認しています。

```json
{
  "openai": "^6.42.0",
  "weave": "^0.15.1"
}
```

OpenAI client は通常の OpenAI SDK と同じように作成します。この教材では named import を使っています。

```ts
import { OpenAI } from "openai";

const openai = new OpenAI();
```

この形にすると、`node --import=weave/instrument ...` で起動したときに `openai.chat.completions.create(...)` が `openai.chat.completions.create` という子 Trace として記録されます。

注意点:

- `weave@0.9.3` では `openai@6` の自動 trace が期待通りに動かないケースがありました。`openai@6` を使う場合は `weave@0.15.1` 以降を使ってください。
- 最新 Weave では、patched function に `__isOp` が付くとは限りません。検証では `openai.chat.completions.create` が `wrappedWithAgents` に置き換わることを確認しています。
- OpenAI Agents SDK integration は `1_2_agent_sdk.ts` で実行例として扱っています。
- TypeScript で Agent SDK integration が必要な場合は、W&B までご連絡ください。

よく使う章は `package.json` にショートカットを用意しています。

```bash
npm run run:1_1
npm run run:1_2
npm run run:3_1
```

`npm run run:1_1` は内部的には次と同じです。

```bash
npm run build
node --import=weave/instrument dist/jp/1_1_basic_trace.js
```

## Agenda

### 1. Tracing

- `1_1` 基本的なトレーシング: 対応
- `1_2` OpenAI Agents SDK Integration: 対応。`@openai/agents` と `weave.instrumentOpenAIAgents()` を使用
- `1_3` マルチモーダル: Python は PNG / JPG / MP3 / MP4 / PDF / HTML を media preview として trace。TypeScript は PNG / WAV は対応、JPG / MP3 / MP4 / PDF / HTML は metadata trace のみ
- `1_4` 高度なトレーシング: display name と attributes は対応。cost / Presidio PII redaction / sampling は TypeScript SDK-level API なし

### 2. Asset Management

- `2_1` Dataset、Prompt、function-based scorer は対応
- `weave.Model` は現状 Python SDK のみ。TypeScript では Model asset として保存せず、traced function の実行を Traces に記録。`weave.Scorer` 継承、built-in scorers も Python 版の説明として整理

### 3. Evaluation

- `3_1` `weave.Evaluation`: 対応
- `3_2` `EvaluationLogger`: 対応。`logPrediction()` / `logScore()` / `finish()` / `logSummary()` を使用
- `3_3` Annotation Queue: UI 機能として説明

### 4. Monitoring

- `4_1` Online Feedback: Python の高水準 feedback API 中心のため説明のみ
- `4_2` Guardrails: TypeScript SDK-level API は未対応
- `4_3` Custom Monitors: TypeScript で monitor 対象 op と trace を作成。Custom Monitor の作成、judge model、prompt、sampling rate は Weave UI で設定

### 5. その他便利な機能

`5_1` から `5_6` は、W&B Skills / MCP、Automations、Dynamic Leaderboards、Trace Plots、Saved Views、Playground の説明を TypeScript 版の文脈に合わせて移植しています。

## 参考

- W&B Weave TypeScript SDK: https://docs.wandb.ai/weave/reference/typescript-sdk
- TypeScript SDK integration guide: https://docs.wandb.ai/weave/guides/integrations/js
- Built-in scorers: https://docs.wandb.ai/weave/guides/evaluation/builtin_scorers

OpenAI Agents SDK integration は `1_2_agent_sdk.ts` で扱います。CrewAI、AutoGen、LlamaIndex、LangChain など Python 側で対応している他の Agent / orchestration integration について、TypeScript 対応の要望がある場合は W&B までご連絡ください。
