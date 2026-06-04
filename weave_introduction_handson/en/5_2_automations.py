"""
5_2: Automations - Trigger notifications and actions

==========================================================
What are Automations?
==========================================================

Automations let you trigger actions based on monitor metrics and trace
activity in a Weave project.

Instead of manually watching dashboards, you can configure rules that send
notifications or call webhooks when quality drops, errors increase, latency
changes, or other conditions are met.

==========================================================
Common use cases
==========================================================

1. Threshold alerts
   - Notify when a monitor average crosses a threshold
   - Detect increases in toxicity or hallucination

2. Regression detection
   - Notify when quality scores drop after a change
   - Catch accuracy or safety regressions early

3. Deployment gates
   - Trigger a webhook when quality is above a threshold over a rolling window
   - Connect quality checks to release workflows

4. Operational monitoring
   - Alert on error rate, latency, or rate-limit changes

==========================================================
Basic workflow
==========================================================

1. Set up an Op or Monitor in your Weave project
2. Configure the action you want, such as Slack or a webhook
3. Open the Automations page and click Create automation
4. Configure metric, threshold, window, and aggregation
5. Configure the action, such as a Slack notification or webhook
6. Review the summary and create the automation

==========================================================
How this relates to this hands-on
==========================================================

After learning Monitors in 3_4, Automations let you move from
"detect a problem" to "notify someone or trigger an action when it happens."

==========================================================
Reference
==========================================================

Set up automations:
https://docs.wandb.ai/weave/guides/evaluation/automations

==========================================================
Note
==========================================================

- This script only prints an overview
- Slack or webhook actions require integration setup in Team Settings
"""

print(__doc__)
