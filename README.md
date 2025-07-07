# AI Agents System

This project features specialized AI agents for backend and frontend ticket resolution, powered by [LangChain](https://www.langchain.com/) and OpenAI.

## Features

- **LangChain-based Agents**: Both backend and frontend agents now utilize LangChain's LLMChain abstractions for prompt management and output parsing.
- **Orchestrator Router**: The orchestrator agent uses a LangChain router chain to dispatch tickets to the correct agent based on description.
- **Easy LLM Configuration**: LLM settings (model, API key) are managed in `utils/langchain_helpers.py`.

## Usage

Make sure you have `OPENAI_API_KEY` set in your environment.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the orchestrator agent via CLI:

```bash
cat ticket.json | python agents/orchestrator_agent.py --stdin
```

Where `ticket.json` is a JSON file with at least `descripcion`, `id`, and `tipo` fields.