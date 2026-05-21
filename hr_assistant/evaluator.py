"""
evaluator.py — LLM-powered ATS (Applicant Tracking System) resume scorer.

Exposes a single public function:
  evaluate_resume_for_job(resume_text, jd_text) -> dict
    Returns {"ats_score": int, "fit_reason": str}
"""

import json

from langchain_openai import ChatOpenAI

from hr_assistant.config import BASE_LLM_MODEL


def evaluate_resume_for_job(resume_text: str, jd_text: str) -> dict:
    """Evaluates a resume against a job description using an LLM.

    Args:
        resume_text: Plain-text content of the candidate's resume.
        jd_text:     The job description requirements.

    Returns:
        dict with keys:
            "ats_score"  (int, 0–100) — compatibility score
            "fit_reason" (str)        — 2–3 sentence professional explanation
    """
    llm = ChatOpenAI(
        model=BASE_LLM_MODEL,
        temperature=0,
        stream_usage=True,
        model_kwargs={"response_format": {"type": "json_object"}},
    )

    prompt = f"""\
You are an expert AI recruiting assistant and ATS optimizer.
Analyze the candidate's resume against the provided job description.

Return a JSON object with exactly these two fields:
  "ats_score"  : integer 0–100 representing the candidate-job fit percentage
  "fit_reason" : 2–3 sentence professional explanation of the match or mismatch,
                 citing specific skills or experience gaps

Job Description:
{jd_text}

Candidate Resume:
{resume_text}

Respond with valid JSON only.
"""

    try:
        response = llm.invoke(prompt, config={"run_name": "ATS_Resume_Evaluator"})
        from langchain_core.tracers.langchain import wait_for_all_tracers
        wait_for_all_tracers()

        result = json.loads(response.content)
        ats_score = max(0, min(100, int(result.get("ats_score", 50))))
        fit_reason = str(result.get("fit_reason", "No detailed evaluation provided."))
        return {"ats_score": ats_score, "fit_reason": fit_reason}

    except Exception as e:
        print(f"[evaluator] Error scoring resume: {e}")
        return {"ats_score": 0, "fit_reason": f"Evaluation error: {e}"}
