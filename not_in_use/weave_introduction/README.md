# W&B Weave Hands-on

[Japanese version](README_JP.md)

This repository contains hands-on materials for learning W&B Weave, a framework for tracking, experimenting with, evaluating, deploying, and improving LLM-based applications.

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/olachinkei/wandb-handson.git
   cd wandb-handson/weave_introduction
   ```

2. **Set up the environment using uv (recommended):**
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create and activate virtual environment
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   uv pip install -r weave_introduction/requirements.txt
   ```

   **Alternative using pip:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**

   ```bash
   export WANDB_BASE_URL="https://api.wandb.ai"
   export WANDB_API_KEY="your_wandb_api_key_here" 
   export GOOGLE_API_KEY="your_google_api_key" # optional if you want to try video
   export OPENAI_API_KEY="your_openai_api_key_here"
   # If you want to use Azure OpenAI, set the following:
   export AZURE_OPENAI_API_KEY="your_azureopenai_api_key_here"
   export AZURE_OPENAI_ENDPOINT="https://<your>.openai.azure.com/"
   export AZURE_OPENAI_DEPLOYMENT="name of your model"
   ```
   
   **Note:** 
   - WANDB_API_KEY can be obtained from [here](https://docs.wandb.ai/support/find_api_key/).
   - If you are using dedicated cloud or on-premises environments, please change the `WANDB_BASE_URL` accordingly.
   - To use Azure OpenAI, set `USE_AZURE_OPENAI=true` in your environment variables.

4. ** wandb login *
   ```bash  
   wandb login
   ```

5. **Launch Jupyter Lab and open the notebook:**
   ```bash
   jupyter lab weave_intro_notebook.ipynb
   ```

## What's Included

- `weave_introduction/`: Contains the main hands-on notebook
  - `weave_intro_notebook.ipynb`: Interactive notebook for learning W&B Weave
  - `requirements.txt`: Python dependencies

## Resources

- **Documentation**: [W&B Weave Documentation](https://weave-docs.wandb.ai/)
- **Videos**:
  - [Japanese Tutorial](https://www.youtube.com/watch?v=Ua0Wx9fqhDo&t=295s)
  - [English Tutorial](https://www.youtube.com/watch?v=sJNjw6U2Tvg&t=522s) 
