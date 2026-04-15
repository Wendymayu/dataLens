"""MCP Client wrapper for DataLens Agent"""
import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPClientWrapper:
    """Wrapper for MCP Client to communicate with DataLens MCP Server"""

    def __init__(self, config_manager):
        """Initialize MCP Client

        Args:
            config_manager: ConfigManager instance with database configurations
        """
        self.config_manager = config_manager
        self.session: Optional[ClientSession] = None
        self.server_process: Optional[subprocess.Popen] = None
        self._read_stream = None
        self._write_stream = None
        self._initialized = False

    async def _start_server(self):
        """Start MCP Server as subprocess"""
        try:
            # Get Python executable path
            python_exe = sys.executable

            # Get MCP server script path
            server_script = Path(__file__).parent.parent / "mcp_server" / "server.py"

            # Prepare database configurations as environment variable
            db_configs = {}
            for name, db_config in self.config_manager.config.databases.items():
                db_configs[name] = {
                    "name": name,
                    "host": db_config.host,
                    "port": db_config.port,
                    "user": db_config.user,
                    "password": db_config.password,
                    "database": db_config.database
                }

            # Create server parameters
            server_params = StdioServerParameters(
                command=python_exe,
                args=["-m", "mcp_server.server"],
                env={
                    **subprocess.os.environ,
                    "DATALENS_DB_CONFIG": json.dumps(db_configs)
                }
            )

            # Start stdio client
            self._read_stream, self._write_stream = await stdio_client(server_params)

            # Create session
            self.session = ClientSession(self._read_stream, self._write_stream)
            await self.session.__aenter__()

            # Initialize session
            await self.session.initialize()

            self._initialized = True
            logger.info("MCP Server started successfully")

        except Exception as e:
            logger.error(f"Failed to start MCP Server: {e}")
            raise Exception(f"MCP Server startup failed: {e}")

    async def _ensure_initialized(self):
        """Ensure MCP Client is initialized"""
        if not self._initialized:
            await self._start_server()

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result as dictionary
        """
        await self._ensure_initialized()

        try:
            result = await self.session.call_tool(tool_name, arguments)

            # Parse result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)

            return {"success": False, "error": "Empty response from server"}

        except Exception as e:
            logger.error(f"Tool call failed: {tool_name}, error: {e}")
            return {"success": False, "error": str(e)}

    def execute_query(self, db_name: str, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query

        Args:
            db_name: Database name
            sql: SQL query

        Returns:
            List of result rows as dictionaries
        """
        result = asyncio.run(self._call_tool("execute_query", {
            "db_name": db_name,
            "sql": sql
        }))

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            raise Exception(f"Query execution failed: {error_msg}")

        return result.get("results", [])

    def get_schema(self, db_name: str) -> str:
        """Get database schema

        Args:
            db_name: Database name

        Returns:
            Schema description as string
        """
        result = asyncio.run(self._call_tool("get_schema", {
            "db_name": db_name
        }))

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            raise Exception(f"Schema retrieval failed: {error_msg}")

        return result.get("schema", "")

    def get_table_sample(self, db_name: str, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample data from table

        Args:
            db_name: Database name
            table_name: Table name
            limit: Number of rows to return

        Returns:
            List of sample rows
        """
        result = asyncio.run(self._call_tool("get_table_sample", {
            "db_name": db_name,
            "table_name": table_name,
            "limit": limit
        }))

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            raise Exception(f"Table sample retrieval failed: {error_msg}")

        return result.get("results", [])

    def refresh_schema(self, db_name: str):
        """Refresh schema cache

        Args:
            db_name: Database name
        """
        result = asyncio.run(self._call_tool("refresh_schema", {
            "db_name": db_name
        }))

        if not result.get("success"):
            error_msg = result.get("error", "Unknown error")
            raise Exception(f"Schema refresh failed: {error_msg}")

    def test_connection(self, db_name: str) -> bool:
        """Test database connection

        Args:
            db_name: Database name

        Returns:
            True if connection is active
        """
        result = asyncio.run(self._call_tool("test_connection", {
            "db_name": db_name
        }))

        return result.get("success", False)

    async def _stop_server(self):
        """Stop MCP Server"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None

            if self._read_stream:
                self._read_stream = None
            if self._write_stream:
                self._write_stream = None

            self._initialized = False
            logger.info("MCP Server stopped")

        except Exception as e:
            logger.error(f"Error stopping MCP Server: {e}")

    def close(self):
        """Close MCP Client and stop server"""
        if self._initialized:
            asyncio.run(self._stop_server())
