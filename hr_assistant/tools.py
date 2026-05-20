"""
tools.py — LangChain @tool definitions for the Recruiting Agent.

Each function is decorated with @tool so LangChain can bind it to an agent's
tool-calling interface. Tools are intentionally stateless — they read from the
shared data store but do not modify it.

Tools:
  parse_resume                 — Extract structured info from raw resume text
  match_job_description        — Score a resume against a job description
  generate_interview_questions — Generate targeted interview questions
  list_jobs                    — Return all active job postings
  get_candidates               — Return candidate applications (optionally filtered by job)
  search_market_intelligence   — Web search for salary benchmarks and skills trends
"""

import json

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from hr_assistant.data_store import load_jobs, load_applications

_ddg_search = DuckDuckGoSearchRun()


@tool
def parse_resume(resume_text: str) -> str:
    """Extracts skills, experience, education, and a summary from a resume."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""\
Extract the following structured information from the resume below:
  - Skills (bullet list)
  - Experience (brief summary)
  - Education (brief summary)
  - Overall Summary (1–2 sentences)

Resume:
{resume_text}
"""
    return llm.invoke(prompt).content


@tool
def match_job_description(resume_text: str, jd_text: str) -> str:
    """Compares a resume to a job description and returns a match analysis."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = f"""\
Compare the candidate's resume to the job description below.

Provide:
  - Match Score (0–100%)
  - Missing Skills
  - Key Strengths
  - Recommendation Summary

Resume:
{resume_text}

Job Description:
{jd_text}
"""
    return llm.invoke(prompt).content


@tool
def generate_interview_questions(missing_skills_or_role_reqs: str) -> str:
    """Generates 3–5 targeted interview questions for a candidate's skill gaps."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    prompt = f"""\
Generate 3–5 targeted, professional interview questions to assess the following
missing skills or role requirements:

{missing_skills_or_role_reqs}

Make each question specific and behavioural or technical where appropriate.
"""
    return llm.invoke(prompt).content


@tool
def list_jobs(query: str = "") -> str:
    """Returns all active job postings as a JSON list (id, title, description)."""
    jobs = load_jobs()
    if not jobs:
        return "No active job postings found."
    return json.dumps(jobs, indent=2)


@tool
def get_candidates(job_id: str = None) -> str:
    """Returns candidate applications as JSON, optionally filtered by job_id."""
    apps = load_applications()
    if job_id:
        apps = [app for app in apps if app.get("job_id") == job_id]
    if not apps:
        return "No applications found."
    return json.dumps(apps, indent=2)


@tool
def search_market_intelligence(query: str) -> str:
    """Search the web for real-time job market data such as salary benchmarks,
    in-demand skills, hiring trends, or competitor job postings for a given role.
    Use this when the user asks about market rates, typical salaries, or what
    skills are currently trending for a position."""
    try:
        return _ddg_search.run(query)
    except Exception as e:
        return f"Web search failed: {e}"
