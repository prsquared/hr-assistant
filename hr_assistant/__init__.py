"""
hr_assistant — Core application package for the Agentic HR Recruiting Assistant.

Modules:
    data_store  — SQLite3-based persistence layer (jobs, applications, policies)
    evaluator   — LLM-powered ATS resume scoring
    prompts     — System prompt strings for all agents
    rag         — FAISS vector store creation and RAG chain
    tools       — LangChain @tool definitions for the Recruiting Agent
    agents      — Supervisor and Recruiting agent factory functions
"""
