"""
5_5: Saved Views - Save common Trace and Evaluation views

==========================================================
What are Saved Views?
==========================================================

Saved Views let you save filters, sorting, columns, and display settings for
Trace and Evaluation tables.

Instead of rebuilding the same view each time, you can save views for common
investigation or review workflows.

==========================================================
Common use cases
==========================================================

1. Failed trace investigation
   - Show only traces with errors
   - Filter to a specific op_name
   - Sort by high latency

2. Evaluation review
   - Show samples with low scorer values
   - Compare by model or dataset
   - Display only columns needed for review

3. Team sharing
   - Save common investigation views
   - Let team members inspect data under the same conditions

4. SDK workflows
   - Use SavedView from the Python SDK
   - Configure filters and columns programmatically

==========================================================
Basic workflow
==========================================================

In the UI:
   1. Open the Traces or Evals table
   2. Adjust filters, sorting, and columns
   3. Save the view
   4. Reopen the saved view later

In the SDK:
   1. Create `weave.SavedView()`
   2. Configure columns and filters
   3. Save the view
   4. Inspect it with `.to_grid()`

==========================================================
How this relates to this hands-on
==========================================================

As traces and evaluations grow, it becomes hard to inspect everything
manually.

Saved Views make repeated workflows reusable:
"show failures", "show low scorer examples", or "show high-latency traces".

==========================================================
Reference
==========================================================

Create and manage saved views:
https://docs.wandb.ai/weave/guides/tools/saved-views

==========================================================
Note
==========================================================

- This script only prints an overview
- Saved Views are available from both the UI and Python SDK
"""

print(__doc__)
