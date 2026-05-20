"""
candidate_portal.py — Candidate Careers portal view.

Exported functions:
    render_candidate_portal() — Renders the careers page where candidates
                                can browse open roles and submit applications.
"""

import streamlit as st

from hr_assistant.data_store import load_jobs, save_application
from hr_assistant.evaluator import evaluate_resume_for_job


def render_candidate_portal() -> None:
    """Renders the candidate portal: job listings with inline application forms."""
    st.markdown("## 💼 Candidate Careers Portal")
    st.markdown("### Available Job Openings")

    jobs = load_jobs()
    if not jobs:
        st.info("There are no job openings posted at this time. Please check back later.")
        return

    for job in jobs:
        _render_job_listing(job)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _render_job_listing(job: dict) -> None:
    """Renders a single job card followed by a collapsible application form."""
    st.markdown(
        f"""
        <div class="job-card">
            <h3 style="margin-top: 0; color: #1e293b;">{job['title']}</h3>
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 12px;">
                Posted: {job['created_at'][:10]}
            </p>
            <p style="white-space: pre-line; color: #334155; line-height: 1.6;">
                {job['description']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(f"Apply for {job['title']}"):
        _render_application_form(job)


def _render_application_form(job: dict) -> None:
    """Renders the resume upload form and handles submission logic."""
    cand_name = st.text_input("Your Full Name", key=f"name_{job['id']}")
    resume_file = st.file_uploader(
        "Upload Resume (PDF or TXT)", type=["pdf", "txt"], key=f"res_{job['id']}"
    )

    if not st.button("Submit Application", key=f"btn_{job['id']}", use_container_width=True):
        return

    if not cand_name:
        st.error("Please enter your full name.")
        return
    if not resume_file:
        st.error("Please upload your resume.")
        return

    with st.spinner("Analyzing resume matching score..."):
        resume_text = _extract_resume_text(resume_file)
        if resume_text:
            eval_result = evaluate_resume_for_job(resume_text, job["description"])
            save_application(
                job_id=job["id"],
                candidate_name=cand_name,
                resume_filename=resume_file.name,
                resume_text=resume_text,
                ats_score=eval_result["ats_score"],
                fit_reason=eval_result["fit_reason"],
            )
            st.success("✓ Application successfully submitted!")


def _extract_resume_text(resume_file) -> str:
    """
    Extracts plain text from an uploaded PDF or TXT resume file.
    Returns an empty string and shows an error if extraction fails.
    """
    if resume_file.name.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(resume_file)
            text = "\n".join(
                page.extract_text() for page in reader.pages if page.extract_text()
            )
            return text.strip()
        except Exception as e:
            st.error(f"Error parsing resume PDF: {e}")
            return ""
    else:
        try:
            return resume_file.read().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading resume text: {e}")
            return ""
