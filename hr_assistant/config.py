import os

SUPERVISOR_LLM_MODEL = os.getenv("SUPERVISOR_LLM_MODEL", "gpt-4o")
BASE_LLM_MODEL = os.getenv("BASE_LLM_MODEL", "gpt-4o-mini")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
