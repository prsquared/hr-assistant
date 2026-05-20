"""
data_store.py — SQLite3-based persistence layer.

Manages a single SQLite database:
  - data/hr_assistant.db

Tables:
  - jobs         : Active job openings
  - applications : Candidate applications with ATS scores

Also manages the data/policies/ directory for uploaded HR policy PDFs.
Provides an init_db() call that seeds mock data on first run.
"""

import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "hr_assistant.db")
POLICIES_DIR = os.path.join(DATA_DIR, "policies")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

@contextmanager
def _get_conn():
    """Yields a sqlite3 connection with row_factory set for dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Converts a sqlite3.Row to a plain dict."""
    return dict(row)


# ---------------------------------------------------------------------------
# Schema & seed data
# ---------------------------------------------------------------------------

def init_db():
    """
    Creates the data directory, SQLite database, tables, policies folder,
    and seeds mock data if the tables are empty.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(POLICIES_DIR, exist_ok=True)

    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id          TEXT PRIMARY KEY,
                title       TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at  TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id               TEXT PRIMARY KEY,
                job_id           TEXT NOT NULL,
                candidate_name   TEXT NOT NULL,
                resume_filename  TEXT NOT NULL,
                resume_text      TEXT NOT NULL,
                ats_score        INTEGER NOT NULL,
                fit_reason       TEXT NOT NULL,
                applied_at       TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
        """)

        # Seed mock jobs only if the table is empty
        job_count = conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        if job_count == 0:
            now = datetime.now().isoformat()
            conn.executemany(
                "INSERT INTO jobs (id, title, description, created_at) VALUES (?, ?, ?, ?)",
                [
                    (
                        "job-python-ai",
                        "Software Engineer (Python/AI)",
                        (
                            "We are looking for a Python Software Engineer to build agentic workflows "
                            "and LLM-powered applications. Requirements: Experience with Python, "
                            "LangChain, Streamlit, and OpenAI APIs."
                        ),
                        now,
                    ),
                    (
                        "job-hr-mgr",
                        "HR Manager",
                        (
                            "We are seeking a senior HR Manager to manage employee relations, "
                            "policy enforcement, and talent acquisition. Experience in enterprise "
                            "HR policy design is preferred."
                        ),
                        now,
                    ),
                ],
            )

        # Seed mock applications only if the table is empty
        app_count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
        if app_count == 0:
            now = datetime.now().isoformat()
            conn.executemany(
                """INSERT INTO applications
                   (id, job_id, candidate_name, resume_filename, resume_text,
                    ats_score, fit_reason, applied_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        "app-alice",
                        "job-python-ai",
                        "Alice Chen",
                        "alice_resume.pdf",
                        (
                            "Alice Chen. Python developer with 4 years of experience building web "
                            "applications. Expert in Django, Flask, Streamlit, and OpenAI API integrations."
                        ),
                        92,
                        (
                            "Alice is a strong fit. She has hands-on experience with Python, Streamlit, "
                            "and OpenAI API, matching the core technical requirements for the AI Software "
                            "Engineer role."
                        ),
                        now,
                    ),
                    (
                        "app-bob",
                        "job-python-ai",
                        "Bob Smith",
                        "bob_resume.txt",
                        (
                            "Bob Smith. Experienced recruiter and HR professional. "
                            "Skills in employee management, payroll, and recruiting."
                        ),
                        35,
                        (
                            "Bob has an HR background and lacks the required technical programming "
                            "skills in Python, LangChain, or Streamlit needed for this engineering position."
                        ),
                        now,
                    ),
                ],
            )


# ---------------------------------------------------------------------------
# Job helpers
# ---------------------------------------------------------------------------

def load_jobs() -> list:
    """Loads and returns all job openings as a list of dicts."""
    init_db()
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM jobs ORDER BY created_at").fetchall()
    return [_row_to_dict(r) for r in rows]


def save_job(title: str, description: str) -> dict:
    """Creates and persists a new job opening. Returns the new job dict."""
    init_db()
    new_job = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "description": description,
        "created_at": datetime.now().isoformat(),
    }
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO jobs (id, title, description, created_at) VALUES (?, ?, ?, ?)",
            (new_job["id"], new_job["title"], new_job["description"], new_job["created_at"]),
        )
    return new_job


def delete_job(job_id: str) -> None:
    """Deletes a job opening and all associated candidate applications.

    Args:
        job_id: The ID of the job to remove.
    """
    init_db()
    with _get_conn() as conn:
        conn.execute("DELETE FROM applications WHERE job_id = ?", (job_id,))
        conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))



# ---------------------------------------------------------------------------
# Application helpers
# ---------------------------------------------------------------------------

def load_applications() -> list:
    """Loads and returns all candidate applications as a list of dicts."""
    init_db()
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM applications ORDER BY applied_at").fetchall()
    return [_row_to_dict(r) for r in rows]


def save_application(
    job_id: str,
    candidate_name: str,
    resume_filename: str,
    resume_text: str,
    ats_score: int,
    fit_reason: str,
) -> dict:
    """Persists a candidate's job application. Returns the saved application dict."""
    init_db()
    new_app = {
        "id": str(uuid.uuid4())[:8],
        "job_id": job_id,
        "candidate_name": candidate_name,
        "resume_filename": resume_filename,
        "resume_text": resume_text,
        "ats_score": int(ats_score),
        "fit_reason": fit_reason,
        "applied_at": datetime.now().isoformat(),
    }
    with _get_conn() as conn:
        conn.execute(
            """INSERT INTO applications
               (id, job_id, candidate_name, resume_filename, resume_text,
                ats_score, fit_reason, applied_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                new_app["id"],
                new_app["job_id"],
                new_app["candidate_name"],
                new_app["resume_filename"],
                new_app["resume_text"],
                new_app["ats_score"],
                new_app["fit_reason"],
                new_app["applied_at"],
            ),
        )
    return new_app


def get_applications_for_job(job_id: str) -> list:
    """Returns all applications for a given job ID."""
    init_db()
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM applications WHERE job_id = ? ORDER BY applied_at",
            (job_id,),
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


def has_applied(job_id: str, candidate_name: str) -> bool:
    """Checks if a candidate has already applied for a given job."""
    init_db()
    with _get_conn() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM applications WHERE job_id = ? AND LOWER(candidate_name) = LOWER(?)",
            (job_id, candidate_name),
        ).fetchone()[0]
    return count > 0


def get_top_candidates(job_id: str, top_n: int = 3) -> list:
    """Returns the top N candidates for a job, ranked by ATS score descending."""
    init_db()
    with _get_conn() as conn:
        rows = conn.execute(
            """SELECT * FROM applications
               WHERE job_id = ?
               ORDER BY ats_score DESC
               LIMIT ?""",
            (job_id, top_n),
        ).fetchall()
    return [_row_to_dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Policy helpers
# ---------------------------------------------------------------------------

def get_policies_list() -> list:
    """Returns filenames of all uploaded HR policy PDFs."""
    os.makedirs(POLICIES_DIR, exist_ok=True)
    return [f for f in os.listdir(POLICIES_DIR) if f.endswith(".pdf")]
