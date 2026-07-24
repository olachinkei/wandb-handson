# Weave Introduction Hands-on TypeScript

W&B Weave を TypeScript / Node.js から使うためのハンズオンです。

元の Python 版 `weave_introduction_handson` をベースにしていますが、Python SDK と TypeScript SDK では対応している API が完全には同じではありません。この TypeScript 版では、実行できるもの、TypeScript では代替実装になるもの、現時点では未対応として説明だけにしているものを明確に分けています。

詳しい対応表は [docs/typescript-support.md](docs/typescript-support.md) も確認してください。

## セットアップ

```bash
cd wandb-handson/weave_introduction_handson_typescript
npm install
cp .env.example .env
```

`.env` に最低限、次の 2 つを設定します。

```bash
WANDB_API_KEY=...
OPENAI_API_KEY=...
```

Team project に trace を保存する場合は `WANDB_ENTITY` も設定します。

```bash
WANDB_ENTITY=your_team_name
WANDB_PROJECT=weave-handson-typescript
```

Dedicated Cloud / self-managed W&B を使う場合は `WANDB_BASE_URL` も設定してください。

```bash
WANDB_BASE_URL=https://your-instance.wandb.io
```

`RUN_EXPENSIVE_MULTIMODAL=1` は `.env.example` でデフォルト設定しています。`1_3_multimodal_openai.ts` で画像生成や音声生成を実行するためのフラグです。

## 実行方法

TypeScript のソースコードは `jp/*.ts` にあります。Node.js は通常そのまま `.ts` を実行しないため、まず `npm run build` で JavaScript に変換します。

変換後のファイルは `dist/jp/*.js` に出力されます。

例:

```text
jp/1_1_basic_trace.ts
-> dist/jp/1_1_basic_trace.js
```

よく使う章は `package.json` にショートカットを用意しています。

```bash
npm run run:1_1
npm run run:1_2
npm run run:1_3
npm run run:1_4
npm run run:2_1
npm run run:3_1
npm run run:3_2
npm run run:4_2
npm run run:4_3
```

たとえば `npm run run:1_1` は内部的には次と同じです。

```bash
npm run build
node --import=weave/instrument dist/jp/1_1_basic_trace.js
```

## `node --import=weave/instrument` とは

TypeScript SDK の OpenAI integration では、アプリ本体より先に Weave の計装コードを読み込む必要があります。

そのため、この教材ではビルド後の JavaScript を次の形で起動します。

```bash
node --import=weave/instrument dist/jp/1_1_basic_trace.js
```

`--import=weave/instrument` は Node.js の ESM preload です。OpenAI SDK が読み込まれる前に Weave の instrument を先に読み込み、`openai.chat.completions.create(...)` などの呼び出しを自動 trace できるようにします。

`weave.op(...)` で明示的に包んだ通常の関数は、基本的にこの自動計装とは別に trace されます。一方で OpenAI SDK などの library integration を安定して trace するには、この `--import` 付きで起動するのが重要です。

Node.js のバージョンによっては、Weave 側の instrument 読み込み時に `DEP0205` の deprecation warning が表示されることがあります。ハンズオンの実行自体や trace 記録が成功していれば、その警告は Node.js / SDK 側の警告として扱ってください。

## TypeScript / ESM について

このプロジェクトは `package.json` で `"type": "module"` を指定しているため、Node.js の ESM として動きます。

そのため、import は次のように書きます。

```ts
import { OpenAI } from "openai";
import * as weave from "weave";
import { initWeave } from "../src/config.js";
```

TypeScript のソースでは `../src/config.js` のように `.js` 拡張子で import しています。これは ESM の実行時にはビルド後の JavaScript ファイルを読むためです。ソースは `.ts` ですが、実行されるのは `dist/src/config.js` です。

## `await` の考え方

`await` は「Promise が完了するまで待つ」ための JavaScript / TypeScript の書き方です。Weave 専用の書き方ではありません。

同期関数を `weave.op(...)` で包んだだけなら、通常は `await` は不要です。

```ts
const echo = weave.op(function echo(text: string): string {
  return text;
});

const result = echo("hello");
```

OpenAI API 呼び出しのように非同期処理をする関数は `async` になり、呼び出し側で `await` が必要です。

```ts
const answer = await openai.chat.completions.create({
  model: "gpt-4o-mini",
  messages: [{ role: "user", content: "Hello" }],
});
```

## Agenda

### 1. Tracing

| 章 | ファイル | TypeScript 対応 | 内容 |
| --- | --- | --- | --- |
| `1_1` | `jp/1_1_basic_trace.ts` | 対応 | 基本的な `weave.op(...)`、OpenAI SDK integration、nested op |
| `1_2` | `jp/1_2_agent_sdk.ts` | 対応 | OpenAI Agents SDK integration。Agent run / tool call / model call を trace |
| `1_3` | `jp/1_3_multimodal_openai.ts` | 一部対応 | PNG / WAV は TypeScript helper で media preview。JPG / MP3 / MP4 / PDF / HTML は未対応説明のみ |
| `1_4` | `jp/1_4_advanced_trace.ts` | 一部対応 | display name / attributes は対応。cost / Presidio PII redaction / sampling は SDK-level API 未対応 |

### 2. Asset Management

| 章 | ファイル | TypeScript 対応 | 内容 |
| --- | --- | --- | --- |
| `2_1` | `jp/2_1_assets.ts` | 一部対応 | Dataset、Prompt、function-based scorer は対応。`weave.Model` は現状 Python SDK のみ |

TypeScript SDK では `weave.Model` が public export されていないため、この教材では Model asset として保存せず、モデル実行を traced function として記録します。

### 3. Evaluation

| 章 | ファイル | TypeScript 対応 | 内容 |
| --- | --- | --- | --- |
| `3_1` | `jp/3_1_evaluation.ts` | 対応 | `weave.Evaluation`。同じ eval 名 / model 名で、弱い prompt と強い prompt を比較 |
| `3_2` | `jp/3_2_evaluation_logger.ts` | 対応 | `EvaluationLogger` / `ScoreLogger` による逐次 logging |
| `3_3` | `jp/3_3_annotation_queue.ts` | UI 機能 | Annotation Queue の使い方を説明 |

### 4. Monitoring

| 章 | ファイル | TypeScript 対応 | 内容 |
| --- | --- | --- | --- |
| `4_1` | `jp/4_1_online_feedback.ts` | 説明のみ | Python の高水準 feedback API 中心 |
| `4_2` | `jp/4_2_guardrail_monitoring.ts` | 未対応 | Python の `Scorer` class / `call.apply_scorer()` guardrail API は TypeScript SDK-level API として未対応 |
| `4_3` | `jp/4_3_monitors.ts` | 一部対応 | monitor 対象 op と trace は TypeScript で作成。Custom Monitor は Weave UI で設定 |

### 5. その他便利な機能

`5_1` から `5_6` は、W&B Skills / MCP、Automations、Dynamic Leaderboards、Trace Plots、Saved Views、Playground の説明を TypeScript 版の文脈に合わせて移植しています。

## 参考

- W&B Weave TypeScript SDK: https://docs.wandb.ai/weave/reference/typescript-sdk
- TypeScript SDK integration guide: https://docs.wandb.ai/weave/guides/integrations/js
- Attributes TypeScript guide: https://docs.wandb.ai/weave/guides/tools/attributes#typescript
- EvaluationLogger TypeScript guide: https://docs.wandb.ai/weave/guides/evaluation/evaluation_logger#typescript
- Custom Monitors: https://docs.wandb.ai/weave/guides/evaluation/custom-monitors
- Built-in scorers: https://docs.wandb.ai/weave/guides/evaluation/builtin_scorers
