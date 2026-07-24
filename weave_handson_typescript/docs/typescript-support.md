# TypeScript 対応状況

このディレクトリは `weave_introduction_handson` の TypeScript 版です。Python SDK と TypeScript SDK では API の粒度が違うため、章ごとに「そのまま移植」「TypeScript で代替」「Python 専用または UI 操作のみ」に分けています。

この対応表は、このディレクトリで実際にインストールして型チェックした `weave@0.15.1` を基準にしています。公式 TypeScript reference に掲載されていても、現行 npm package ではまだ Python SDK と同等ではない API があります。

## 対応マトリクス

| 元の章 | TypeScript 版 | 状態 | メモ |
| --- | --- | --- | --- |
| `1_1_basic_trace.py` | `jp/1_1_basic_trace.ts` | 対応 | `@weave.op()` ではなく `weave.op(fn, options)` を使用。ESM では `node --import=weave/instrument` で実行。 |
| `1_2_agent_sdk.py` | `jp/1_2_agent_sdk.ts` | 対応 | `@openai/agents` と `weave.instrumentOpenAIAgents()` を使って Agent run / tool call / model call を trace。 |
| `1_3_multimodal_openai.py` | `jp/1_3_multimodal_openai.ts` | 一部対応 | Python は PNG / JPG / MP3 / MP4 / PDF / HTML を `Content[Literal[...]]` で media preview として trace。TypeScript は PNG / WAV は helper 対応、JPG / MP3 / MP4 / PDF / HTML は metadata trace のみ。 |
| `1_4_advanced_trace.py` | `jp/1_4_advanced_trace.ts` | 一部対応 | display name と attributes は対応。attributes は `globalAttributes`、`withAttributes()`、`client.getCurrentAttributes()` を使用。custom cost、Presidio PII redaction、`tracing_sample_rate` は Python 版と同じ API では扱っていません。 |
| `2_1_assets.py` | `jp/2_1_assets.ts` | 一部対応 | `Dataset`、`StringPrompt`、`MessagesPrompt`、`client.publish()` は使用。`weave.Model` は現状 Python SDK の API で、TypeScript SDK には public export されていません。TypeScript では Model asset として保存せず、traced function の実行を Traces に記録します。`weave.Scorer` 継承も使わず function-based scorer に置換。 |
| `3_1_evaluation.py` | `jp/3_1_evaluation.ts` | 対応 | `Dataset`、`Evaluation`、function-based scorer で実装。 |
| `3_2_evaluation_logger.py` | `jp/3_2_evaluation_logger.ts` | 対応 | `EvaluationLogger` / `ScoreLogger` を使用。TypeScript では `logPrediction()` / `logScore()` / `finish()` の fire-and-forget pattern と `logSummary()` を使います。 |
| `3_3_annotation_queue.py` | `jp/3_3_annotation_queue.ts` | UI 機能 | TypeScript の Trace でも UI 上で利用。SDK 実装ではなく説明ファイル。 |
| `4_1_online_feedback.py` | `jp/4_1_online_feedback.ts` | Python API 中心 | Python の `call.feedback.add_reaction()` / `add_note()` 相当の高水準 TypeScript API はこの教材では扱いません。 |
| `4_2_guardrail_monitoring.py` | `jp/4_2_guardrail_monitoring.ts` | 未対応 | Python 版の `Scorer` class / `call.apply_scorer()` による guardrail API は TypeScript SDK-level API としては扱っていません。 |
| `4_3_monitors.py` | `jp/4_3_monitors.ts` | 一部対応 | TypeScript で monitor 対象 op と trace を作成。Custom Monitor の作成、judge model、prompt、sampling rate は Weave UI で設定。 |
| `5_1` - `5_6` | `jp/5_x_*.ts` | UI / 外部機能 | TypeScript 固有コードではなく、Weave UI や MCP / Skills の説明として移植。 |

## TypeScript で特に注意する点

- ESM では OpenAI などの自動計装を先に読み込む必要があります。この教材では `node --import=weave/instrument dist/...js` で実行します。
- OpenAI Library Integration は `weave@0.15.1` + `openai@6.42.0` で確認しています。OpenAI client は `import { OpenAI } from "openai"` の named import で作成します。
- `weave@0.9.3` では `openai@6` の自動 trace が期待通りに動かないケースがありました。`openai@6` を使う場合は `weave@0.15.1` 以降を使ってください。
- Python の decorator API は TypeScript では `weave.op(function name(...) { ... }, { name: "..." })` のように書きます。
- Built-in / local scorers は公式ドキュメント上、Python SDK のみです。TypeScript では function-based scorer を作ります。
- `weave.Model` は現状 Python SDK の API です。TypeScript SDK には public export されていないため、TypeScript 版では Model asset として保存しません。モデル実行は traced function として Traces に記録します。`weave.Scorer` 継承も使わず、function-based scorer を作ります。
- マルチモーダルは TypeScript SDK の `weaveImage` / `weaveAudio` helper を使います。現時点の型定義では `weaveImage` は PNG、`weaveAudio` は WAV のみです。JPG、MP3、MP4、PDF、HTML は Trace に通常 object としてメタデータを残すところまでにしています。
