# Weave Introduction Hands-on

[Japanese Version](README.md)

This is a hands-on guide for learning Trace, evaluation, and monitoring with W&B Weave.

## New to Weave?

For an overview of Weave features and value, see the [W&B Weave documentation](https://docs.wandb.ai/weave).

## W&B Account and Environment Setup

Before starting the hands-on, create a W&B account and obtain your API key.

The account setup process depends on your environment.

- **W&B Multitenant SaaS**
  - Go to [https://wandb.ai/](https://wandb.ai/) and create an account.
- **Dedicated Cloud or on-premises**
  - Your administrator creates your user account. Ask your administrator to issue an account for you.
  - Log in from the link in the email you receive after the account is created.
  - Set the `WANDB_BASE_URL` environment variable to the URL provided by W&B.
  - If login fails, a missing `WANDB_BASE_URL` is a common cause. Ask your administrator or W&B engineer for the correct URL.

**Team-Based Workspace Management**

W&B organizes work by Team, Project, Run (W&B Models), and Trace (W&B Weave). A Team is the collaboration unit, and results are shared with members in the same Team. A Project is a folder-like unit under a Team.

In Enterprise environments, only Admins can create Teams. Ask your Admin for an existing Team name or request a new Team. On the Free plan, you can create one Team.

<img src="img/whatisteam.png" alt="What is a Team" width="640">

## Hands-on Agenda

### 1. Tracing

- `1_1` Basic tracing (@weave.op, Library Integration, error tracking)
- `1_2` Agent SDK (tool calls, Threads)
- `1_3` Multimodal - OpenAI (image, audio, PDF)
- `1_4` Advanced tracing (Display Name, Attributes, PII Redaction, Sampling)
- `1_5` Playground (prompt experimentation: [documentation](https://docs.wandb.ai/weave/guides/tools/playground#use-the-playground-to-experiment-with-prompts))
- `1_6` W&B Skills (W&B skills for AI agents: [wandb/skills](https://github.com/wandb/skills))

**Note: Agent Tracing**

For agent applications, it is important to trace not only LLM calls, but also tool execution, subtasks, and multi-step decision making. Weave is developing new Agent Trace features, currently available as Public Preview.

In this hands-on, `1_2` covers the basic integration between OpenAI Agents SDK and Weave. Public Preview Agent Trace features may change, so refer to the [official Agent Trace documentation](https://docs.wandb.ai/weave/guides/tracking/trace-agents) when using them.

### 2. Asset Management

- `2_1_assets` Asset management and Scorer creation (Model, Prompt, Dataset, Scorer)

### 3. Evaluation

- `3_1` Offline evaluation (`weave.Evaluation`, multiple Scorers)
- `3_2` EvaluationLogger (flexible batch evaluation)
- `3_3` Annotation Queue / Review ([documentation](https://docs.wandb.ai/weave/guides/tracking/annotation-review#annotation-workflow))
- `3_4` Monitors (continuous evaluation of production Traces with Scorers / built-in signals: [documentation](https://docs.wandb.ai/weave/guides/evaluation/monitors))

### 4. Monitoring

- `4_1` Online feedback (Reaction, Note, custom feedback)
- `4_2` Guardrails and monitoring (using Scorers as guardrails)

## Environment Setup and Running Scripts

Before starting the hands-on, confirm that your environment is correctly configured.

### Setup Steps

**1. Move to the project directory**

```bash
cd weave_introduction_handson
```

**2. Set environment variables**

After obtaining your W&B and OpenAI API keys, set them as environment variables. For local execution, creating a `.env` file at the project root is the simplest option.

```env
# Required
WANDB_API_KEY=your_wandb_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional
WANDB_ENTITY=your_team_name
WANDB_PROJECT=weave-handson

# For Dedicated Cloud or on-premises
WANDB_BASE_URL=https://your-instance.wandb.io
```

**Note:** If you use Dedicated Cloud or an on-premises environment, set `WANDB_BASE_URL` to your instance URL.

**Useful environment variables:**

Details: [official documentation](https://docs.wandb.ai/weave/guides/core-types/env-vars)

| Variable | Default | Description |
| --- | --- | --- |
| `WEAVE_DISABLED` | `false` | Disable tracing |
| `WEAVE_PRINT_CALL_LINK` | `true` | Print UI links |
| `WEAVE_PARALLELISM` | `20` | Evaluation parallelism |

**3. Install dependencies**

**Using uv (recommended):**

```bash
uv sync
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

**Using pip:**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**4. Run a script**

If your virtual environment is activated, you can run scripts without prefixing each command with `uv`.

```bash
python en/1_1_basic_trace.py
```

The run is successful if you see:

```text
============================================================
Basic Trace Demo Complete!
============================================================
```

If this message does not appear, check the error message and review your environment variables and dependencies.

## Resources

- **Documentation**: [W&B Weave Documentation](https://docs.wandb.ai/weave)
- **W&B Skills**: [wandb/skills](https://github.com/wandb/skills)
- **W&B MCP Server**: [MCP Server Documentation](https://docs.wandb.ai/platform/mcp-server)
- **Agent Trace**: [Trace agents](https://docs.wandb.ai/weave/guides/tracking/trace-agents)
- **Built-in Scorers**: [Built-in Scorers](https://docs.wandb.ai/weave/guides/evaluation/builtin_scorers)
- **Environment Variables**: [Environment Variables](https://docs.wandb.ai/weave/guides/core-types/env-vars)
- **Videos**:
  - [Japanese Tutorial](https://www.youtube.com/watch?v=Ua0Wx9fqhDo&t=295s)
  - [English Tutorial](https://www.youtube.com/watch?v=sJNjw6U2Tvg&t=522s)
