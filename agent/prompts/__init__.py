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
from agent.prompts.react_prompts import (
    REACT_SYSTEM_PROMPT,
    REACT_USER_TEMPLATE,
    REACT_OBSERVATION_TEMPLATE,
    REACT_ERROR_TEMPLATE,
)
from agent.prompts.reflection_prompts import (
    REFLECTION_PROMPT,
    ERROR_CLASSIFICATION_PROMPT,
    CORRECTION_PROMPT,
)

__all__ = [
    # System prompts
    "ANTHROPIC_SYSTEM_PROMPT",
    "OPENAI_SYSTEM_PROMPT",
    "QWEN_SYSTEM_PROMPT",
    "ZIPMU_SYSTEM_PROMPT",
    # SQL prompts
    "SQL_GENERATION_PROMPT",
    "SQL_RESULT_INTERPRET_PROMPT",
    # ReAct prompts
    "REACT_SYSTEM_PROMPT",
    "REACT_USER_TEMPLATE",
    "REACT_OBSERVATION_TEMPLATE",
    "REACT_ERROR_TEMPLATE",
    # Reflection prompts
    "REFLECTION_PROMPT",
    "ERROR_CLASSIFICATION_PROMPT",
    "CORRECTION_PROMPT",
]