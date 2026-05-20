"""
styles.py — Global CSS for the Agentic HR Portal.

Call inject_styles() once at app startup to apply all shared styles.
"""

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Global Typography */
html, body, p, h1, h2, h3, h4, h5, h6, label, button, input, textarea, select {
    font-family: 'Outfit', sans-serif !important;
}

/* Main Title Styling with gradient */
.main-title {
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-bottom: 0.5rem !important;
    padding-bottom: 10px;
}

/* Description subtitle */
.subtitle {
    color: #64748b;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

/* Sidebar glassmorphism theme */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}

/* Sidebar text color adjustments */
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
}

/* Card designs */
.job-card {
    background-color: rgba(128, 128, 128, 0.05);
    border: 1px solid rgba(128, 128, 128, 0.15);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.job-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    border-color: rgba(99, 102, 241, 0.4);
}

.candidate-card {
    background-color: rgba(128, 128, 128, 0.03);
    border: 1px solid rgba(128, 128, 128, 0.1);
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 12px;
}

/* Login panel styling */
.login-box {
    background-color: rgba(128, 128, 128, 0.05);
    border: 1px solid rgba(128, 128, 128, 0.15);
    border-radius: 16px;
    padding: 40px;
    margin-top: 50px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
}

/* Badges */
.role-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
    display: inline-block;
    margin-bottom: 10px;
}
.role-hr {
    background-color: rgba(99, 102, 241, 0.15);
    color: #6366f1;
    border: 1px solid rgba(99, 102, 241, 0.3);
}
.role-candidate {
    background-color: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.role-employee {
    background-color: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

/* Score badges */
.score-badge {
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 0.85rem;
    float: right;
}
.score-high {
    background-color: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.score-medium {
    background-color: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
.score-low {
    background-color: rgba(239, 68, 68, 0.15);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Document upload confirmation badges */
.upload-success {
    padding: 6px 12px;
    background-color: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 6px;
    color: #10b981;
    font-size: 0.85rem;
    font-weight: 500;
    margin-top: 4px;
    display: inline-block;
}
</style>
"""


def inject_styles() -> None:
    """Injects the shared CSS into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)
