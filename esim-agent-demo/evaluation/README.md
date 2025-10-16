# eSIM Agent Evaluation

Comprehensive evaluation suite for the eSIM Agent Demo using Weights & Biases Weave.

## 📁 Structure

```
evaluation/
├── scenarios/              # Evaluation test cases
│   ├── plan_search_scenarios.json   # 5 scenarios
│   ├── rag_scenarios.json           # 8 scenarios
│   └── booking_scenarios.json       # 5 scenarios
├── scorers.py             # 11 scorer classes
├── eval.py                # Main evaluation runner
└── README.md              # This file
```

## 🎯 Evaluation Coverage

### Plan Search Agent (5 scenarios)
**Metrics:**
- `tool_accuracy`: Correct tool calls (ask_country_period, plan_search)
- `accuracy`: LLM judge for date calculation, pricing, plan type accuracy
- `booking_prompt_present`: Checks for booking confirmation prompt

**Scenarios:**
- Single country plan search (Japan, 7 days)
- Regional plan search (France + Germany, 14 days)
- Global plan search (US + Japan + France, 30 days)
- Minimal input format (South Korea, 3 days)
- Regional within Europe (Spain + Portugal, 10 days)

### RAG Agent (8 scenarios)
**Metrics:**
- `faithfulness`: LLM judge for response faithfulness to sources
- `answer_relevancy`: LLM judge for answer relevance to question
- `source_citation`: Checks for source citations
- `out_of_scope_handling`: Verifies redirect behavior
- `accuracy`: LLM judge for overall answer correctness

**Scenarios:**
- Basic eSIM definition
- Device compatibility (iPhone 13)
- Activation instructions (Android)
- Troubleshooting help
- Out-of-scope: Pricing question (should redirect)
- Out-of-scope: Booking request (should redirect)
- International travel question
- Security and privacy question

### Booking Agent (5 scenarios)
**Metrics:**
- `tool_accuracy`: Correct tool calls (status_check, cost_calculator)
- `booking_flow_completion`: Checks flow completion or prompts
- `accuracy`: LLM judge for cost calculation accuracy

**Scenarios:**
- Logged-in user with payment ($19.99)
- User without payment method ($29.99)
- Multiple quantity purchase (2 x $15)
- User not logged in ($25.00)
- Higher priced plan ($49.99)

## 🚀 Usage

### Run All Evaluations

```bash
uv run python evaluation/eval.py
```

This will:
1. Run evaluations for all 3 agent types
2. Upload results to Weave
3. Print summary statistics
4. Provide link to Weave dashboard

### Run Single Agent Evaluation

```bash
# Plan Search Agent only
uv run python evaluation/eval.py plan_search

# RAG Agent only
uv run python evaluation/eval.py rag

# Booking Agent only
uv run python evaluation/eval.py booking
```

## 📊 Scorers

All scorers are implemented in `scorers.py` following Weave best practices:

### Base Scorers
- `LLMJudgeScorer`: Base class for LLM-as-a-judge evaluations

### Plan Search Scorers
- `PlanSearchToolAccuracyScorer`: Tool call verification
- `PlanSearchAccuracyScorer`: LLM judge for overall accuracy
- `PlanSearchBookingPromptScorer`: Booking prompt detection

### RAG Scorers
- `RAGFaithfulnessScorer`: LLM judge for faithfulness
- `RAGAnswerRelevancyScorer`: LLM judge for relevancy
- `RAGSourceCitationScorer`: Citation detection
- `RAGOutOfScopeHandlingScorer`: Out-of-scope handling
- `RAGAccuracyScorer`: LLM judge for accuracy

### Booking Scorers
- `BookingToolAccuracyScorer`: Tool call verification
- `BookingFlowCompletionScorer`: Flow completion check
- `BookingAccuracyScorer`: LLM judge for cost accuracy

## 🔍 LLM-as-a-Judge

For metrics where exact matching is difficult (e.g., accuracy, faithfulness), we use GPT-4o-mini as a judge:

```python
class MyScorer(LLMJudgeScorer):
    @weave.op
    def score(self, output: str, input: str) -> dict:
        system_prompt = "Evaluate if..."
        user_prompt = f"Question: {input}\nResponse: {output}"
        judgment = self.call_llm_judge(system_prompt, user_prompt)
        return {"accuracy": judgment["accurate"]}
```

The LLM judge returns structured JSON responses for consistent evaluation.

## 📈 Viewing Results

After running evaluations, results are available in Weave:

1. **Weave Dashboard**: `https://wandb.ai/{entity}/{project}/weave`
2. **Evaluation Traces**: View individual test case traces
3. **Score Analysis**: Aggregate metrics across all scenarios
4. **Comparison**: Compare different evaluation runs

## 🧪 Adding New Evaluations

### 1. Add Scenarios

Create/update JSON in `scenarios/`:

```json
{
  "id": "new_test_001",
  "input": "User query here",
  "expected_tool_calls": ["tool1", "tool2"],
  "expected_output": "Expected output",
  "description": "Test description"
}
```

### 2. Add Scorers (if needed)

In `scorers.py`:

```python
class MyNewScorer(weave.Scorer):
    @weave.op
    def score(self, output: str, expected: str) -> dict:
        is_correct = output == expected
        return {"my_metric": is_correct}
```

### 3. Update Evaluation Runner

In `eval.py`, add your scorer to the appropriate list:

```python
PLAN_SEARCH_SCORERS = [
    # ... existing scorers
    MyNewScorer(),
]
```

## 💡 Tips

1. **Start Small**: Test with single agent evaluation first
2. **Check Traces**: Use Weave UI to debug failed evaluations
3. **Iterate**: Adjust scorer prompts based on results
4. **Compare Runs**: Use Weave to compare different model versions

## 📚 References

- [Weave Scorers Guide](https://weave-docs.wandb.ai/guides/evaluation/scorers)
- [Builtin Scorers](https://weave-docs.wandb.ai/guides/evaluation/builtin_scorers)
- [Local Scorers](https://weave-docs.wandb.ai/guides/evaluation/weave_local_scorers)

## ⚠️ Notes

- Evaluations require OpenAI API access (for agents and LLM judges)
- Results are uploaded to Weights & Biases
- RAG Agent requires vector store to be set up first (run `rag_prep.py`)
- Each evaluation run creates a new entry in Weave for tracking

