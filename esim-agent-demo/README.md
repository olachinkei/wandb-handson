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

Example interactions:
- "I'm traveling to Japan for 7 days" → Plan Search
- "How do I activate an eSIM?" → RAG
- "I want to buy this plan" → Booking

### Single Query Test

Edit `demo.py` to test specific queries:

```python
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

## 📁 Project Structure

```
esim-agent-demo/
├── config/
│   ├── config.yaml           # Main configuration
│   └── README.md            # Config documentation
├── database/
│   ├── price_list.json      # eSIM pricing data
│   ├── RAG_docs/            # Knowledge base documents
│   └── vector_store_info.json  # Vector store metadata
├── cache/
│   └── user_cache.json      # Mock user data
├── src/
│   ├── agents/
│   │   ├── esim_agent.py        # Main orchestrator
│   │   ├── plan_search_agent.py # Plan search specialist
│   │   ├── booking_agent.py     # Booking specialist
│   │   └── rag_agent.py         # Q&A specialist
│   ├── tools.py             # Agent tools
│   └── utils.py             # Utility functions
├── tests/
│   ├── test_utils.py        # Utils tests
│   └── test_tools.py        # Tools tests
├── demo.py                  # Interactive demo
├── rag_prep.py             # RAG setup script
└── AGENT.md                # Detailed documentation
```

## 🎯 Development Workflow

This project follows a phased development approach:

- ✅ **Phase 1**: Database Setup
- ✅ **Phase 2**: Configuration
- ✅ **Phase 3**: RAG Preparation
- ✅ **Phase 4**: Agent Implementation
- ⏳ **Phase 5**: Evaluation

See `AGENT.md` for detailed documentation.

## 📊 Observability

All agent interactions are automatically traced to Weights & Biases Weave:

1. Run the demo or tests
2. Check your Weave project at: `https://wandb.ai/{entity}/{project}/weave`

Weave provides:
- Full conversation traces
- Tool call details
- Agent handoff visualization
- Performance metrics

## 🔍 Key Components

### Tools

- **ask_country_period**: Process travel destinations and dates
- **plan_search**: Search for eSIM plans (local/regional/global)
- **status_check**: Verify user login and payment status
- **cost_calculator**: Calculate booking costs with tax

### Agents

Each agent has:
- Specific instructions and personality
- Relevant tools or handoffs
- Clear responsibilities
- Configured model (GPT-5 or GPT-5-mini)

### Configuration

Centralized in `config/config.yaml`:
- Agent models and settings
- Weave tracking
- RAG configuration
- Tool parameters

## 📝 Development Notes

- All tools have `_impl` versions for testing
- Use `@function_tool` decorator for agent tools
- Vector store is created once and reused
- Mock data in `cache/` for testing without real auth

## 🤝 Contributing

1. Create a new branch
2. Make changes
3. Run tests: `uv run pytest`
4. Commit with descriptive messages
5. Push and create PR

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
