import pytest
from unittest.mock import MagicMock
import json
import hr_assistant.evaluator as ev

def test_evaluate_resume_for_job_success(mocker):
    # Mock LLM and its response
    mock_llm_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.content = json.dumps({
        "ats_score": 85,
        "fit_reason": "Good match with Python skills."
    })
    mock_llm_instance.invoke.return_value = mock_response
    
    # Patch ChatOpenAI constructor to return our mock instance
    mocker.patch("hr_assistant.evaluator.ChatOpenAI", return_value=mock_llm_instance)
    
    # Run evaluation
    result = ev.evaluate_resume_for_job("Python developer", "Need Python dev")
    
    # Asserts
    assert result["ats_score"] == 85
    assert result["fit_reason"] == "Good match with Python skills."
    mock_llm_instance.invoke.assert_called_once()

def test_evaluate_resume_for_job_invalid_json(mocker):
    mock_llm_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "not a valid json"
    mock_llm_instance.invoke.return_value = mock_response
    
    mocker.patch("hr_assistant.evaluator.ChatOpenAI", return_value=mock_llm_instance)
    
    result = ev.evaluate_resume_for_job("Python developer", "Need Python dev")
    assert result["ats_score"] == 0
    assert "Evaluation error" in result["fit_reason"]

def test_evaluate_resume_for_job_missing_fields(mocker):
    mock_llm_instance = MagicMock()
    mock_response = MagicMock()
    # Missing ats_score and fit_reason
    mock_response.content = json.dumps({})
    mock_llm_instance.invoke.return_value = mock_response
    
    mocker.patch("hr_assistant.evaluator.ChatOpenAI", return_value=mock_llm_instance)
    
    result = ev.evaluate_resume_for_job("Python developer", "Need Python dev")
    assert result["ats_score"] == 50 # fallback
    assert result["fit_reason"] == "No detailed evaluation provided." # fallback
