# Configuration Guide

## Setup Instructions

### 1. Environment Variables

Create a `.env` file in the project root with the following:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
WANDB_API_KEY=your_wandb_api_key_here

# Optional
OPENAI_ORG_ID=your_org_id  # If using OpenAI organization
```

### 2. Weave Configuration

Update `config.yaml`:

```yaml
weave:
  entity: "your-wandb-username-or-team"  # Your W&B username or team name
  project: "esim-agent-demo"
```

### 3. Model Selection

Current models configured (as of October 2025):

| Agent | Model | Purpose |
|-------|-------|---------|
| eSIM Agent | gpt-5-2025-08-07 | Main orchestrator, complex reasoning |
| Plan Search | gpt-5-mini-2025-08-07 | Fast pricing lookups |
| RAG Agent | gpt-5-2025-08-07 | Knowledge retrieval and synthesis |
| Booking Agent | gpt-5-mini-2025-08-07 | Structured booking flow |

**Model Options:**
- `gpt-5-2025-08-07`: Latest flagship model with advanced reasoning
- `gpt-5-mini-2025-08-07`: Fast, cost-effective, excellent for structured tasks
- `gpt-4o`: Previous generation flagship (fallback option)
- `gpt-4o-mini`: Previous generation mini (fallback option)

Refer to [OpenAI Models](https://platform.openai.com/docs/models) for latest options.

## Configuration Sections

### Agent Configuration
- **Temperature**: Lower (0.1-0.3) for consistent outputs, higher (0.7-1.0) for creative responses
- **Max tokens**: Maximum response length
- **Model**: OpenAI model to use

### RAG Configuration
- **Embeddings**: `text-embedding-3-small` (default) or `text-embedding-3-large` (higher quality)
- **Top K**: Number of relevant documents to retrieve (default: 5)
- **Similarity threshold**: Minimum relevance score (0-1, default: 0.7)

### Tool Configuration
- **Plan search**: Database path and default settings
- **User cache**: Mock user data location
- **Booking**: Confirmation and processing settings

### Evaluation Configuration
- **Scenarios**: Test case definitions
- **Metrics**: Evaluation criteria for each agent
- **Execution**: Parallel vs sequential testing

## Customization

### For Development
```yaml
development:
  debug_mode: true
  mock_external_apis: false
  cache_responses: false
```

### For Production
```yaml
development:
  debug_mode: false
  mock_external_apis: false
  cache_responses: true
```

### For Testing
```yaml
testing:
  test_user: "user_003"  # Guest user
  test_scenarios_limit: 5  # Run only first 5 tests
```

## Configuration Loading

The configuration is loaded by `src/utils.py`:

```python
from src.utils import load_config

config = load_config()
print(config['agents']['esim_agent']['model'])
```

## Validation

Run configuration validation:

```bash
python -c "from src.utils import load_config; load_config()"
```

## Troubleshooting

**Issue: API Key not found**
- Ensure `.env` file exists in project root
- Check environment variable names match `config.yaml`

**Issue: Weave connection fails**
- Verify WANDB_API_KEY is set
- Update `weave.entity` with your W&B username/team

**Issue: Model not found**
- Update to latest available model names
- Check [OpenAI Platform](https://platform.openai.com/docs/models)

