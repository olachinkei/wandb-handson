"""
3_4: Monitors - continuous evaluation with built-in signals

==========================================================
What are Monitors?
==========================================================

Monitors help continuously evaluate production traces so you can understand
quality and error trends over time.

Inspecting individual traces is useful for debugging, but production systems
can generate a large number of traces. It is not realistic for humans to
review every trace manually.

With Monitors, built-in signals or custom monitors can score incoming traces
continuously.

==========================================================
What are built-in signals?
==========================================================

Built-in signals are preset scorers provided by Weave. They automatically
detect common quality issues and errors in production traces.

Examples:

- Hallucination: claims that contradict the provided input context
- Low quality: incomplete, poorly formatted, or low-effort responses
- User frustration: repeated questions, complaints, or negative sentiment
- Jailbreaking: attempts to bypass safety constraints
- Network Error: network-related failures
- Ratelimited: 429 responses or quota exhaustion
- Bug: application issues such as KeyError or TypeError

==========================================================
Common use cases
==========================================================

1. Production quality monitoring
   - Detect increases in failures or low-quality outputs
   - Tag problematic traces by issue type

2. Finding improvement areas
   - Identify common failure patterns
   - Decide what to improve in Prompts, Datasets, Scorers, or Guardrails

3. Operational alerts
   - Filter traces with triggered signals
   - Combine signals with Automations for notifications

4. Agent improvement
   - Monitor conversation and tool-use quality
   - Feed failure cases back into Annotation Queues or Evaluation Datasets

==========================================================
Basic workflow
==========================================================

1. Open the Monitors page in your Weave project
2. Enable the built-in signals you want to use
3. New incoming traces are scored automatically
4. Review signals in the Traces page or project dashboard
5. Investigate problematic traces and improve the application

==========================================================
How this relates to this hands-on
==========================================================

3_1 and 3_2 cover evaluation against local datasets.
3_3 covers feedback collection through human review.

3_4 Monitors are for continuous evaluation in production. Together,
offline evaluation, annotation, and production monitoring create a feedback
loop for improving LLM applications.

==========================================================
Reference
==========================================================

Monitor using built-in signals:
https://docs.wandb.ai/weave/guides/evaluation/monitors

==========================================================
Note
==========================================================

- Weave for Agents is in Public Preview
- Features, APIs, and the Agents view UI may change before general availability
- This script only prints an overview
"""

print(__doc__)
