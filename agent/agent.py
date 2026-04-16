"""DataLens Agent with ReAct Architecture

A complete NL2SQL agent with:
- ReAct (Reasoning + Acting) loop
- Session memory
- Self-correction on errors
- Multi-provider support
"""

import json
import logging
from typing import Optional, List, Dict, Any

from agent.config import ModelConfig, DatabaseConfig, ConfigManager
from agent.mcp_client import MCPClientWrapper
from agent.security import SQLValidator, InjectionDetector
from agent.memory import SessionMemory, QueryRecord
from agent.core import ReActEngine, ToolExecutor, AgentResult
from agent.reflection import ErrorAnalyzer, SelfCorrector

logger = logging.getLogger(__name__)


class NL2SQLAgent:
    """
    Complete NL2SQL Agent with ReAct architecture

    Features:
    - ReAct loop: Thought → Action → Observation
    - Session memory: Tracks queries and results
    - Self-correction: Analyzes errors and retries
    - Multi-provider: Anthropic, OpenAI, Qwen, Zhipu
    """

    def __init__(
        self,
        model_config: ModelConfig,
        db_config: DatabaseConfig,
        config_manager: Optional[ConfigManager] = None,
        use_mcp: bool = True,
        session_memory: Optional[SessionMemory] = None
    ):
        self.model_config = model_config
        self.db_config = db_config
        self.db_name = db_config.name
        self.use_mcp = use_mcp

        # Security components
        self.sql_validator = SQLValidator()
        self.injection_detector = InjectionDetector()

        # MCP Client
        if self.use_mcp and config_manager:
            self.mcp_client = MCPClientWrapper(config_manager)
            self.db_manager = None
        else:
            from agent.database import DatabaseManager
            self.db_manager = DatabaseManager(db_config)
            self.mcp_client = None

        # Memory (can be shared across queries)
        self.memory = session_memory or SessionMemory()

        # ReAct Engine
        self.react_engine = ReActEngine(model_config, model_config.provider)

        # Reflection components
        self.error_analyzer = ErrorAnalyzer()
        self.self_corrector = SelfCorrector(model_config, model_config.provider)

        # Tool Executor
        self.tool_executor = None  # Initialized when needed

        # Schema cache
        self._schema = None

        self._init_client()

    @property
    def schema(self):
        """Get schema (returns cached schema)"""
        return self._schema or ""

    async def _ensure_schema_loaded(self):
        """Ensure schema is loaded"""
        if self._schema is None:
            if self.use_mcp:
                self._schema = await self.mcp_client.get_schema(self.db_name)
            else:
                self._schema = self.db_manager.get_schema()

            # Update memory
            self.memory.set_schema(self._schema)

    def _init_client(self):
        """Initialize LLM client based on provider"""
        provider = self.model_config.provider.lower()

        if provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.model_config.api_key)
        elif provider == "qwen":
            from dashscope import Generation
            self.generation = Generation
        elif provider == "zhipu":
            from zhipuai import ZhipuAI
            self.client = ZhipuAI(api_key=self.model_config.api_key)
        elif provider == "openai-compatible":
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.model_config.api_key,
                base_url=self.model_config.base_url
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _validate_sql(self, sql: str) -> str:
        """Validate SQL and return safe SQL"""
        if not self.injection_detector.is_safe(sql):
            risk_level = self.injection_detector.get_risk_level(sql)
            raise ValueError(f"SQL injection detected (risk: {risk_level}). Query rejected.")

        is_valid, errors, warnings = self.sql_validator.validate(sql)

        if not is_valid:
            raise ValueError(f"SQL validation failed: {'; '.join(errors)}")

        if warnings:
            for warning in warnings:
                logger.warning(f"SQL warning: {warning}")

        return self.sql_validator.get_safe_limit(sql)

    async def query(self, user_query: str) -> str:
        """
        Process user query using ReAct loop

        Args:
            user_query: User's natural language question or SQL query

        Returns:
            Natural language answer
        """
        # Check if user input is a direct SQL query
        if self._is_sql_query(user_query):
            sql = self._extract_direct_sql(user_query)
            if sql:
                return await self._handle_direct_sql(user_query, sql)

        # Ensure schema is loaded
        await self._ensure_schema_loaded()

        # Initialize tool executor
        if self.tool_executor is None:
            if self.use_mcp:
                self.tool_executor = ToolExecutor(self.mcp_client, self.db_name)
            else:
                # Create a simple wrapper for db_manager
                self.tool_executor = self._create_db_manager_executor()

        # Get memory context
        memory_context = self.memory.get_context_for_query()

        # Run ReAct loop
        result = await self.react_engine.run(
            user_query=user_query,
            tool_executor=self.tool_executor,
            schema=self._schema,
            memory_context=memory_context,
            max_iterations=10
        )

        # Record in memory
        record = QueryRecord(
            timestamp=result.steps[-1].timestamp if result.steps else None,
            natural_query=user_query,
            sql=result.sql,
            success=result.success,
            result_count=0,  # Could extract from steps
            error=result.error,
            answer=result.answer
        )
        if record.timestamp is None:
            from datetime import datetime
            record.timestamp = datetime.now()
        self.memory.add_query(record)

        return result.answer

    async def _handle_direct_sql(self, user_query: str, sql: str) -> str:
        """
        Handle direct SQL execution with self-correction

        Args:
            user_query: Original user query
            sql: Extracted SQL

        Returns:
            Natural language answer
        """
        logger.info(f"Detected direct SQL query: {sql}")

        # Execute SQL with correction
        result = await self._execute_direct_sql(sql)

        # Build answer
        if result["success"]:
            data = result["data"]

            # Check if SQL was corrected
            if result.get("original_sql"):
                answer = f"✅ 您的SQL有误，已自动修正并执行。\n\n"
                answer += f"**原始SQL：**\n```sql\n{result['original_sql']}\n```\n\n"
                answer += f"**修正后SQL：**\n```sql\n{result['sql']}\n```\n\n"
            else:
                answer = f"✅ SQL执行成功。\n\n```sql\n{result['sql']}\n```\n\n"

            # Format results
            if isinstance(data, list):
                if len(data) == 0:
                    answer += "查询结果为空（0条记录）。"
                elif len(data) <= 20:
                    answer += f"**查询结果（{len(data)}条记录）：**\n"
                    answer += self._format_data_table(data)
                else:
                    answer += f"**查询结果（共{len(data)}条记录，显示前20条）：**\n"
                    answer += self._format_data_table(data[:20])
            else:
                answer += f"结果：{data}"

            # Record in memory
            record = QueryRecord(
                natural_query=user_query,
                sql=result["sql"],
                success=True,
                result_count=len(data) if isinstance(data, list) else 0,
                answer=answer
            )
            self.memory.add_query(record)

            return answer

        else:
            # Execution failed
            error = result["error"]
            history = result.get("correction_history", [])

            answer = f"❌ SQL执行失败。\n\n"
            answer += f"**执行的SQL：**\n```sql\n{result['sql']}\n```\n\n"
            answer += f"**错误信息：**\n{error}\n\n"

            # Show correction attempts if any
            if len(history) > 1:
                answer += "**尝试的修正：**\n"
                for h in history:
                    answer += f"- 第{h['attempt']}次: {h.get('corrected_sql', h['sql'])}\n"
                    answer += f"  错误: {h['error']}\n"

            # Provide suggestion
            answer += "\n**建议：**\n"
            answer += "请检查SQL语法是否正确，表名和字段名是否存在。"
            answer += "您可以输入自然语言问题，我会帮您生成正确的SQL。"

            # Record in memory
            record = QueryRecord(
                natural_query=user_query,
                sql=result["sql"],
                success=False,
                error=error,
                answer=answer
            )
            self.memory.add_query(record)

            return answer

    def _format_data_table(self, data: List[Dict]) -> str:
        """Format data as a readable table"""
        if not data:
            return ""

        import json
        # Use JSON format for clean display
        return f"```json\n{json.dumps(data, ensure_ascii=False, default=str, indent=2)}\n```"

    def _create_db_manager_executor(self) -> ToolExecutor:
        """Create tool executor wrapper for db_manager"""
        class DBManagerWrapper:
            def __init__(self, db_manager, sql_validator):
                self.db_manager = db_manager
                self.sql_validator = sql_validator

            async def execute_query(self, db_name, sql):
                # Validate
                sql = self.sql_validator.get_safe_limit(sql)
                return self.db_manager.execute_query(sql)

            async def get_schema(self, db_name):
                return self.db_manager.get_schema()

            async def get_table_sample(self, db_name, table_name, limit=5):
                sql = f"SELECT * FROM {table_name} LIMIT {limit}"
                return self.db_manager.execute_query(sql)

            async def refresh_schema(self, db_name):
                return {"success": True, "message": "Schema refreshed"}

            async def test_connection(self, db_name):
                return {"success": True, "message": "Connection OK"}

        wrapper = DBManagerWrapper(self.db_manager, self.sql_validator)
        return ToolExecutor(wrapper, self.db_name)

    async def close(self):
        """Clean up resources"""
        if self.use_mcp and self.mcp_client:
            await self.mcp_client.close()
        elif self.db_manager:
            self.db_manager.disconnect()

    # Legacy methods for backward compatibility
    async def _call_anthropic(self, user_query: str) -> str:
        """Legacy Anthropic call - use query() instead"""
        return await self.query(user_query)

    async def _call_openai_compatible(self, user_query: str) -> str:
        """Legacy OpenAI call - use query() instead"""
        return await self.query(user_query)

    def _call_qwen(self, user_query: str) -> str:
        """Legacy Qwen call - simplified version"""
        # Simple implementation without ReAct
        from agent.prompts import QWEN_SYSTEM_PROMPT
        prompt = QWEN_SYSTEM_PROMPT.format(
            schema=self.schema,
            user_query=user_query
        )
        try:
            response = self.generation.call(
                model="qwen-turbo",
                messages=[{"role": "user", "content": prompt}],
                api_key=self.model_config.api_key,
            )
            return response.output.text
        except Exception as e:
            return f"Error calling Qwen: {e}"

    def _call_zhipu(self, user_query: str) -> str:
        """Legacy Zhipu call - simplified version"""
        from agent.prompts import ZIPMU_SYSTEM_PROMPT
        messages = [
            {
                "role": "user",
                "content": ZIPMU_SYSTEM_PROMPT.format(
                    schema=self.schema,
                    user_query=user_query
                ),
            }
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model_config.model_name,
                messages=messages,
                temperature=self.model_config.temperature,
                max_tokens=self.model_config.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling Zhipu: {e}"

    def _extract_sql(self, text: str) -> Optional[str]:
        """Extract SQL from text"""
        import re

        # Try code block
        code_block_pattern = r"```sql\s*(.*?)\s*```"
        match = re.search(code_block_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try generic code block
        code_block_pattern = r"```\s*(.*?)\s*```"
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            sql = match.group(1).strip()
            if sql.upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                return sql

        # Try direct SELECT
        select_pattern = r"(SELECT\s+.*?;?)\s*$"
        match = re.search(select_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip().rstrip(';')

        return None

    def _is_sql_query(self, user_input: str) -> bool:
        """
        Check if user input is a valid SQL query

        Args:
            user_input: User's input string

        Returns:
            True if the input appears to be a SQL query
        """
        import re

        # Clean the input
        cleaned = user_input.strip().strip('`').strip()

        # SQL keywords that start a query
        sql_start_patterns = [
            r'^\s*SELECT\s+',           # SELECT statement
            r'^\s*SHOW\s+',             # SHOW statement
            r'^\s*DESCRIBE\s+',         # DESCRIBE statement
            r'^\s*DESC\s+',             # DESC shorthand
            r'^\s*EXPLAIN\s+',          # EXPLAIN statement
        ]

        # Check if starts with SQL keyword
        for pattern in sql_start_patterns:
            if re.match(pattern, cleaned, re.IGNORECASE):
                return True

        # Check for SQL in code block
        if '```sql' in user_input.lower():
            return True

        return False

    def _extract_direct_sql(self, user_input: str) -> Optional[str]:
        """
        Extract SQL from direct SQL input

        Args:
            user_input: User's input string

        Returns:
            Clean SQL string or None
        """
        import re

        # Clean the input
        cleaned = user_input.strip()

        # Remove code block markers if present
        if '```sql' in cleaned.lower():
            match = re.search(r'```sql\s*(.*?)\s*```', cleaned, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip().rstrip(';')
        elif '```' in cleaned:
            match = re.search(r'```\s*(.*?)\s*```', cleaned, re.DOTALL)
            if match:
                return match.group(1).strip().rstrip(';')

        # Direct SQL - clean it
        cleaned = cleaned.strip('`').strip().rstrip(';')

        # Validate it's actually SQL
        if re.match(r'^\s*(SELECT|SHOW|DESCRIBE|DESC|EXPLAIN)\s+', cleaned, re.IGNORECASE):
            return cleaned

        return None

    async def _execute_direct_sql(
        self,
        sql: str,
        max_correction_attempts: int = 2
    ) -> Dict[str, Any]:
        """
        Execute SQL directly with self-correction on errors

        Args:
            sql: SQL query to execute
            max_correction_attempts: Maximum correction attempts

        Returns:
            Result dict with success, data/error, and correction info
        """
        await self._ensure_schema_loaded()

        current_sql = sql
        attempts = 0
        correction_history = []

        while attempts <= max_correction_attempts:
            attempts += 1

            # Validate SQL security
            try:
                safe_sql = self._validate_sql(current_sql)
            except ValueError as e:
                return {
                    "success": False,
                    "error": str(e),
                    "sql": current_sql,
                    "correction_history": correction_history
                }

            # Execute the query
            try:
                if self.use_mcp:
                    result = await self.mcp_client.execute_query(self.db_name, safe_sql)
                else:
                    result = self.db_manager.execute_query(safe_sql)

                # Success!
                return {
                    "success": True,
                    "data": result,
                    "sql": current_sql,
                    "original_sql": sql if current_sql != sql else None,
                    "correction_history": correction_history,
                    "attempts": attempts
                }

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"SQL execution failed (attempt {attempts}): {error_msg}")

                # Record this attempt
                correction_history.append({
                    "attempt": attempts,
                    "sql": current_sql,
                    "error": error_msg
                })

                # Try to correct the SQL
                if attempts <= max_correction_attempts:
                    corrected = await self.self_corrector.correct_sql(
                        sql=current_sql,
                        error=error_msg,
                        schema=self._schema or ""
                    )

                    if corrected and corrected != current_sql:
                        logger.info(f"SQL corrected: {corrected}")
                        correction_history[-1]["corrected_sql"] = corrected
                        current_sql = corrected
                    else:
                        # Cannot correct further
                        break
                else:
                    break

        # All attempts failed
        return {
            "success": False,
            "error": correction_history[-1]["error"] if correction_history else "Unknown error",
            "sql": current_sql,
            "original_sql": sql if current_sql != sql else None,
            "correction_history": correction_history,
            "attempts": attempts
        }
