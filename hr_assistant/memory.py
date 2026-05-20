"""
memory.py — LangChain memory factory functions for the HR Assistant.

Provides session-scoped memory objects that survive Streamlit reruns but reset
on browser refresh, keeping state cleanly isolated per user session.

Public API:
    get_agent_memory(llm, session_key) -> ConversationSummaryBufferMemory
    get_rag_memory(session_key)        -> ConversationBufferWindowMemory
"""

import streamlit as st
from langchain_classic.memory import ConversationSummaryBufferMemory, ConversationBufferWindowMemory


def get_agent_memory(llm, session_key: str = "agent_memory") -> ConversationSummaryBufferMemory:
    """Returns (or creates) a ConversationSummaryBufferMemory for agent chat.

    Summarises older messages once the token buffer exceeds max_token_limit,
    keeping the context window manageable for long conversations.

    The memory outputs to the ``chat_history`` key expected by the agent
    ChatPromptTemplate MessagesPlaceholder.

    Args:
        llm:         A LangChain-compatible LLM used for summarisation.
        session_key: The st.session_state key to store the memory under.

    Returns:
        A ConversationSummaryBufferMemory instance, reused across reruns.
    """
    if session_key not in st.session_state:
        st.session_state[session_key] = ConversationSummaryBufferMemory(
            llm=llm,
            max_token_limit=1000,
            memory_key="chat_history",
            return_messages=True,
            output_key="output",
        )
    return st.session_state[session_key]


def get_rag_memory(session_key: str = "policy_memory") -> ConversationBufferWindowMemory:
    """Returns (or creates) a ConversationBufferWindowMemory for the RAG chatbot.

    Keeps only the last ``k`` conversation turns to provide focused context
    without overwhelming the retrieval chain's prompt.

    Args:
        session_key: The st.session_state key to store the memory under.

    Returns:
        A ConversationBufferWindowMemory instance, reused across reruns.
    """
    if session_key not in st.session_state:
        st.session_state[session_key] = ConversationBufferWindowMemory(
            k=5,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )
    return st.session_state[session_key]
