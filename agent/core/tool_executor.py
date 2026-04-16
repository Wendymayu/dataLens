"""Tool Executor - Unified interface for tool execution"""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Unified tool executor that wraps MCP Client

    Provides a consistent interface for executing tools
    and handling errors.
    """

    def __init__(self, mcp_client: Any, db_name: str):
        """
        Initialize tool executor

        Args:
            mcp_client: MCPClientWrapper instance
            db_name: Database name to operate on
        """
        self.mcp_client = mcp_client
        self.db_name = db_name

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool and return structured result

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            {
                "success": bool,
                "data": Any,  # On success
                "error": str,  # On failure
                "suggestion": str  # Error suggestion
            }
        """
        try:
            # Add db_name to arguments if not present
            if "db_name" not in arguments:
                arguments["db_name"] = self.db_name

            result = await self._call_tool(tool_name, arguments)

            return {
                "success": True,
                "data": result
            }

        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {e}")

            # Analyze error and provide suggestion
            suggestion = self._get_error_suggestion(str(e))

            return {
                "success": False,
                "error": str(e),
                "suggestion": suggestion
            }

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call the actual tool via MCP client"""

        if tool_name == "execute_query":
            sql = arguments.get("sql", "")
            return await self.mcp_client.execute_query(
                self.db_name, sql
            )

        elif tool_name == "get_schema":
            return await self.mcp_client.get_schema(self.db_name)

        elif tool_name == "get_table_sample":
            table_name = arguments.get("table_name", "")
            limit = arguments.get("limit", 5)
            return await self.mcp_client.get_table_sample(
                self.db_name, table_name, limit
            )

        elif tool_name == "refresh_schema":
            return await self.mcp_client.refresh_schema(self.db_name)

        elif tool_name == "test_connection":
            return await self.mcp_client.test_connection(self.db_name)

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def _get_error_suggestion(self, error: str) -> str:
        """Generate helpful suggestion based on error type"""
        error_lower = error.lower()

        if "syntax" in error_lower:
            return "检查 SQL 语法，确保关键字正确、括号匹配"
        elif "unknown column" in error_lower:
            return "检查字段名是否正确，使用 get_schema 查看表结构"
        elif "doesn't exist" in error_lower or "not found" in error_lower:
            return "检查表名是否正确，使用 get_schema 查看可用表"
        elif "timeout" in error_lower:
            return "查询可能过于复杂，尝试添加 LIMIT 或简化条件"
        elif "connection" in error_lower:
            return "数据库连接问题，请检查配置或使用 test_connection 测试"
        else:
            return "请检查查询参数或尝试简化查询"

    def get_tool_definitions(self) -> list:
        """Return tool definitions for LLM"""
        return [
            {
                "name": "execute_query",
                "description": "执行 SQL 查询并返回结果。只支持 SELECT/SHOW/DESCRIBE/EXPLAIN。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "要执行的 SQL 查询语句"
                        }
                    },
                    "required": ["sql"]
                }
            },
            {
                "name": "get_schema",
                "description": "获取数据库结构，包括所有表名、字段名和类型。",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_table_sample",
                "description": "获取指定表的样本数据，帮助理解数据格式。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "表名"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回行数，默认5",
                            "default": 5
                        }
                    },
                    "required": ["table_name"]
                }
            }
        ]
