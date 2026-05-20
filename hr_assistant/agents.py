"""
agents.py — Agent factory functions for the multi-agent HR system.

Architecture:
  ┌────────────────────────────────────┐
  │         Supervisor Agent           │  ← Entry point (orchestrator)
  │  Routes requests via tool-calling  │
  └─────────┬──────────────────────────┘
            │
    ┌───────┴───────┐
    ▼               ▼
  Recruiting      Policy
  Agent           Agent (RAG)
  (5 tools)       (FAISS retrieval)

Public API:
  get_recruiting_agent(llm) -> AgentExecutor
  get_supervisor_agent(llm, recruiting_executor, policy_rag_chain) -> AgentExecutor
"""

from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

from hr_assistant.tools import (
    parse_resume,
    match_job_description,
    generate_interview_questions,
    list_jobs,
    get_candidates,
)
from hr_assistant.prompts import SUPERVISOR_PROMPT, RECRUITING_AGENT_PROMPT


def get_recruiting_agent(llm) -> AgentExecutor:
    """Builds the Recruiting Agent equipped with resume and job-matching tools.

    Args:
        llm: A LangChain-compatible LLM (e.g. ChatOpenAI).

    Returns:
        An AgentExecutor that accepts {"input": str} and returns {"output": str}.
    """
    tools = [
        parse_resume,
        match_job_description,
        generate_interview_questions,
        list_jobs,
        get_candidates,
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", RECRUITING_AGENT_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)


def get_supervisor_agent(llm, recruiting_executor, policy_rag_chain=None) -> AgentExecutor:
    """Builds the Supervisor Agent that routes to Recruiting or Policy agents.

    The Recruiting and Policy agents are exposed to the Supervisor as callable
    tools, implementing an "Agent-as-a-Tool" pattern for clean orchestration.

    Args:
        llm:                 A LangChain-compatible LLM.
        recruiting_executor: A pre-built Recruiting AgentExecutor.
        policy_rag_chain:    A pre-built RAG retrieval chain, or None if no
                             policies have been uploaded yet.

    Returns:
        An AgentExecutor that accepts {"input": str} and returns {"output": str}.
    """

    @tool
    def recruiting_agent_tool(query: str) -> str:
        """Delegate to the Recruiting Agent for resume parsing, candidate evaluation,
        job matching, and interview question generation."""
        response = recruiting_executor.invoke({"input": query})
        return response["output"]

    @tool
    def policy_agent_tool(query: str) -> str:
        """Delegate to the Policy Agent for HR policy, vacation, benefits, and
        employee handbook questions."""
        if policy_rag_chain is None:
            return (
                "The policy knowledge base is not yet initialized. "
                "Please ask HR to upload a policy PDF first."
            )
        response = policy_rag_chain.invoke({"input": query})
        return response["answer"]

    tools = [recruiting_agent_tool, policy_agent_tool]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)
