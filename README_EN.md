# W&B Hands-on Assets

[日本語](README.md)

This repository collects sample code, notebooks, configuration files, and evaluation assets used in Weights & Biases (W&B) hands-on workshops. The materials cover W&B Models, W&B Weave, W&B Training, experiment tracking, LLM application tracing, evaluation, monitoring, and Agentic RL through runnable examples.

Each hands-on is organized as an independent directory or notebook. See the README inside each hands-on directory for detailed setup and execution steps.

## Hands-on List

| Hands-on | Location | What it covers |
| --- | --- | --- |
| W&B Models 101 | [models/W&B_models_intro_notebook.ipynb](models/W%26B_models_intro_notebook.ipynb) | An introductory notebook for the `wandb` library, including login, Run creation, metric and media logging, Tables, Artifacts, and lineage tracking for data and models. |
| Weave Introduction Hands-on | [weave_introduction_handson/](weave_introduction_handson/) | A W&B Weave hands-on for LLM application tracing, prompt/dataset/model/Scorer management, offline evaluation, online feedback, guardrails, and monitoring. It includes both Japanese and English scripts. |
| eSIM Agent Demo | [esim-agent-demo/](esim-agent-demo/) | A multi-agent demo for an eSIM service using the OpenAI Agents SDK and W&B Weave. It includes plan search, booking, RAG Q&A, guardrails, Weave tracing, evaluation scenarios, and Scorers. |
| ART-E: Email Search Agent | [ART-E/](ART-E/) | A hands-on project for training an email search agent with Agentic RL on the Enron email dataset. It covers ART, W&B Training / Serverless RL, W&B / Weave logging, and inference evaluation for the trained model. |
