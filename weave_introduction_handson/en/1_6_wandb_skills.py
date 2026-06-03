"""
1_6: W&B Skills - W&B skills for AI agents

==========================================================
What are W&B Skills?
==========================================================

W&B Skills are reusable instructions that teach AI coding agents how to
work with W&B and Weave.

They are useful when you want an agent to help with tasks such as:

- Inspecting W&B Runs
- Reviewing Weave Traces
- Summarizing Evaluation results
- Comparing model or prompt changes
- Suggesting next improvements from experiment results

In short, W&B Skills help move from "humans inspect W&B" to
"AI agents can also inspect W&B and help with development."

==========================================================
How this relates to this hands-on
==========================================================

This hands-on first teaches the core Weave workflow:

1. Use Traces to inspect LLM application behavior
2. Manage Models, Prompts, Datasets, and Scorers as Assets
3. Use Evaluation to measure output quality
4. Use Feedback and Guardrails to improve production behavior

W&B Skills are a next step after that.

They let an AI agent use the same W&B / Weave context that you inspect
in the UI. For example, you can ask an agent:

"Investigate why this Trace failed."
"Summarize the latest Evaluation results."
"Suggest a better Prompt based on failed examples."

==========================================================
Common use cases
==========================================================

1. Trace investigation
   - Find failed calls
   - Inspect inputs, outputs, exceptions, and latency
   - Identify which tool call failed

2. Evaluation analysis
   - Summarize recent evaluation results
   - Extract low-scoring examples
   - Identify which Scorers are failing

3. Improvement planning
   - Suggest prompt changes from failures
   - Propose new Dataset examples
   - Improve Guardrails or Scorers

4. W&B / Weave assistance
   - Query Runs and Traces in a project
   - Compare experiments
   - Prepare report summaries

==========================================================
References
==========================================================

W&B Skills GitHub:
https://github.com/wandb/skills

W&B Skills documentation:
https://docs.wandb.ai/platform/wb-skills

W&B MCP Server:
https://docs.wandb.ai/platform/mcp-server

==========================================================
Note
==========================================================

- This script only prints an overview of W&B Skills
- To use Skills, install them in your AI agent environment
- Combining Skills with the W&B MCP Server makes it easier for agents to access W&B context
"""

print(__doc__)
