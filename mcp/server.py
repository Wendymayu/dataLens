"""MCP Server for DataLens database access"""
import asyncio
import json
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from mcp.tools.database_tools import DatabaseTools
from mcp.connection_pool import ConnectionPoolManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


class DataLensMCPServer:
    """MCP Server for DataLens database operations"""

    def __init__(self):
        self.server = Server("datalens-db")
        self.db_tools = DatabaseTools()
        self.pool_manager = ConnectionPoolManager()
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="execute_query",
                    description="Execute SQL query and return results. Only SELECT, SHOW, DESCRIBE, EXPLAIN queries are allowed.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Database name to query"
                            },
                            "sql": {
                                "type": "string",
                                "description": "SQL query to execute"
                            }
                        },
                        "required": ["db_name", "sql"]
                    }
                ),
                Tool(
                    name="get_schema",
                    description="Get database schema information including tables, columns, types, and keys",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Database name"
                            }
                        },
                        "required": ["db_name"]
                    }
                ),
                Tool(
                    name="get_table_sample",
                    description="Get sample data from a specific table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Database name"
                            },
                            "table_name": {
                                "type": "string",
                                "description": "Table name"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of rows to return (default 5)",
                                "default": 5
                            }
                        },
                        "required": ["db_name", "table_name"]
                    }
                ),
                Tool(
                    name="refresh_schema",
                    description="Refresh the cached schema information for a database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Database name"
                            }
                        },
                        "required": ["db_name"]
                    }
                ),
                Tool(
                    name="test_connection",
                    description="Test database connection status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "db_name": {
                                "type": "string",
                                "description": "Database name"
                            }
                        },
                        "required": ["db_name"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            try:
                logger.info(f"Tool called: {name} with arguments: {arguments}")

                if name == "execute_query":
                    result = self.db_tools.execute_query(
                        arguments["db_name"],
                        arguments["sql"]
                    )
                elif name == "get_schema":
                    result = self.db_tools.get_schema(arguments["db_name"])
                elif name == "get_table_sample":
                    result = self.db_tools.get_table_sample(
                        arguments["db_name"],
                        arguments["table_name"],
                        arguments.get("limit", 5)
                    )
                elif name == "refresh_schema":
                    result = self.db_tools.refresh_schema(arguments["db_name"])
                elif name == "test_connection":
                    result = self.db_tools.test_connection(arguments["db_name"])
                else:
                    result = {
                        "success": False,
                        "error": f"Unknown tool: {name}"
                    }

                return [TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )]

            except Exception as e:
                logger.error(f"Tool execution error: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e)
                    })
                )]

    def load_config_from_env(self):
        """Load database configurations from environment variables or config file"""
        import os
        from pathlib import Path

        # Try to load from config.json
        config_path = Path(os.getenv("DATALENS_CONFIG", "config.json"))
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = json.load(f)
                    databases = config_data.get("databases", {})

                    for db_name, db_config in databases.items():
                        self.pool_manager.add_database(
                            name=db_name,
                            host=db_config["host"],
                            port=db_config.get("port", 3306),
                            user=db_config["user"],
                            password=db_config["password"],
                            database=db_config["database"],
                            pool_size=db_config.get("pool_size", 5)
                        )
                        logger.info(f"Loaded database config: {db_name}")

            except Exception as e:
                logger.error(f"Failed to load config from {config_path}: {e}")

    async def run(self):
        """Run the MCP server"""
        logger.info("Starting DataLens MCP Server...")
        self.load_config_from_env()
        logger.info("MCP Server ready")

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point"""
    server = DataLensMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
