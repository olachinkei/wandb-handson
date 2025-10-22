# eSIM Agent Demo

A multi-agent system for eSIM plan recommendations, bookings, and customer support.

---

## 🎯 Overview

This project implements a sophisticated agent-based system for managing eSIM services, including plan recommendations, booking operations, and knowledge-base powered Q&A support.

---

## 🤖 Agent Architecture

### 1. **eSIM Agent** (Main Orchestrator)
**Role:** Master coordinator that handles overall communication, planning, and tool selection
- Routes user requests to appropriate sub-agents
- Manages conversation flow and context
- Coordinates responses from multiple agents

### 2. **Plan Search Agent**
**Role:** Provides pricing information based on country and duration

#### Tools:
- **`ask_country_period`**
  - Asks user for country and travel dates if not provided in conversation history
  - Converts date ranges to number of days when dates are provided
  - **Returns:** `{"countries": ["country1", "country2"], "days": int}`

- **`plan_select`**
  - Classifies travel type into three categories:
    1. **Local:** Single country
    2. **Regional:** Multiple countries within a region (e.g., Asia)
    3. **Cross-regional:** Countries across different regions
  - Uses `plan_search` tool to fetch appropriate plans
  - Returns 1-3 plans depending on coverage needs

- **`plan_search`**
  - Searches `plan_list` database for given countries/regions
  - **Returns:** `{"country_or_region": "price", ...}`

### 3. **RAG Agent**
**Role:** Handles Q&A using Retrieval-Augmented Generation

#### Workflow:
1. Receives user question
2. Determines if question is eSIM-related
   - If not related: Politely declines to answer
3. If related: Searches knowledge base using RAG
4. If answer found: Provides response
5. If not found: Escalates to human support

### 4. **Booking Agent**
**Role:** Handles booking and payment processing

#### Tools:
- **`status_check`**
  - Verifies user login status
  - Confirms credit card registration

- **`cost_calculator`**
  - Calculates total booking cost based on selected plan

---

## 🛠️ Technology Stack

- **Agent Framework:** OpenAI Agent SDK
- **Observability & Evaluation:** Weights & Biases Weave
- **Package Manager:** uv
- **Vector Store:** OpenAI Retrieval API

---

## 📁 Project Structure

```
esim-agent-demo/
├── src/
│   ├── agent.py              # Agent implementations
│   └── utils.py              # Helper functions
├── database/
│   ├── plan_list.json        # eSIM plan database
│   ├── embedding.py          # Vector embedding utilities
│   └── RAG_docs/             # Knowledge base documents (markdown files)
├── config/
│   └── config.yaml           # Configuration settings
├── cache/
│   └── user_cache.json       # Mock user session data (login, payment info)
├── evaluation/
│   ├── eval.py               # Weave-based evaluation scripts
│   └── evaluation_scenarios/ # Test scenarios (JSON format)
├── rag_prep.py               # RAG setup and preparation
├── demo.py                   # Interactive demo interface
├── .env                      # API keys (WANDB_API_KEY, OPENAI_API_KEY)
└── README.md
```

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- uv package manager

**Implementation References:**
OpenAI Agents SDK: https://openai.github.io/openai-agents-python/agents/

**Architecture Implemented:**
- Main eSIM Agent uses `handoffs` to delegate to specialized agents
- Each specialized agent has relevant `tools`
- RAG Agent uses OpenAI Vector Store with `file_search`
- All agents traced with Weave for observability
- Tools have both wrapper (`@function_tool`) and implementation (`_impl`) versions

**Files Created:**
- `src/agents/esim_agent.py`: Main orchestrator
- `src/agents/plan_search_agent.py`: Plan search specialist
- `src/agents/booking_agent.py`: Booking specialist
- `src/agents/rag_agent.py`: Q&A specialist with RAG
- `src/tools.py`: All agent tools
- `demo.py`: Interactive demo application
- `README.md`: Full documentation
- `evaluation/eval.py`: Main evaluation runner (420+ lines)
- `evaluation/scorers_plan_search.py`: Plan Search scorers (4 scorers)
- `evaluation/scorers_rag.py`: RAG scorers (5 scorers)
- `evaluation/scorers_booking.py`: Booking scorers (3 scorers)
- `evaluation/scorers_end_to_end.py`: End-to-End scorers (7 scorers) 
- `evaluation/README.md`: Complete evaluation guide
- `tests/evaluation/test_eval.py`: Evaluation tests (21 tests)


**Usage:**
```bash
# Run all evaluations
uv run python evaluation/eval.py

# Run single agent evaluation
uv run python evaluation/eval.py plan_search
uv run python evaluation/eval.py rag
uv run python evaluation/eval.py booking
uv run python evaluation/eval.py end_to_end
```

**Evaluation Criteria:**

**Plan Search Agent (4 scorers):**
- ✓ **tool_accuracy**: Correct agent and tool selection
- ✓ **accuracy**: Accurate pricing, plan type, country, and days
- ✓ **booking_prompt_correct**: Asks for booking confirmation appropriately
- ✓ **service_availability_correct**: Handles unavailable countries gracefully

**RAG Agent (5 scorers - LLM-as-a-judge):**
- ✓ **faithfulness**: Response accuracy to retrieved context
- ✓ **answer_relevancy**: Response relevance to user question
- ✓ **source_citation**: Provides reference indicators
- ✓ **out_of_scope_handling**: Correctly redirects non-eSIM questions
- ✓ **accuracy**: Overall answer correctness with topic coverage

**Booking Agent (3 scorers):**
- ✓ **tool_accuracy**: Correct tool usage (status_check, cost_calculator)
- ✓ **booking_flow_completion**: Proper flow with login/payment prompts
- ✓ **accuracy**: Accurate total cost calculation (price × quantity + 8% tax) (LLM judge)

**End-to-End System (7 scorers)** 🆕:
- ✓ **agent_sequence_correct**: Correct agent handoff sequence
- ✓ **tool_coverage**: All expected tools used
- ✓ **intermediate_accuracy**: Mid-workflow result validation
- ✓ **final_accuracy**: End result validation (price, total, prompts, etc.)
- ✓ **step_count_correct**: Workflow completed within expected step range
- ✓ **reflection_detected**: Error correction and retry behavior
- ✓ **overall_success**: Complete workflow success


---

## 🎮 Usage

Run the interactive demo:
```bash
python demo.py
```

---

## 🧪 Evaluation

Run evaluations with Weave:
```bash
python evaluation/eval.py
```

---

## ⚠️ Implementation Notes

1. **Always refer to documentation:**
   - Consult Weave documentation for tracing and evaluation patterns
   - Check OpenAI Agent SDK documentation for agent implementation best practices

2. **Incremental development:**
   - Test each agent independently before integration
   - Use Weave traces to debug agent behavior

3. **Mock data:**
   - User cache is simulated for development purposes
   - Replace with real authentication in production

---

## 📝 Git Management

This project uses Git for version control. Follow standard Git workflows:
- Create feature branches for new agents/tools
- Write descriptive commit messages
- Use pull requests for code review


## To do (work later)
- Plan search agent
    - plan search agentに複雑なケース (日本が数日, アメリカが数日, フランスが数日)的なプランを入れる。Global planは削除する
- manage prompts with weave.prompts
- manage datasets with weave.datasets
