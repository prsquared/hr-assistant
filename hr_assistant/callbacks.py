import logging
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Dict, List

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from hr_assistant.config import LOG_LEVEL

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("HR_Agent_Trace")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# Setup rotating file handler if not already present
if not logger.handlers:
    handler = TimedRotatingFileHandler(
        filename="logs/agent_trace.log",
        when="H",
        interval=1,
        backupCount=24,  # Keep up to 24 hours of logs
    )
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class LoggingCallbackHandler(BaseCallbackHandler):
    """A custom callback handler that logs LangChain execution flow and metrics."""

    def __init__(self):
        super().__init__()
        self.active_chains = set()
        self.ignore_chains = {
            "RunnableSequence", "RunnableParallel", "RunnableAssign", 
            "RunnableBranch", "RunnableMap", "ChatPromptTemplate", 
            "PromptTemplate", "StrOutputParser", "Chain"
        }

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        # invocation_params sometimes holds model_name
        model_name = kwargs.get("invocation_params", {}).get("model", "Unknown")
        if model_name == "Unknown":
            model_name = kwargs.get("invocation_params", {}).get("model_name", "Unknown")
            
        logger.info(f"[LLM Start] Model: {model_name}")
        logger.debug(f"[LLM Prompts]: {prompts}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        token_usage = {}
        if response.llm_output and "token_usage" in response.llm_output:
            token_usage = response.llm_output["token_usage"]
        elif response.generations:
            try:
                # ChatModels often put it in the first message's response_metadata
                message = response.generations[0][0].message
                token_usage = message.response_metadata.get("token_usage", {})
            except AttributeError:
                pass
                
        logger.info(f"[LLM End] Token Usage: {token_usage}")
        if response.generations:
            for i, generation_list in enumerate(response.generations):
                for j, gen in enumerate(generation_list):
                    logger.debug(f"[LLM Generation {i}.{j}]: {gen.text}")

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        chain_name = serialized.get("name", "Chain") if serialized else "Chain"
        if "run_name" in kwargs and kwargs["run_name"]:
            chain_name = kwargs["run_name"]
            
        if chain_name not in self.ignore_chains:
            run_id = kwargs.get("run_id")
            if run_id:
                self.active_chains.add(run_id)
            logger.info(f"[Chain Start] {chain_name}")
            logger.debug(f"[Chain Inputs]: {inputs}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends running."""
        run_id = kwargs.get("run_id")
        if run_id in self.active_chains:
            logger.info("[Chain End]")
            logger.debug(f"[Chain Outputs]: {outputs}")
            self.active_chains.remove(run_id)

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""
        tool_name = serialized.get("name", "Tool") if serialized else "Tool"
        logger.info(f"[Tool Start] {tool_name}")
        logger.debug(f"[Tool Input]: {input_str}")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""
        logger.info("[Tool End]")
        logger.debug(f"[Tool Output]: {output}")
