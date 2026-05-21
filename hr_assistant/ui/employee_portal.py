"""
employee_portal.py — Employee Policy Q&A portal view.

Exported functions:
    render_employee_portal() — Renders the RAG-powered policy chatbot for employees.
"""

import streamlit as st
from langchain_core.tracers.langchain import wait_for_all_tracers
from langchain_openai import ChatOpenAI

from hr_assistant.config import BASE_LLM_MODEL
from hr_assistant.memory import get_rag_memory
from hr_assistant.rag import get_rag_chain, load_vector_store
from hr_assistant.callbacks import LoggingCallbackHandler

_WELCOME_MSG = {
    "role": "assistant",
    "content": (
        "Welcome! Ask me any questions regarding company policies, "
        "guidelines, vacation, benefits, and handbooks."
    ),
}


def render_employee_portal() -> None:
    """Renders the employee handbook Q&A chatbot."""
    st.markdown("## 👥 Employee Handbook Portal")

    vector_store = load_vector_store()
    if not vector_store:
        st.warning(
            "⚠️ No company policies have been uploaded or indexed yet. "
            "Please check back after HR uploads policies."
        )
        return

    st.markdown("### Policy Queries")
    _init_chat_history()
    _render_chat_history()
    _handle_user_input(vector_store)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _init_chat_history() -> None:
    """Seeds the employee message history with a welcome message if empty."""
    if not st.session_state.get("employee_messages"):
        st.session_state.employee_messages = [_WELCOME_MSG]


def _render_chat_history() -> None:
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear Memory", use_container_width=True, help="Reset conversation memory"):
            st.session_state.employee_messages = [_WELCOME_MSG]
            if "policy_memory" in st.session_state:
                del st.session_state["policy_memory"]
            st.rerun()
    for msg in st.session_state.employee_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def _handle_user_input(vector_store) -> None:
    user_input = st.chat_input("Ask a question about company policy...")
    if not user_input:
        return

    st.session_state.employee_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching company documents..."):
            try:
                llm = ChatOpenAI(model=BASE_LLM_MODEL, temperature=0, stream_usage=True)
                rag_chain = get_rag_chain(vector_store, llm)

                # Load (or initialise) session-scoped memory for this chatbot
                memory = get_rag_memory()
                history = memory.load_memory_variables({})
                chat_history = history.get("chat_history", [])

                log_callback = LoggingCallbackHandler()
                response = rag_chain.invoke(
                    {
                        "input": user_input,
                        "chat_history": chat_history,
                    },
                    config={"callbacks": [log_callback], "run_name": "Employee_Policy_Agent"},
                )
                wait_for_all_tracers()
                answer = response["answer"]

                # Save this turn into memory
                memory.save_context(
                    {"input": user_input},
                    {"answer": answer},
                )

                st.markdown(answer)
                st.session_state.employee_messages.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
