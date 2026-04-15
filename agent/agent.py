"""DataLens Agent supporting multiple model providers"""
import json
from typing import Optional
from agent.database import DatabaseManager
from agent.config import ModelConfig, DatabaseConfig, ConfigManager
from agent.mcp_client import MCPClientWrapper


class NL2SQLAgent:
    """DataLens Agent that converts natural language to SQL queries"""

    def __init__(self, model_config: ModelConfig, db_config: DatabaseConfig, config_manager: Optional[ConfigManager] = None, use_mcp: bool = True):
        self.model_config = model_config
        self.use_mcp = use_mcp
        self.db_name = db_config.name
        self._schema = None

        if self.use_mcp and config_manager:
            # Use MCP Client
            self.mcp_client = MCPClientWrapper(config_manager)
            self.db_manager = None
        else:
            # Use legacy DatabaseManager
            self.db_manager = DatabaseManager(db_config)
            self.mcp_client = None
            self._schema = self.db_manager.get_schema()

        self._init_client()

    @property
    def schema(self):
        """Get schema (returns cached schema)"""
        return self._schema or ""

    async def _ensure_schema_loaded(self):
        """Ensure schema is loaded (async)"""
        if self._schema is None and self.use_mcp:
            self._schema = await self.mcp_client.get_schema(self.db_name)

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
            # 支持自定义base_url的OpenAI兼容API
            self.client = OpenAI(
                api_key=self.model_config.api_key,
                base_url=self.model_config.base_url
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _call_anthropic(self, user_query: str) -> str:
        """Call Anthropic Claude API"""
        # Ensure schema is loaded
        await self._ensure_schema_loaded()

        tools = [
            {
                "name": "execute_query",
                "description": "Execute SQL query and return results",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "SQL query to execute",
                        }
                    },
                    "required": ["sql"],
                },
            }
        ]

        messages = [
            {
                "role": "user",
                "content": f"""You are a SQL expert. Convert the user's natural language query to SQL.

Database Schema:
{self.schema}

User Query: {user_query}

Guidelines:
1. First generate the SQL query based on the schema
2. Use the execute_query tool to run it
3. Analyze the results and provide a natural language response""",
            }
        ]

        # Agent loop
        for _ in range(10):  # Max 10 iterations to prevent infinite loops
            response = self.client.messages.create(
                model=self.model_config.model_name,
                max_tokens=self.model_config.max_tokens,
                tools=tools,
                messages=messages,
            )

            # Check if we're done
            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return "Query completed successfully"

            # Process tool use
            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        if block.name == "execute_query":
                            try:
                                sql = block.input["sql"]
                                # Use MCP or legacy database manager
                                if self.use_mcp:
                                    results = await self.mcp_client.execute_query(self.db_name, sql)
                                else:
                                    results = self.db_manager.execute_query(sql)
                                tool_results.append(
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": block.id,
                                        "content": json.dumps(
                                            results[:10], default=str
                                        ),
                                    }
                                )
                            except Exception as e:
                                tool_results.append(
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": block.id,
                                        "content": f"Error: {e}",
                                        "is_error": True,
                                    }
                                )

                messages.append({"role": "user", "content": tool_results})
            else:
                break

        return "Unable to process query"

    def _call_qwen(self, user_query: str) -> str:
        """Call Qwen API (Alibaba Tongyi)"""
        prompt = f"""You are a SQL expert. Convert the user's natural language query to SQL and execute it.

Database Schema:
{self.schema}

User Query: {user_query}

Instructions:
1. Generate the appropriate SQL query
2. Execute it against the database
3. Return the results in natural language format"""

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
        """Call Zhipu AI API (GLM)"""
        messages = [
            {
                "role": "user",
                "content": f"""You are a SQL expert. Convert the user's natural language query to SQL.

Database Schema:
{self.schema}

User Query: {user_query}

Provide:
1. The generated SQL query
2. Execute and return results
3. Natural language explanation""",
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

    async def _call_openai_compatible(self, user_query: str) -> str:
        """Call OpenAI-compatible API (支持阿里云、智谱等兼容接口)"""
        # Ensure schema is loaded
        await self._ensure_schema_loaded()

        messages = [
            {
                "role": "system",
                "content": f"""You are a SQL expert. You have access to the following database schema:

{self.schema}

IMPORTANT RULES:
1. Carefully analyze the user's query for any filtering conditions (e.g., "VIP会员", "VIP用户", "会员用户" means filtering by level field)
2. If user asks about specific member types, use WHERE level='VIP会员' or similar conditions
3. Do NOT count all records when user asks about a specific subset
4. Always wrap your SQL in ```sql``` code block
5. After execution, summarize results in natural language matching the original query"""
            },
            {
                "role": "user",
                "content": user_query
            }
        ]

        try:
            # 第一步：生成SQL
            response = self.client.chat.completions.create(
                model=self.model_config.model_name,
                messages=messages,
                temperature=self.model_config.temperature,
                max_tokens=self.model_config.max_tokens,
            )

            assistant_response = response.choices[0].message.content

            # 尝试从响应中提取SQL
            sql_query = self._extract_sql(assistant_response)

            if sql_query:
                try:
                    # 执行SQL
                    if self.use_mcp:
                        results = await self.mcp_client.execute_query(self.db_name, sql_query)
                    else:
                        results = self.db_manager.execute_query(sql_query)
                    result_count = len(results)

                    # 第二步：让模型分析结果
                    messages.append({"role": "assistant", "content": assistant_response})
                    messages.append({
                        "role": "user",
                        "content": f"SQL执行成功，返回 {result_count} 条记录，结果如下（最多显示10条）：\n{json.dumps(results[:10], ensure_ascii=False, default=str)}\n\n请用自然语言总结这些结果。注意：在回复中不要重复显示SQL代码块，我已经在前面展示过了。"
                    })

                    final_response = self.client.chat.completions.create(
                        model=self.model_config.model_name,
                        messages=messages,
                        temperature=self.model_config.temperature,
                        max_tokens=self.model_config.max_tokens,
                    )

                    # 组合响应：SQL + 结果分析
                    return f"```sql\n{sql_query}\n```\n\n{final_response.choices[0].message.content}"

                except Exception as e:
                    return f"```sql\n{sql_query}\n```\n\nSQL执行错误: {e}"
            else:
                return assistant_response

        except Exception as e:
            return f"Error calling OpenAI-compatible API: {e}"

    def _extract_sql(self, text: str) -> Optional[str]:
        """从文本中提取SQL语句"""
        import re

        # 尝试匹配代码块中的SQL
        code_block_pattern = r"```sql\s*(.*?)\s*```"
        match = re.search(code_block_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # 尝试匹配普通代码块
        code_block_pattern = r"```\s*(.*?)\s*```"
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            sql = match.group(1).strip()
            if sql.upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                return sql

        # 尝试直接匹配SELECT语句
        select_pattern = r"(SELECT\s+.*?;?)\s*$"
        match = re.search(select_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip().rstrip(';')

        return None

    async def query(self, user_query: str) -> str:
        """Process user query and return response"""
        provider = self.model_config.provider.lower()

        if provider == "anthropic":
            return await self._call_anthropic(user_query)
        elif provider == "qwen":
            return self._call_qwen(user_query)
        elif provider == "zhipu":
            return self._call_zhipu(user_query)
        elif provider == "openai-compatible":
            return await self._call_openai_compatible(user_query)
        else:
            return f"Unsupported provider: {provider}"

    async def close(self):
        """Clean up resources"""
        if self.use_mcp and self.mcp_client:
            await self.mcp_client.close()
        elif self.db_manager:
            self.db_manager.disconnect()
