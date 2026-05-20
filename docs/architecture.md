# Agentic HR Assistant — Architecture

```mermaid
flowchart TD
    subgraph UI["Streamlit UI"]
        HR["🏢 HR Portal"]
        Candidate["👤 Candidate Portal"]
        Employee["👩‍💼 Employee Portal"]
    end

    subgraph Agents["Multi-Agent System (LangChain)"]
        SUP["🧠 Supervisor Agent\ngpt-4o + Memory"]
        REC["🔍 Recruiting Agent\ngpt-4o-mini · 6 tools"]
        POL["📖 Policy Agent\nRAG + Memory"]
    end

    subgraph Storage["Data Layer"]
        DB["🗃️ SQLite\njobs · applications"]
        FAISS["🗄️ FAISS Vector Store\nHR Policy PDFs"]
    end

    subgraph External["External Services"]
        OAI["☁️ OpenAI API"]
        DDG["🌐 DuckDuckGo Search"]
    end

    HR --> SUP
    Employee --> POL
    Candidate --> DB

    SUP -->|recruiting_agent_tool| REC
    SUP -->|policy_agent_tool| POL

    REC --> DB
    REC -.->|search_market_intelligence| DDG
    POL --> FAISS

    Agents --> OAI
```
