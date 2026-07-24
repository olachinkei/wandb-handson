"""
5_4: Trace Plots - Visualize cost, latency, and token usage

==========================================================
What are Trace Plots?
==========================================================

Trace Plots visualize trace-level metrics from the Weave Traces page using
interactive charts.

For LLM applications, quality is only one part of operations. Latency, cost,
and token usage are also important. Trace Plots make those patterns visible
directly from your trace data.

==========================================================
What you can inspect
==========================================================

1. Latency
   - Whether latency is getting worse over time
   - Whether a specific op is slow

2. Cost
   - Whether cost suddenly increased
   - Which traces are expensive

3. Token usage
   - Relationship between prompt tokens and completion tokens
   - Inputs or outputs that are too long

4. Trace investigation
   - Click a point in a scatter plot to open the corresponding trace
   - Combine plots with filters to focus on specific traces

==========================================================
Basic workflow
==========================================================

1. Open the Traces page in the Weave UI
2. Filter by datetime or operation if needed
3. Open Trace Plots from Show Metrics
4. Review the default plots
5. Add custom charts when needed

==========================================================
How this relates to this hands-on
==========================================================

After running the 1_x tracing examples, 3_x evaluations, and 4_x guardrails,
your project will contain many traces.

Trace Plots help inspect those traces through cost, latency, and token usage.

==========================================================
Reference
==========================================================

Use trace plots:
https://docs.wandb.ai/weave/guides/tracking/trace-plots

==========================================================
Note
==========================================================

- This script only prints an overview
- Trace Plots are available from the Traces page in the Weave UI
"""

print(__doc__)
