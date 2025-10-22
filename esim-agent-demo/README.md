# eSIM Agent Demo

A multi-agent system for eSIM services built with OpenAI Agents SDK and Weights & Biases Weave.

## 🌟 Features

- **Multi-Agent Architecture**: Specialized agents for different tasks
  - **eSIM Agent** (Main): Orchestrates all interactions
  - **Plan Search Agent**: Finds eSIM plans by destination and duration
  - **Booking Agent**: Handles purchase process
  - **RAG Agent**: Answers general eSIM questions using knowledge base

- **OpenAI Agents SDK**: Modern agent framework with tool calling and handoffs
- **Weave Integration**: Full observability and tracing
- **RAG with Vector Store**: Knowledge base for eSIM information

## 🏗️ Architecture

```
User
  ↓
eSIM Agent (Main Orchestrator)
  ├── Plan Search Agent
  │   ├── ask_country_period (tool)
  │   └── plan_search (tool)
  ├── Booking Agent
  │   ├── status_check (tool)
  │   └── cost_calculator (tool)
  └── RAG Agent
      └── file_search (OpenAI Vector Store)
```

### Agent Details

#### 1. **eSIM Agent** (Main Orchestrator)
- **Role:** Master coordinator that handles overall communication
- Routes user requests to appropriate sub-agents
- Manages conversation flow and context
- Coordinates responses from multiple agents

#### 2. **Plan Search Agent**
- **Role:** Provides pricing information based on country and duration
- **Tools:**
  - `ask_country_period`: Collects travel destination and dates, converts date ranges to days
  - `plan_search`: Searches database for plans (local/regional/global)
- **Returns:** Plan details with pricing, coverage, and booking prompt

#### 3. **RAG Agent**
- **Role:** Handles Q&A using Retrieval-Augmented Generation
- **Workflow:**
  1. Determines if question is eSIM-related
  2. If not related: Politely declines to answer
  3. If related: Searches knowledge base using Vector Store
  4. Provides response with source citations
- **Knowledge Base:** 9 markdown documents covering device compatibility, activation, troubleshooting, etc.

#### 4. **Booking Agent**
- **Role:** Handles booking and payment processing
- **Tools:**
  - `status_check`: Verifies user login status and payment method
  - `cost_calculator`: Calculates total cost (price × quantity + 8% tax)
- **Flow:** Guides user through login → payment setup → booking confirmation

## 📋 Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- OpenAI API key
- Weights & Biases account (for Weave)

## 🚀 Setup

### 1. Install Dependencies

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync --extra dev
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Weights & Biases API Key
WANDB_API_KEY=...
```

Get your API keys:
- OpenAI: https://platform.openai.com/api-keys
- W&B: https://wandb.ai/authorize

### 3. Configure Project Settings

Edit `config/config.yaml` to customize:
- Weave project entity and name
- Agent models
- RAG settings
- Tool configurations

### 4. Set Up RAG Knowledge Base

Run the RAG preparation script to create and populate the vector store:

```bash
uv run python rag_prep.py
```

This will:
- Upload knowledge base documents to OpenAI
- Create a vector store
- Save vector store info for the RAG agent

## 💻 Usage

### Interactive Demo

Run the interactive demo to chat with the eSIM agent system:

```bash
uv run python demo.py
```

### Run with Guardrails (Programmatic)

The `run_agent()` function applies quality guardrails synchronously:

```python
from demo import run_agent
import asyncio

# Run with guardrails (default, silent mode)
response = asyncio.run(run_agent("What devices support eSIM?"))

# Run with verbose mode to see guardrail checks
response = asyncio.run(run_agent("What devices support eSIM?", verbose=True))

# Run without guardrails
response = asyncio.run(run_agent("What devices support eSIM?", apply_guardrails=False))
```

**Guardrail Checks:**
- **Faithfulness**: Response is grounded in knowledge base (blocking)
- **Relevancy**: Response answers the question (blocking)
- **Source Citation**: Response includes proper references (BLOCKING - critical for RAG)

**Blocking Behavior:**
- If citation check fails → Returns error message in Japanese
- If faithfulness check fails → Returns error message
- If relevancy check fails → Returns error message
- All guardrail results are recorded in Weave for analysis

**Error Messages:**
```
⚠️ 申し訳ございません。適切な参照情報を含む回答を作成できませんでした。質問を言い換えてお試しください。
(Sorry, we couldn't create a response with appropriate references. Please rephrase your question.)
```

### Test with Sample Queries

Run 10 predefined queries to test the system:

```python
# Run with verbose mode to see guardrails
asyncio.run(run_sample_queries(verbose=True))

# Run in silent mode (default)
asyncio.run(run_sample_queries())
```

Or test a single query:

```python
# With verbose mode
asyncio.run(single_query_demo("What devices support eSIM?", verbose=True))

# Silent mode
asyncio.run(single_query_demo("I'm traveling to Japan for 7 days"))
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_utils.py -v

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

## 📊 Evaluation

### Running Evaluations

This project includes comprehensive evaluation using Weights & Biases Weave:

```bash
# Run all evaluations
uv run python evaluation/eval.py

# Run individual evaluations
uv run python evaluation/eval.py plan_search  # Plan Search Agent only
uv run python evaluation/eval.py rag          # RAG Agent only
uv run python evaluation/eval.py booking      # Booking Agent only
uv run python evaluation/eval.py end_to_end   # Full system workflow
```

### Evaluation Metrics

#### **Plan Search Agent** (6 scorers, 8 scenarios)
- ✓ **tool_accuracy**: Correct tool selection and execution
- ✓ **accuracy**: Accurate pricing, plan type, country, and days
- ✓ **booking_prompt_correct**: Appropriate booking confirmation prompts
- ✓ **service_availability_correct**: Graceful handling of unavailable countries
- ✓ **provides_complete_answer**: Complete response vs asking clarification vs incomplete
- ✓ **clarification_appropriate**: Whether asking for clarification is appropriate

#### **RAG Agent** (7 scorers - LLM-as-a-judge, 8 scenarios)
- ✓ **faithfulness**: Response accuracy to retrieved context
- ✓ **answer_relevancy**: Response relevance to user question
- ✓ **source_citation**: Provides reference indicators
- ✓ **out_of_scope_handling**: Correctly redirects non-eSIM questions
- ✓ **accuracy**: Overall answer correctness with topic coverage
- ✓ **provides_complete_answer**: Complete response vs asking clarification vs incomplete
- ✓ **clarification_appropriate**: Whether asking for clarification is appropriate

#### **Booking Agent** (5 scorers, 6 scenarios)
- ✓ **tool_accuracy**: Correct tool usage (status_check, cost_calculator)
- ✓ **booking_flow_completion**: Proper flow with login/payment prompts
- ✓ **accuracy**: Accurate total cost calculation (LLM judge)
- ✓ **provides_complete_answer**: Complete response vs asking clarification vs incomplete
- ✓ **clarification_appropriate**: Whether asking for clarification is appropriate

#### **End-to-End System** (8 scorers, 15 scenarios)
- ✓ **agent_sequence_correct**: Correct agent handoff sequence
- ✓ **tool_usage_correct**: All expected tools used
- ✓ **final_score & meets_requirements**: End result validation via LLM-as-a-judge
- ✓ **step_count_correct & step_efficiency**: Workflow completed within expected step range
- ✓ **reflection_detected**: Error correction and retry behavior
- ✓ **overall_success**: Complete workflow success
- ✓ **provides_complete_answer**: Complete response vs asking clarification vs incomplete
- ✓ **clarification_appropriate**: Whether asking for clarification is appropriate

### Test Scenarios

- **Plan Search**: 8 scenarios (5 standard + 2 negative/unavailable + 1 ambiguous)
- **RAG**: 8 scenarios (6 eSIM questions + 2 out-of-scope)
- **Booking**: 6 scenarios (5 standard + 1 ambiguous)
- **End-to-End**: 15 scenarios (8 plan search flows + 4 RAG flows + 3 direct booking flows)

View evaluation results in Weave: `https://wandb.ai/{entity}/{project}/weave`

## 📁 Project Structure

```
esim-agent-demo/
├── config/
│   ├── config.yaml              # Main configuration
│   └── README.md                # Config documentation
├── database/
│   ├── price_list.json          # eSIM pricing data (35 countries, 9 regions)
│   ├── RAG_docs/                # Knowledge base (9 markdown documents)
│   └── vector_store_info.json   # Vector store metadata
├── cache/
│   └── user_cache.json          # Mock user data
├── src/
│   ├── agents/
│   │   ├── esim_agent.py        # Main orchestrator
│   │   ├── plan_search_agent.py # Plan search specialist
│   │   ├── booking_agent.py     # Booking specialist
│   │   └── rag_agent.py         # Q&A specialist
│   ├── tools.py                 # Agent tools (4 tools)
│   └── utils.py                 # Utility functions
├── evaluation/
│   ├── eval.py                  # Main evaluation runner (480+ lines)
│   ├── scorers.py               # Base & common scorers (2 common scorers)
│   ├── scorers_plan_search.py   # Plan Search scorers (4 + 2 common = 6)
│   ├── scorers_rag.py           # RAG scorers (5 + 2 common = 7)
│   ├── scorers_booking.py       # Booking scorers (3 + 2 common = 5)
│   ├── scorers_end_to_end.py    # End-to-End scorers (6 + 2 common = 8)
│   ├── scenarios/               # Test scenarios (37 total)
│   │   ├── plan_search_scenarios.json    # 8 scenarios
│   │   ├── rag_scenarios.json            # 8 scenarios
│   │   ├── booking_scenarios.json        # 6 scenarios
│   │   └── end_to_end_scenarios.json     # 15 scenarios
│   └── README.md                # Evaluation guide
├── tests/
│   ├── test_utils.py            # Utils tests (20 tests)
│   ├── test_tools.py            # Tools tests (13 tests)
│   ├── test_rag_prep.py         # RAG prep tests (4 tests)
│   └── evaluation/
│       └── test_eval.py         # Evaluation tests (21 tests)
├── demo.py                      # Interactive demo
├── rag_prep.py                  # RAG setup script
├── pyproject.toml               # Dependencies
├── uv.lock                      # Lock file
├── README.md                    # This file
└── AGENT.md                     # Detailed technical documentation
```

## 📊 Observability

All agent interactions are automatically traced to Weights & Biases Weave:

1. Run the demo or tests
2. Check your Weave project at: `https://wandb.ai/{entity}/{project}/weave`

Weave provides:
- Full conversation traces
- Tool call details
- Agent handoff visualization
- Performance metrics

## 📝 Development Notes

- All tools have `_impl` versions for testing
- Use `@function_tool` decorator for agent tools
- Vector store is created once and reused
- Mock data in `cache/` for testing without real auth

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- OpenAI Agents SDK
- Weights & Biases Weave
- Python community

## 📚 Additional Resources

- [OpenAI Agents Documentation](https://openai.github.io/openai-agents-python/)
- [Weave Documentation](https://wandb.me/weave)
- [Project Documentation](AGENT.md)
