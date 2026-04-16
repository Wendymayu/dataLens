"""ReAct Engine - Thought → Action → Observation loop"""

import re
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

from agent.core.tool_executor import ToolExecutor
from agent.prompts.react_prompts import (
    REACT_SYSTEM_PROMPT,
    REACT_USER_TEMPLATE,
    REACT_OBSERVATION_TEMPLATE,
)

logger = logging.getLogger(__name__)


@dataclass
class ReActStep:
    """Single step in ReAct loop"""
    iteration: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    is_final: bool = False
    error: Optional[str] = None


@dataclass
class ReActResult:
    """Result of ReAct execution"""
    success: bool
    answer: str
    sql: Optional[str] = None
    steps: List[ReActStep] = field(default_factory=list)
    total_iterations: int = 0
    error: Optional[str] = None


class ReActEngine:
    """
    ReAct (Reasoning + Acting) Engine

    Implements the Thought → Action → Observation loop for
    systematic problem solving.
    """

    def __init__(self, model_config: Any, provider: str = "openai-compatible"):
        """
        Initialize ReAct engine

        Args:
            model_config: Model configuration
            provider: LLM provider type
        """
        self.model_config = model_config
        self.provider = provider.lower()
        self._init_client()

    def _init_client(self):
        """Initialize LLM client based on provider"""
        if self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.model_config.api_key)
        elif self.provider in ("openai-compatible", "qwen", "zhipu"):
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.model_config.api_key,
                base_url=getattr(self.model_config, 'base_url', None)
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def run(
        self,
        user_query: str,
        tool_executor: ToolExecutor,
        schema: str,
        memory_context: str = "",
        max_iterations: int = 10
    ) -> ReActResult:
        """
        Run ReAct loop to answer user query

        Args:
            user_query: User's natural language question
            tool_executor: Tool executor for actions
            schema: Database schema
            memory_context: Context from session memory
            max_iterations: Maximum iterations before stopping

        Returns:
            ReActResult with answer and execution trace
        """
        steps: List[ReActStep] = []
        messages = self._build_initial_messages(user_query, schema, memory_context)
        tools = tool_executor.get_tool_definitions()

        current_sql = None

        for i in range(max_iterations):
            logger.info(f"ReAct iteration {i + 1}/{max_iterations}")

            # Get LLM response
            response = await self._call_llm(messages, tools)

            # Parse response
            step = self._parse_response(response, i)
            steps.append(step)

            # Check if done
            if step.is_final:
                logger.info(f"ReAct completed at iteration {i + 1}")
                return ReActResult(
                    success=True,
                    answer=step.thought,
                    sql=current_sql,
                    steps=steps,
                    total_iterations=i + 1
                )

            # Execute action if present
            if step.action and step.action_input:
                # Track SQL
                if step.action == "execute_query" and "sql" in step.action_input:
                    current_sql = step.action_input["sql"]

                # Execute tool
                result = await tool_executor.execute(step.action, step.action_input)

                # Build observation
                if result["success"]:
                    observation = self._format_observation(result["data"])
                else:
                    observation = f"Error: {result['error']}\nSuggestion: {result.get('suggestion', '')}"

                step.observation = observation

                # Add to messages for next iteration
                messages.append({
                    "role": "assistant",
                    "content": f"Thought: {step.thought}\nAction: {step.action}\nAction Input: {json.dumps(step.action_input, ensure_ascii=False)}"
                })
                messages.append({
                    "role": "user",
                    "content": REACT_OBSERVATION_TEMPLATE.format(observation=observation)
                })
            else:
                # No action but not final - force continue
                messages.append({
                    "role": "user",
                    "content": "请继续思考并采取行动，或使用 'Final Answer:' 给出答案。"
                })

        # Max iterations reached
        logger.warning(f"ReAct reached max iterations ({max_iterations})")
        return ReActResult(
            success=False,
            answer="抱歉，处理您的请求时超出了最大迭代次数。请尝试简化问题。",
            sql=current_sql,
            steps=steps,
            total_iterations=max_iterations,
            error="max_iterations_reached"
        )

    def _build_initial_messages(
        self,
        user_query: str,
        schema: str,
        memory_context: str
    ) -> List[Dict[str, str]]:
        """Build initial messages for LLM"""
        tools_desc = self._format_tools_description()
        system_prompt = REACT_SYSTEM_PROMPT.format(tools_description=tools_desc)

        user_content = REACT_USER_TEMPLATE.format(
            schema=schema,
            memory_context=memory_context,
            user_query=user_query
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

    def _format_tools_description(self) -> str:
        """Format tools for prompt"""
        return """
1. execute_query(sql) - 执行 SQL 查询
   - 参数: sql (string) - SQL 查询语句
   - 用途: 查询数据库数据

2. get_schema() - 获取数据库结构
   - 用途: 查看所有表和字段

3. get_table_sample(table_name, limit) - 获取表样本
   - 参数: table_name (string), limit (integer, 可选)
   - 用途: 查看表的数据样例
"""

    def _format_observation(self, data: Any) -> str:
        """Format observation data for prompt"""
        if isinstance(data, list):
            if len(data) == 0:
                return "查询结果为空（0条记录）"
            elif len(data) <= 10:
                return f"查询结果（{len(data)}条记录）：\n{json.dumps(data, ensure_ascii=False, default=str)}"
            else:
                return f"查询结果（共{len(data)}条记录，显示前10条）：\n{json.dumps(data[:10], ensure_ascii=False, default=str)}"
        elif isinstance(data, str):
            return data
        else:
            return json.dumps(data, ensure_ascii=False, default=str)

    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]]
    ) -> str:
        """Call LLM and get response"""

        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model_config.model_name,
                max_tokens=self.model_config.max_tokens,
                messages=messages
            )
            return response.content[0].text
        else:
            # OpenAI-compatible
            response = self.client.chat.completions.create(
                model=self.model_config.model_name,
                messages=messages,
                temperature=getattr(self.model_config, 'temperature', 0.7),
                max_tokens=self.model_config.max_tokens
            )
            return response.choices[0].message.content

    def _parse_response(self, response: str, iteration: int) -> ReActStep:
        """
        Parse LLM response into ReAct step

        Response formats:
        - Thought: ...\nAction: xxx\nAction Input: {...}
        - Final Answer: ...
        """
        response = response.strip()

        # Check for Final Answer
        final_match = re.search(
            r"Final Answer:\s*(.+)",
            response,
            re.IGNORECASE | re.DOTALL
        )
        if final_match:
            return ReActStep(
                iteration=iteration,
                thought=final_match.group(1).strip(),
                is_final=True
            )

        # Parse Thought
        thought_match = re.search(
            r"Thought:\s*(.+?)(?=\nAction:|$)",
            response,
            re.IGNORECASE | re.DOTALL
        )
        thought = thought_match.group(1).strip() if thought_match else response

        # Parse Action
        action_match = re.search(
            r"Action:\s*(\w+)",
            response,
            re.IGNORECASE
        )
        action = action_match.group(1) if action_match else None

        # Parse Action Input
        action_input = None
        input_match = re.search(
            r"Action Input:\s*(\{.+?\})",
            response,
            re.IGNORECASE | re.DOTALL
        )
        if input_match:
            try:
                action_input = json.loads(input_match.group(1))
            except json.JSONDecodeError:
                # Try to extract key-value pairs
                action_input = {"raw": input_match.group(1)}

        return ReActStep(
            iteration=iteration,
            thought=thought,
            action=action,
            action_input=action_input,
            is_final=False
        )
