"""
hr_portal.py — HR Manager portal view.

Exported functions:
    render_hr_portal() — Renders the three-tab HR portal:
        - 📋 Company Policy  : upload & list policy PDFs
        - 💼 Job Openings    : create jobs, view ATS-ranked candidates
        - 🤖 Agent Chat      : Supervisor agent chat interface
"""

import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.tracers.langchain import wait_for_all_tracers
from langchain_openai import ChatOpenAI

from hr_assistant.agents import get_recruiting_agent, get_supervisor_agent
from hr_assistant.data_store import (
    POLICIES_DIR,
    delete_job,
    get_policies_list,
    get_top_candidates,
    load_jobs,
    save_job,
)
from hr_assistant.memory import get_agent_memory
from hr_assistant.rag import get_rag_chain, load_vector_store, rebuild_index_from_policies


def render_hr_portal() -> None:
    """Renders the full HR Manager portal with three tabs."""
    st.markdown("## 🏢 HR Portal")
    tab_policy, tab_jobs, tab_chat = st.tabs(
        ["📋 Company Policy", "💼 Job Openings", "🤖 Agent Chat"]
    )

    with tab_policy:
        _render_policy_tab()

    with tab_jobs:
        _render_jobs_tab()

    with tab_chat:
        _render_agent_chat_tab()


# ---------------------------------------------------------------------------
# Private tab renderers
# ---------------------------------------------------------------------------

def _render_policy_tab() -> None:
    st.markdown("### Upload and Index Policies")

    policy_file = st.file_uploader("Upload HR Policy PDF document", type=["pdf"])
    if policy_file:
        with st.spinner("Processing & indexing PDF..."):
            import os
            os.makedirs(POLICIES_DIR, exist_ok=True)
            pdf_path = os.path.join(POLICIES_DIR, policy_file.name)
            with open(pdf_path, "wb") as f:
                f.write(policy_file.getbuffer())
            try:
                rebuild_index_from_policies()
                st.markdown(
                    f'<div class="upload-success">✓ Company Policy "{policy_file.name}" indexed successfully!</div>',
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.error(f"Error processing PDF: {e}")

    st.markdown("---")
    st.markdown("### Uploaded Policy Files")
    policies = get_policies_list()
    if not policies:
        st.info("No policy files uploaded yet.")
    else:
        for doc in policies:
            st.markdown(f"📄 **{doc}**")


def _render_jobs_tab() -> None:
    st.markdown("### Job Postings & ATS Candidate Matching")

    with st.expander("➕ Add New Job Opening"):
        new_title = st.text_input("Job Title", placeholder="e.g. Senior Frontend Engineer")
        new_desc = st.text_area(
            "Job Description Requirements",
            placeholder="Enter core skills, roles and responsibilities...",
            height=150,
        )
        if st.button("Create Job Posting", use_container_width=True):
            if new_title and new_desc:
                save_job(new_title, new_desc)
                st.success(f"✓ Job opening for '{new_title}' posted successfully!")
                st.rerun()
            else:
                st.error("Please provide both a Title and a Description.")

    st.markdown("---")
    jobs = load_jobs()
    if not jobs:
        st.info("No active job openings.")
        return

    selected_job = st.selectbox(
        "Select job opening to view details & applications:",
        jobs,
        format_func=lambda x: x["title"],
    )
    if not selected_job:
        return

    # ---- Delete job ----
    confirm_key = f"confirm_delete_{selected_job['id']}"
    col_info, col_del = st.columns([5, 1])
    with col_del:
        if not st.session_state.get(confirm_key):
            if st.button(
                "🗑️ Delete",
                key=f"del_{selected_job['id']}",
                use_container_width=True,
                help="Delete this job listing and all its applications",
            ):
                st.session_state[confirm_key] = True
                st.rerun()
        else:
            st.warning("Delete this job and all its applications?")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Confirm", key=f"confirm_yes_{selected_job['id']}", use_container_width=True):
                    delete_job(selected_job["id"])
                    st.session_state.pop(confirm_key, None)
                    st.success(f"'{selected_job['title']}' deleted.")
                    st.rerun()
            with c2:
                if st.button("❌ Cancel", key=f"confirm_no_{selected_job['id']}", use_container_width=True):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()

    st.markdown(
        f"""
        <div style="background-color: rgba(128,128,128,0.05); padding: 15px;
                    border-radius: 8px; border: 1px solid rgba(128,128,128,0.15);
                    margin-bottom: 20px;">
            <strong>Job Description:</strong><br/>
            <p style="white-space: pre-line; margin-top: 5px; color: #475569;">
                {selected_job['description']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Best Fit Candidates")
    top_x = st.slider("Show Top Candidates", min_value=1, max_value=10, value=3)
    candidates = get_top_candidates(selected_job["id"], top_n=top_x)

    if not candidates:
        st.info("No candidate applications for this job yet.")
        return

    for cand in candidates:
        _render_candidate_card(cand)


def _render_candidate_card(cand: dict) -> None:
    score = cand["ats_score"]
    if score >= 80:
        badge_class = "score-high"
    elif score >= 50:
        badge_class = "score-medium"
    else:
        badge_class = "score-low"

    st.markdown(
        f"""
        <div class="candidate-card">
            <span class="score-badge {badge_class}">{score}% Match</span>
            <strong style="font-size: 1.1rem; color: #1e293b;">👤 {cand['candidate_name']}</strong>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 4px; margin-bottom: 8px;">
                Applied: {cand['applied_at'][:10]} | Resume: {cand['resume_filename']}
            </p>
            <div style="background-color: rgba(99,102,241,0.05); border-left: 3px solid #6366f1;
                        padding: 10px; border-radius: 4px; margin-top: 8px;">
                <strong style="color: #4f46e5; font-size: 0.9rem;">AI Fit Analysis:</strong><br/>
                <span style="font-style: italic; color: #334155;">{cand['fit_reason']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander(f"View resume text for {cand['candidate_name']}"):
        st.text_area(
            "Extracted Resume",
            value=cand["resume_text"],
            height=150,
            disabled=True,
            key=f"res_txt_{cand['id']}",
        )


def _render_agent_chat_tab() -> None:
    st.markdown("### HR Assistant Supervisor Agent")
    st.markdown(
        "Use this agent to ask questions about company policy or request candidate "
        "evaluation based on their resumes."
    )

    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = [
            {
                "role": "assistant",
                "content": "Hello! I am your HR Assistant Supervisor. How can I help you with recruiting or policy queries today?",
            }
        ]

    # Memory clear button
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear Memory", use_container_width=True, help="Reset conversation memory"):
            st.session_state.agent_messages = [
                {
                    "role": "assistant",
                    "content": "Memory cleared! Starting a fresh conversation.",
                }
            ]
            if "agent_memory" in st.session_state:
                del st.session_state["agent_memory"]
            st.rerun()

    for msg in st.session_state.agent_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    agent_input = st.chat_input("Ask the Supervisor Agent...", key="hr_agent_input")
    if not agent_input:
        return

    st.session_state.agent_messages.append({"role": "user", "content": agent_input})
    with st.chat_message("user"):
        st.markdown(agent_input)

    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        try:
            llm = ChatOpenAI(model="gpt-4o", temperature=0)

            # Initialise (or retrieve) session-scoped conversation memory
            memory = get_agent_memory(llm)

            recruiting_executor = get_recruiting_agent(llm, memory=memory)

            vector_store = load_vector_store()
            policy_rag_chain = get_rag_chain(vector_store, llm) if vector_store else None

            supervisor = get_supervisor_agent(
                llm, recruiting_executor, policy_rag_chain, memory=memory
            )
            response = supervisor.invoke(
                {"input": agent_input},
                config={"callbacks": [st_callback]},
            )
            wait_for_all_tracers()

            st.markdown(response["output"])
            st.session_state.agent_messages.append(
                {"role": "assistant", "content": response["output"]}
            )
        except Exception as e:
            st.error(f"An error occurred: {e}")
