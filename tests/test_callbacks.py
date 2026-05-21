import pytest
from unittest.mock import MagicMock
from langchain_core.outputs import LLMResult
from langchain_core.messages import AIMessage
import hr_assistant.callbacks as cb

@pytest.fixture
def mock_logger(mocker):
    return mocker.patch("hr_assistant.callbacks.logger")

def test_on_llm_start(mock_logger):
    handler = cb.LoggingCallbackHandler()
    handler.on_llm_start(
        serialized={}, 
        prompts=["Hello!"], 
        invocation_params={"model": "gpt-4o"}
    )
    mock_logger.info.assert_any_call("[LLM Start] Model: gpt-4o")

def test_on_llm_end_with_token_usage(mock_logger):
    handler = cb.LoggingCallbackHandler()
    
    # Test when token_usage is in llm_output
    result_with_output = LLMResult(
        generations=[],
        llm_output={"token_usage": {"total_tokens": 100}}
    )
    handler.on_llm_end(result_with_output)
    mock_logger.info.assert_any_call("[LLM End] Token Usage: {'total_tokens': 100}")

    # Test when token_usage is in AIMessage response_metadata (streaming)
    from langchain_core.outputs import ChatGeneration
    message = AIMessage(content="Hello", response_metadata={"token_usage": {"total_tokens": 200}})
    generation = ChatGeneration(message=message, text="Hello")
    result_with_metadata = LLMResult(
        generations=[[generation]]
    )
    handler.on_llm_end(result_with_metadata)
    mock_logger.info.assert_any_call("[LLM End] Token Usage: {'total_tokens': 200}")

def test_on_chain_filtering(mock_logger):
    handler = cb.LoggingCallbackHandler()
    
    # Ignore sequence chain
    handler.on_chain_start(
        serialized={"name": "RunnableSequence"},
        inputs={},
        run_id="run-1"
    )
    mock_logger.info.assert_not_called()
    
    # Do not ignore meaningful chain
    handler.on_chain_start(
        serialized={"name": "MyCustomAgent"},
        inputs={},
        run_id="run-2"
    )
    mock_logger.info.assert_called_with("[Chain Start] MyCustomAgent")
    assert "run-2" in handler.active_chains

    # Verify on_chain_end only logs active chain
    handler.on_chain_end(outputs={}, run_id="run-1") # ignored
    # mock_logger.info should not have been called with [Chain End] yet
    # check that we only have the "[Chain Start] MyCustomAgent" call
    assert mock_logger.info.call_count == 1

    handler.on_chain_end(outputs={}, run_id="run-2") # custom
    mock_logger.info.assert_any_call("[Chain End]")

def test_on_tool(mock_logger):
    handler = cb.LoggingCallbackHandler()
    handler.on_tool_start(serialized={"name": "my_tool"}, input_str="my_input")
    mock_logger.info.assert_any_call("[Tool Start] my_tool")
    
    handler.on_tool_end(output="my_output")
    mock_logger.info.assert_any_call("[Tool End]")
