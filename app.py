"""
app.py — Entry point for the Agentic HR Portal.

Responsibilities:
  - Page configuration
  - Inject shared CSS
  - Initialise session state
  - Route to the correct portal based on login state / role
"""

import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from hr_assistant.ui.styles import inject_styles
from hr_assistant.ui.login import render_login, render_sidebar
from hr_assistant.ui.hr_portal import render_hr_portal
from hr_assistant.ui.candidate_portal import render_candidate_portal
from hr_assistant.ui.employee_portal import render_employee_portal

# ---------------------------------------------------------------------------
# Page config (must be the first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Agentic HR Portal", page_icon="👔", layout="wide")
inject_styles()

st.markdown('<h1 class="main-title">👔 Agentic HR Assistant</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">A role-based AI application simulating HR operations, '
    "Candidate applications, and Employee Policy Q&A.</p>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("role", None)
st.session_state.setdefault("employee_messages", [])

# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------

if not st.session_state.logged_in:
    render_login()
else:
    render_sidebar()

    portal_map = {
        "hr": render_hr_portal,
        "candidate": render_candidate_portal,
        "employee": render_employee_portal,
    }
    portal_map[st.session_state.role]()
