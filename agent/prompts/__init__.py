"""Prompt templates for DataLens Agent"""

from agent.prompts.system_prompts import (
    ANTHROPIC_SYSTEM_PROMPT,
    OPENAI_SYSTEM_PROMPT,
    QWEN_SYSTEM_PROMPT,
    ZIPMU_SYSTEM_PROMPT,
)
from agent.prompts.sql_prompts import (
    SQL_GENERATION_PROMPT,
    SQL_RESULT_INTERPRET_PROMPT,
)

__all__ = [
    "ANTHROPIC_SYSTEM_PROMPT",
    "OPENAI_SYSTEM_PROMPT",
    "QWEN_SYSTEM_PROMPT",
    "ZIPMU_SYSTEM_PROMPT",
    "SQL_GENERATION_PROMPT",
    "SQL_RESULT_INTERPRET_PROMPT",
]