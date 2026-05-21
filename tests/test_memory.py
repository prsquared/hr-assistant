import pytest
import streamlit as st
from unittest.mock import MagicMock
import hr_assistant.memory as mem

def test_get_agent_memory(mocker):
    # Mock st.session_state as a dictionary
    mocker.patch.object(st, "session_state", {})
    
    mock_llm = MagicMock()
    
    # Mock ConversationSummaryBufferMemory class
    mock_memory_class = mocker.patch("hr_assistant.memory.ConversationSummaryBufferMemory")
    mock_memory_instance = MagicMock()
    mock_memory_class.return_value = mock_memory_instance
    
    # Should create and return memory
    memory = mem.get_agent_memory(mock_llm, "test_agent_memory")
    assert "test_agent_memory" in st.session_state
    assert st.session_state["test_agent_memory"] is mock_memory_instance
    
    # Re-invocation should return the cached instance
    memory2 = mem.get_agent_memory(mock_llm, "test_agent_memory")
    assert memory2 is mock_memory_instance
    
    # Verify constructor parameters
    mock_memory_class.assert_called_once_with(
        llm=mock_llm,
        max_token_limit=1000,
        memory_key="chat_history",
        return_messages=True,
        output_key="output",
    )

def test_get_rag_memory(mocker):
    # Mock st.session_state as a dictionary
    mocker.patch.object(st, "session_state", {})
    
    # Mock ConversationBufferWindowMemory class
    mock_memory_class = mocker.patch("hr_assistant.memory.ConversationBufferWindowMemory")
    mock_memory_instance = MagicMock()
    mock_memory_class.return_value = mock_memory_instance
    
    # Should create and return memory
    memory = mem.get_rag_memory("test_rag_memory")
    assert "test_rag_memory" in st.session_state
    assert st.session_state["test_rag_memory"] is mock_memory_instance
    
    # Re-invocation should return the cached instance
    memory2 = mem.get_rag_memory("test_rag_memory")
    assert memory2 is mock_memory_instance
    
    # Verify constructor parameters
    mock_memory_class.assert_called_once_with(
        k=5,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )
