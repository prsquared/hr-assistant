import pytest
import sqlite3
import hr_assistant.data_store as ds

from contextlib import contextmanager

@pytest.fixture
def mock_db(mocker):
    # Create a single in-memory SQLite database
    conn = sqlite3.connect(":memory:")
    
    @contextmanager
    def mock_get_conn():
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
            
    mocker.patch("hr_assistant.data_store._get_conn", side_effect=mock_get_conn)
    
    # Initialize schema and seed data
    ds.init_db()
    
    yield conn
    
    # Actually close the connection at the end of the test
    conn.close()

def test_init_db(mock_db):
    # Verify that jobs and applications tables were created and seeded
    cursor = mock_db.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    assert "jobs" in tables
    assert "applications" in tables

    # Check seeded jobs
    cursor.execute("SELECT COUNT(*) FROM jobs")
    job_count = cursor.fetchone()[0]
    assert job_count == 2

    # Check seeded applications
    cursor.execute("SELECT COUNT(*) FROM applications")
    app_count = cursor.fetchone()[0]
    assert app_count == 2

def test_load_jobs(mock_db):
    jobs = ds.load_jobs()
    assert len(jobs) == 2
    assert jobs[0]["id"] == "job-python-ai"
    assert jobs[0]["title"] == "Software Engineer (Python/AI)"

def test_save_job(mock_db):
    new_job = ds.save_job("DevOps Engineer", "Manage Kubernetes and CI/CD pipelines.")
    assert new_job["title"] == "DevOps Engineer"
    assert new_job["description"] == "Manage Kubernetes and CI/CD pipelines."
    assert "id" in new_job
    
    # Verify saved to db
    jobs = ds.load_jobs()
    assert len(jobs) == 3
    assert any(j["id"] == new_job["id"] for j in jobs)

def test_delete_job(mock_db):
    # Add an application for job-hr-mgr so the applications table is not empty after deletion
    # (which would trigger auto-seeding in load_applications -> init_db)
    ds.save_application(
        job_id="job-hr-mgr",
        candidate_name="John Doe",
        resume_filename="john.pdf",
        resume_text="recruiter",
        ats_score=80,
        fit_reason="good"
    )

    # Delete job and verify cascading delete of applications
    ds.delete_job("job-python-ai")
    
    jobs = ds.load_jobs()
    assert len(jobs) == 1
    assert jobs[0]["id"] == "job-hr-mgr"
    
    apps = ds.load_applications()
    # Should only contain the John Doe application, the others are deleted
    assert len(apps) == 1
    assert apps[0]["candidate_name"] == "John Doe"

def test_save_and_load_applications(mock_db):
    app = ds.save_application(
        job_id="job-hr-mgr",
        candidate_name="John Doe",
        resume_filename="john.pdf",
        resume_text="Experienced HR recruiter",
        ats_score=85,
        fit_reason="Good match"
    )
    
    assert app["candidate_name"] == "John Doe"
    assert app["ats_score"] == 85
    
    apps = ds.load_applications()
    assert len(apps) == 3 # 2 seeded + 1 new
    assert any(a["id"] == app["id"] for a in apps)

def test_get_applications_for_job(mock_db):
    apps = ds.get_applications_for_job("job-python-ai")
    assert len(apps) == 2
    
    apps_hr = ds.get_applications_for_job("job-hr-mgr")
    assert len(apps_hr) == 0

def test_has_applied(mock_db):
    assert ds.has_applied("job-python-ai", "Alice Chen") is True
    assert ds.has_applied("job-python-ai", "alice chen") is True # Case insensitivity check
    assert ds.has_applied("job-python-ai", "Charlie Brown") is False

def test_get_top_candidates(mock_db):
    # Alice has 92, Bob has 35
    top_cand = ds.get_top_candidates("job-python-ai", top_n=1)
    assert len(top_cand) == 1
    assert top_cand[0]["candidate_name"] == "Alice Chen"
