"""
3_3: Annotation Queue

==========================================================
What is an Annotation Queue?
==========================================================

An Annotation Queue is a Weave feature for collecting structured feedback
from human reviewers on traces, model outputs, or other review items.

LLM application quality is not always easy to judge with automatic scores
alone. Some answers require expert judgment, nuanced review, or human checks
for correctness, safety, and usefulness.

With an Annotation Queue, review items are organized into a queue, and
reviewers can inspect each item one by one and submit structured feedback.

==========================================================
Common use cases
==========================================================

1. Human evaluation
   - Check whether an answer is correct
   - Check whether an answer is useful enough
   - Check whether an answer contains unsafe or inappropriate content

2. Evaluation Dataset improvement
   - Find failure cases
   - Identify new examples to add
   - Refine evaluation criteria

3. Scorer and Guardrail improvement
   - Compare automatic scores with human judgment
   - Adjust scorer criteria
   - Find cases missed by guardrails

4. Expert review
   - Ask domain experts to review outputs
   - Reviewers do not need to understand the underlying trace system

==========================================================
Basic workflow
==========================================================

1. Select traces or outputs to review
2. Create an Annotation Queue
3. Configure review fields and instructions
4. Reviewers open the queue and inspect each item
5. Reviewers submit structured feedback
6. Use the saved feedback for evaluation and improvement

==========================================================
How this relates to this hands-on
==========================================================

3_1 and 3_2 cover automated evaluation with Scorers.

Annotation Queue is the next step. It helps collect human feedback for
samples that are difficult to judge automatically.

That feedback can improve Datasets, Scorers, Prompts, and Guardrails.

==========================================================
Reference
==========================================================

Annotation workflow:
https://docs.wandb.ai/weave/guides/tracking/annotation-review#annotation-workflow

==========================================================
Note
==========================================================

- Annotation Queue is a UI feature, so this script only prints an overview
- In practice, queues are created and shared from the Weave UI
- Human feedback is an important signal for improving LLM applications
"""

print(__doc__)
