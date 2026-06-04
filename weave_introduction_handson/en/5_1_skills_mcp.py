"""
5_1: W&B Skills / MCP - Use W&B from AI agents

==========================================================
What this section covers
==========================================================

This section introduces W&B Skills and the W&B MCP Server as useful ways
for AI agents to access W&B and Weave context.

W&B Skills:
   A collection of reusable instructions that teach AI coding agents how to
   inspect W&B / Weave projects and interpret experiment results.

W&B MCP Server:
   A Model Context Protocol server that lets IDEs, coding agents, and chat
   agents query W&B Runs, Traces, Evaluations, Artifacts, and documentation
   in natural language.

==========================================================
Why this is useful
==========================================================

1. Ask an agent to investigate traces
   - Find failed traces
   - Inspect errors, inputs, outputs, and latency
   - Identify which tool call failed

2. Summarize evaluation results
   - Inspect the latest Evaluation
   - Extract low-scoring examples
   - Identify which Scorers are failing

3. Turn experiment results into improvements
   - Suggest prompt changes
   - Propose new Dataset examples
   - Improve Guardrails or Scorers

4. Avoid copy-pasting W&B data
   - Let your IDE or agent access W&B through MCP
   - Query Runs, Traces, Evaluations, and Artifacts in natural language

==========================================================
MCP Server usage model
==========================================================

The W&B MCP Server can be used in two deployment modes.

Hosted server:
   A W&B-managed MCP server that clients connect to over HTTP.
   This is the easiest option to try first.

Local install:
   Run the MCP server on your own machine.
   Use this when you need more isolation or local development.

For Dedicated Cloud or Self-Managed environments, the MCP URL may differ
from the standard SaaS URL. Ask your administrator or W&B contact if needed.

==========================================================
References
==========================================================

W&B Skills:
https://github.com/wandb/skills

W&B MCP Server:
https://docs.wandb.ai/platform/mcp-server

==========================================================
Note
==========================================================

- This script only prints an overview
- Actual setup depends on your IDE or agent environment
- When using MCP, set `WANDB_API_KEY` and, if needed, `WANDB_BASE_URL`
"""

print(__doc__)
