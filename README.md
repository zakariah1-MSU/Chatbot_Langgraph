# Chatbot LangGraph

A conversational chatbot built with [LangGraph](https://langchain-ai.github.io/langgraph/) and [LangChain](https://www.langchain.com/), powered by OpenAI, with a [Streamlit](https://streamlit.io/) web interface.

## Overview

This project implements a minimal chat agent as a LangGraph state machine. User messages flow through a single `chat_node` that calls an OpenAI chat model and returns the assistant reply. Conversation state is persisted in memory via LangGraph's checkpointer, so the graph can maintain context within a thread.

```
User input → Streamlit UI → LangGraph (chat_node) → OpenAI → Response
```

## Project structure

| File | Description |
|------|-------------|
| `langgraph_backend.py` | LangGraph graph definition, OpenAI LLM setup, and in-memory checkpointer |
| `streamlit_frontend.py` | Streamlit chat UI — run this to start the app |
| `pyproject.toml` | Project metadata and dependencies (managed with [uv](https://docs.astral.sh/uv/)) |

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or another Python package manager
- An [OpenAI API key](https://platform.openai.com/api-keys)

## Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Chatbot_Langgraph
   ```

2. **Install dependencies**

   ```bash
   uv sync
   ```

3. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   OPENAI_API_KEY=your-api-key-here
   ```

   LangChain reads `OPENAI_API_KEY` automatically when the backend loads.

## Usage

Start the Streamlit chat interface:

```bash
uv run streamlit run streamlit_frontend.py
```

Open the URL shown in the terminal (typically `http://localhost:8501`) and type messages in the chat input.

## How it works

**Backend (`langgraph_backend.py`)**

- Defines a `ChatState` with a `messages` field that accumulates conversation history.
- A single `chat_node` invokes `ChatOpenAI` with the current messages and appends the model response.
- The graph is compiled with `InMemorySaver` for thread-scoped checkpointing.

**Frontend (`streamlit_frontend.py`)**

- Renders chat history from Streamlit session state.
- Sends each user message to the compiled LangGraph agent and displays the assistant reply.

## Tech stack

- [LangGraph](https://github.com/langchain-ai/langgraph) — agent workflow orchestration
- [LangChain](https://github.com/langchain-ai/langchain) — LLM integration
- [langchain-openai](https://python.langchain.com/docs/integrations/chat/openai/) — OpenAI chat models
- [Streamlit](https://streamlit.io/) — web UI
- [python-dotenv](https://github.com/theskumar/python-dotenv) — environment variable loading

## License

Add your license here.
