"""
1_4: Playground - Using the Playground

==========================================================
What is Weave Playground
==========================================================

Weave Playground is a feature that lets you edit and test prompts
directly in the UI. You can do prompt engineering without writing code.

==========================================================
Main Features
==========================================================

1. Prompt Editing and Testing
   - Edit prompts directly in the UI
   - Run and test changes immediately
   - Maintain history

2. Multi-Model Comparison
   - Run multiple models in parallel
   - Compare responses side by side
   - Compare cost and latency

3. Parameter Tuning
   - Adjust temperature, max_tokens etc. in the UI
   - See results in real-time

4. From Trace to Playground
   - Open past traces in Playground
   - Test different prompts/models with the same input

==========================================================
How to Use
==========================================================

1. Access Weave UI
   https://wandb.ai/<entity>/<project>/weave

2. Select a trace in the Traces tab

3. Click "Open in Playground"

4. Modify parameters and re-run

==========================================================
Playground Use Cases
==========================================================

Prompt Engineering
   - Adjust system prompts
   - Add/remove few-shot examples
   - Specify output format

Model Comparison
   - GPT-4o vs GPT-4o-mini
   - Compare with different temperature
   - Cost vs quality tradeoff analysis

Debugging
   - Reproduce problematic traces
   - Modify prompt and re-run
   - Iterate until expected output is achieved

A/B Test Preparation
   - Try multiple prompt variations
   - Save good prompts when discovered

==========================================================
Tips
==========================================================

Reproduction from Traces
   When issues occur in production, you can open
   that trace in Playground to reproduce and debug
   under the same conditions.

Saving Prompts
   Once you have a good prompt, you can save it as
   weave.StringPrompt or weave.MessagesPrompt.
   -> See 2_1_prompt.py

Integration with Evaluation
   Prompts tuned in Playground can be
   quantitatively evaluated with Evaluation.
   -> See 3_1_offline_evaluation.py

==========================================================
Note
==========================================================

- Playground is a UI feature, so there's no code in this script
- Access Weave UI to try it
- First run 1_1_0_basic_trace.py to create traces,
  then try opening them in Playground
"""

print(__doc__)
