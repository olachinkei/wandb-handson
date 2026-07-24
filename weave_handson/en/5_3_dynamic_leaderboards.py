"""
5_3: Dynamic Leaderboards - Persistent comparison views for evaluations

==========================================================
What are Dynamic Leaderboards?
==========================================================

Dynamic Leaderboards are views for comparing Weave Evaluation results across
models, datasets, scorers, and metrics.

When you save filters and display settings, the Leaderboard can continue to
update as new matching Evaluation runs are added.

In other words, you can create a comparison view once and keep using it as
your experiments evolve.

==========================================================
Why this is useful
==========================================================

1. Model comparison
   - Compare multiple models in the same table
   - Review quality differences between large and lightweight models

2. Dataset and Scorer comparison
   - Filter to a specific Dataset
   - Compare accuracy, latency, cost, and other metrics

3. Display-name cleanup
   - Rename models or datasets to human-readable labels
   - Keep links to the underlying objects

4. Metric direction and coloring
   - Higher accuracy is better
   - Lower latency and cost are better
   - Configure metric direction so colors stay meaningful

==========================================================
Basic workflow
==========================================================

1. Open the Evaluations page in the Weave UI
2. Filter the evaluation table to the runs or datasets you want to compare
3. Click Visualize to create a Leaderboard
4. Use Configure to adjust Models, Datasets, Scorers, and Metrics
5. Save the Leaderboard as a reusable view

==========================================================
How this relates to this hands-on
==========================================================

After running Evaluations in 3_1 and 3_2, Dynamic Leaderboards help you
compare results over time.

They are useful when you want to keep answering:
"Which model, prompt, or scorer is best under the same criteria?"

==========================================================
Reference
==========================================================

Create dynamic Leaderboards in Evaluations:
https://docs.wandb.ai/weave/guides/evaluation/dynamic_leaderboards

==========================================================
Note
==========================================================

- This script only prints an overview
- Leaderboards are created from the Evaluations page in the Weave UI
"""

print(__doc__)
