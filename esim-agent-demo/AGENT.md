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


---

## 📋 Development Process

### Phase 1: Database Setup ✅ COMPLETED
- [x] Create `plan_list` database with eSIM pricing data
- [x] Generate knowledge base documents in `database/RAG_docs/`
  - Created 9 comprehensive markdown files based on reference sources
  - Files cover: device compatibility, activation, troubleshooting, FAQ, etc.
  - Reference links: `database/reference_page_list_delete_later.md`
- [x] Create mock user cache data

### Phase 2: Configuration ✅ COMPLETED
- [x] Set up `config.yaml` with configuration parameters
  - **Model selection**: 
  - **Weave settings**: entity and project configuration
  - **RAG configuration**: Vector store and retrieval settings
  - **Tool configuration**: Plan search, user cache, booking settings
  - **Evaluation metrics**: Defined for each agent type
- [x] Create `src/utils.py` with configuration loading utilities
- [x] Create tests directory structure

### Phase 3: RAG Preparation ✅ COMPLETED
- [x] Implement `rag_prep.py` for knowledge base setup
- [x] Initialize OpenAI Vector Store / Assistants API
- [x] Create and upload knowledge base files
- [x] Configure retrieval settings and test queries
- [x] Add tests for RAG preparation (4 tests passing)

### Phase 4: Agent Implementation ✅ COMPLETED
- [x] Implement core agents in `src/agents/`
  - **eSIM Agent**: Main orchestrator with handoffs ✅
  - **Plan Search Agent**: Pricing and plan recommendations ✅
  - **RAG Agent**: Q&A with knowledge base (Vector Store) ✅
  - **Booking Agent**: Reservation handling ✅
- [x] Implement agent tools in `src/tools.py` ✅
  - `ask_country_period`, `plan_search` (Plan Search)
  - `status_check`, `cost_calculator` (Booking)
- [x] Build interactive demo in `demo.py` ✅
- [x] Write tool tests in `tests/test_tools.py` (11 tests passing) ✅
- [x] Create comprehensive `README.md` ✅

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

### Phase 5: Evaluation ✅ COMPLETED
- [x] Create evaluation scenarios (38 test cases) ✅
  - plan_search_scenarios.json (7 scenarios, including 2 negative cases)
  - rag_scenarios.json (8 scenarios)
  - booking_scenarios.json (5 scenarios)
  - multi_agent_scenarios.json (18 scenarios: 8 plan_search + 4 rag + 3 booking + 3 full_flow) 🆕
- [x] Implement evaluation scorers (19 scorer classes) ✅
  - Base LLMJudgeScorer for LLM-as-a-judge evaluations
  - Plan Search: Tool accuracy, accuracy, booking prompt, service availability (4 scorers)
  - RAG: Faithfulness, relevancy, citations, out-of-scope, accuracy (5 scorers)
  - Booking: Tool accuracy, flow completion, accuracy (3 scorers)
  - Multi-Agent: Sequence, tool usage, intermediate, final, steps, reflection, success (7 scorers) 🆕
- [x] Implement evaluation runner in `evaluation/eval.py` ✅
  - AgentModel wrapper for Weave evaluations
  - Enhanced predict method with agent sequence tracking 🆕
  - Fixed tool name extraction (strip _impl suffix)
  - Dataset preparation from JSON scenarios
  - Support for single or all agent evaluations (including multi_agent) 🆕
  - Full Weave integration with display names
- [x] Write evaluation tests in `tests/evaluation/` ✅
  - 21 tests for scenario loading and validation (+5 for multi-agent) 🆕
  - All tests passing
- [x] Run evaluations and analyze results with Weave ✅
- [x] Implement end-to-end multi-agent workflow evaluation ✅ 🆕

**Completed:**
- ✅ 38 evaluation scenarios covering all agent types, workflows, and edge cases
- ✅ 19 scorer classes based on Weave documentation
- ✅ LLM-as-a-judge implementation for complex metrics
- ✅ Full evaluation runner with CLI support (4 evaluation types)
- ✅ 21 evaluation tests (100% passing)
- ✅ Comprehensive evaluation documentation
- ✅ All evaluations executed with strong performance
- ✅ End-to-end multi-agent workflow evaluation with 3-agent flows 🆕
  - eSIM Agent → Plan Search Agent
  - eSIM Agent → RAG Agent
  - eSIM Agent → Booking Agent
  - eSIM Agent → Plan Search Agent → Booking Agent (Full Flow) 🌟

**Files Created:**
- `evaluation/eval.py`: Main evaluation runner (420+ lines)
- `evaluation/scorers_plan_search.py`: Plan Search scorers (4 scorers)
- `evaluation/scorers_rag.py`: RAG scorers (5 scorers)
- `evaluation/scorers_booking.py`: Booking scorers (3 scorers)
- `evaluation/scorers_multi_agent.py`: Multi-Agent scorers (7 scorers) 🆕
- `evaluation/README.md`: Complete evaluation guide
- `tests/evaluation/test_eval.py`: Evaluation tests (21 tests)

**Evaluation Results:**
- **Plan Search Agent (7 scenarios)**:
  - tool_accuracy: 85.7%
  - accuracy: 85.7%
  - booking_prompt_correct: 85.7%
  - service_availability_correct: 100% ✅ (perfect handling of negative cases)

- **RAG Agent (8 scenarios)**:
  - faithfulness: 75%
  - answer_relevancy: 87.5%
  - source_citation: 50%
  - out_of_scope_handling: 62.5%
  - accuracy: 75%

- **Booking Agent (5 scenarios)**:
  - tool_accuracy: 100% ✅
  - booking_flow_completion: 80%
  - accuracy: 100% ✅
  - total_shown: 100% ✅

- **Multi-Agent System (18 scenarios: 8 Plan Search + 4 RAG + 3 Booking + 3 Full Flow)** 🆕:
  - overall_success: 100% ✅
  - agent_sequence_correct: 83.3% (15/18) ✅ (3-agent flow tracking)
  - tool_coverage: 68.5% (comprehensive tool validation)
  - intermediate_accuracy: 88.9% (16/18) ✅
  - final_accuracy: 22.2% (4/18)
  - step_count_correct: 61.1% (11/18)
  - step_efficiency: 91.2% ✅ (efficient execution)
  - reflection_detected: 44.4% (8/18) (error correction when needed)
  - Covers: Plan search flows, RAG knowledge queries, direct booking, full flow (eSIM → Plan Search → Booking), auth failures, unsupported countries

**Usage:**
```bash
# Run all evaluations
uv run python evaluation/eval.py

# Run single agent evaluation
uv run python evaluation/eval.py plan_search
uv run python evaluation/eval.py rag
uv run python evaluation/eval.py booking
uv run python evaluation/eval.py multi_agent
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

**Multi-Agent System (7 scorers)** 🆕:
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
