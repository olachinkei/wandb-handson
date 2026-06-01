# W&B Weave Hands-on

[Japanese Version](README.md)

## Overview
This repository contains hands-on materials for learning W&B Weave - a framework for tracking, evaluating, and monitoring LLM applications.

For those new to Weave, please refer to [this page](https://wandbai.notion.site/How-to-start-W-B-Models-and-Weave-4ebc2500493a47ad8307da1748dced57?source=copy_link) for comprehensive resources including [Weave demo (10 minutes)](https://www.youtube.com/watch?v=tRGoT1QV8VA) and [Weave documentation](https://wandb.me/weave).

---

## What You'll Learn

### 1. Tracing
- `1_1` Basic Tracing (@weave.op, Library Integration, Error Tracking)
- `1_2` Agent SDK (Tool Calls, Threads)
- `1_3` Multimodal - OpenAI (Image, Audio, PDF)
- `1_4` Advanced Tracing (Display Name, Attributes, PII Redaction, Sampling)

### 2. Asset Management
- `2_1_assets` Asset management and scorer creation (Model, Prompt, Dataset, Scorer)

### 3. Evaluation
- `3_1` Offline Evaluation (weave.Evaluation, multiple scorers)
- `3_2` EvaluationLogger (Flexible batch evaluation)

### 4. Monitoring
- `4_1` Online Feedback (Reactions, Notes, Custom Feedback)
- `4_2` Guardrails and Monitoring (Using Scorers as guardrails)

---


## Environment Setup & Prerequisites

### Setup Steps

**Using uv (recommended):**
```bash
cd weave_introduction_handson
uv sync
```

**Using pip:**
```bash
cd weave_introduction_handson
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```env
# Required
WANDB_API_KEY=your_wandb_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional
WANDB_ENTITY=your_team_name
WANDB_PROJECT=weave-handson

# For Dedicated Cloud or On-premises
WANDB_BASE_URL=https://your-instance.wandb.io
```

**Note**: If using Dedicated Cloud or on-premises environment, set `WANDB_BASE_URL` to your instance URL.

### Verification

Run the verification script:

**Using uv:**
```bash
uv run python jp/1_1_basic_trace.py
```

**Using pip:**
```bash
python jp/1_1_basic_trace.py
```

Success message:
```
============================================================
Basic Trace Demo Complete!
============================================================
```

---

## Project Structure

```
jp/  (Japanese version)
├── config_loader.py                # LLM configuration loader
├── 1_1_basic_trace.py              # Basic tracing
├── 1_2_agent_sdk.py                # Agent SDK
├── 1_3_multimodal_openai.py        # Multimodal - OpenAI
├── 1_4_advanced_trace.py           # Advanced tracing
├── 2_1_assets.py                   # Asset management and scorer creation
├── 3_1_evaluation.py              # Offline evaluation
├── 3_2_evaluation_logger.py       # EvaluationLogger
├── 4_1_online_feedback.py         # Online feedback
└── 4_2_guardrail_monitoring.py    # Guardrails

en/  (English version)
```

---

## Running Scripts

**Using uv:**
```bash
uv run python jp/1_1_basic_trace.py
```

**Using pip:**
```bash
python jp/1_1_basic_trace.py
```

---

## Additional Environment Variables

See [official documentation](https://docs.wandb.ai/weave/guides/core-types/env-vars) for details.

| Variable | Default | Description |
|----------|---------|-------------|
| `WEAVE_DISABLED` | false | Disable tracing |
| `WEAVE_PRINT_CALL_LINK` | true | Print UI links |
| `WEAVE_PARALLELISM` | 20 | Evaluation parallelism |

---

## Resources

- **Documentation**: [W&B Weave Documentation](https://weave-docs.wandb.ai/)
- **Videos**:
  - [Japanese Tutorial](https://www.youtube.com/watch?v=Ua0Wx9fqhDo&t=295s)
  - [English Tutorial](https://www.youtube.com/watch?v=sJNjw6U2Tvg&t=522s)
