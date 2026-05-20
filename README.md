# Agentic HR Assistant

> A take-home project demonstrating a **multi-agent AI system** for HR operations — built with Python, LangChain, OpenAI, FAISS, and Streamlit.

---

## Architecture

The application implements a **Supervisor → Specialist** multi-agent pattern, where a top-level orchestrator routes user requests to purpose-built sub-agents:

```
User Request
     │
     ▼
┌─────────────────────┐
│   Supervisor Agent   │  ← Orchestrator: classifies and delegates requests
│   (GPT-4o)           │
└──────────┬──────────┘
           │ tool-calling
     ┌─────┴──────┐
     ▼            ▼
┌─────────────┐  ┌──────────────────┐
│  Recruiting  │  │   Policy Agent   │
│    Agent     │  │   (RAG + FAISS)  │
│  (GPT-4o-mini│  │  (GPT-4o-mini)   │
│  + 5 tools)  │  │                  │
└─────────────┘  └──────────────────┘
```

| Agent | Role | Implementation |
|---|---|---|
| **Supervisor** | Routes requests to the right agent | `AgentExecutor` with two agent-as-tool delegates |
| **Recruiting Agent** | Resume parsing, ATS scoring, interview Q generation | `AgentExecutor` with 5 LangChain `@tool` functions |
| **Policy Agent** | Employee handbook / HR policy Q&A | FAISS vector store + LangChain RAG chain |

---

## Features by Role

| Portal | Feature |
|---|---|
| **HR Manager** | Upload & index HR policy PDFs · Post job openings · View ranked candidates with ATS scores · Chat with the Supervisor Agent |
| **Employee** | Ask natural-language questions about company policies, benefits, and vacation (RAG-powered) |
| **Candidate** | Browse open positions · Submit applications with PDF or TXT resume upload · Automatic ATS scoring on submission |

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io/) |
| Agents | [LangChain](https://python.langchain.com/) — `AgentExecutor`, `create_openai_tools_agent` |
| LLMs | [OpenAI](https://platform.openai.com/) — `gpt-4o` (Supervisor), `gpt-4o-mini` (tools & RAG) |
| Vector Search | [FAISS](https://github.com/facebookresearch/faiss) (local, persisted to disk) |
| PDF Parsing | [PyPDF](https://pypdf.readthedocs.io/) |
| Observability | [LangSmith](https://smith.langchain.com/) tracing (optional) |
| Package Manager | [uv](https://docs.astral.sh/uv/) |

---

## Project Structure

```
hr-assistant/
├── app.py                    # Streamlit entrypoint — UI only, no business logic
├── pyproject.toml            # Project metadata & dependencies (managed by uv)
├── .env.example              # API key template
│
├── hr_assistant/             # Core application package
│   ├── __init__.py
│   ├── agents.py             # Supervisor & Recruiting agent factories
│   ├── tools.py              # LangChain @tool definitions
│   ├── rag.py                # FAISS vector store + RAG chain
│   ├── evaluator.py          # LLM-powered ATS resume scorer
│   ├── prompts.py            # System prompt strings
│   └── data_store.py         # JSON persistence layer
│
└── data/                     # Runtime data (git-ignored)
    ├── jobs.json
    ├── applications.json
    ├── policies/             # Uploaded HR policy PDFs
    └── faiss_index/          # Persisted FAISS vector index
```

---

## Setup

### Prerequisites
- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (fast Python package manager)

### Steps

```bash
# 1. Install uv (if not already installed)
# Windows (PowerShell):
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install dependencies
uv sync

# 3. Configure your API key
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
# Then edit .env and add your OPENAI_API_KEY

# 4. Run the app
uv run streamlit run app.py
```

---

## Example Workflows

**Recruiting (HR Manager chat)**
> *"Who is the best candidate for the Software Engineer (Python/AI) role? Summarize their strengths and generate three interview questions based on their skill gaps."*

**Policy Q&A (Employee portal)**
> *"What is the company's vacation accrual policy for employees in their first year?"*

---

## Design Decisions

- **Agent-as-a-Tool pattern**: The Recruiting and Policy agents are exposed to the Supervisor as callable tools. This keeps orchestration simple and transparent — the Supervisor's reasoning is fully visible via LangSmith tracing.
- **Local FAISS persistence**: The vector index is saved to disk after each PDF upload, so it survives server restarts without requiring an external vector database.
- **Separation of concerns**: `app.py` is a pure UI layer. All business logic lives in `hr_assistant/`, making each module independently testable.

---

## Future Improvements

- **LangGraph**: Migrate from `AgentExecutor` to LangGraph for stateful, cyclical agent workflows
- **Persistent vector DB**: Replace local FAISS with Pinecone or ChromaDB for production-scale retrieval
- **Authentication**: Swap the demo role-selector with a real auth provider (e.g., Auth0)
- **Async execution**: Parallelize tool calls for faster agent responses
