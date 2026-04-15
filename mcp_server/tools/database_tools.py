"""Database tools for MCP Server"""
from typing import Any, Dict, List
from mcp_server.connection_pool import ConnectionPoolManager
import logging

logger = logging.getLogger(__name__)


class DatabaseTools:
    """Database operation tools for MCP"""

    def __init__(self):
        self.pool_manager = ConnectionPoolManager()

    def execute_query(self, db_name: str, sql: str) -> Dict[str, Any]:
        """Execute SQL query and return results

        Args:
            db_name: Database name
            sql: SQL query to execute

        Returns:
            Dict with 'results' (list of dicts) and 'row_count' (int)
        """
        try:
            results = self.pool_manager.execute_query(db_name, sql)
            return {
                "success": True,
                "results": results,
                "row_count": len(results),
                "message": f"Query executed successfully, returned {len(results)} rows"
            }
        except Exception as e:
            logger.error(f"execute_query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "row_count": 0
            }

    def get_schema(self, db_name: str) -> Dict[str, Any]:
        """Get database schema information

        Args:
            db_name: Database name

        Returns:
            Dict with 'schema' (string description)
        """
        try:
            schema = self.pool_manager.get_schema(db_name)
            return {
                "success": True,
                "schema": schema,
                "message": "Schema retrieved successfully"
            }
        except Exception as e:
            logger.error(f"get_schema failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "schema": ""
            }

    def get_table_sample(self, db_name: str, table_name: str, limit: int = 5) -> Dict[str, Any]:
        """Get sample data from a table

        Args:
            db_name: Database name
            table_name: Table name
            limit: Number of rows to return (default 5)

        Returns:
            Dict with 'results' (list of dicts)
        """
        try:
            sql = f"SELECT * FROM {table_name} LIMIT {limit}"
            results = self.pool_manager.execute_query(db_name, sql)
            return {
                "success": True,
                "results": results,
                "row_count": len(results),
                "message": f"Retrieved {len(results)} sample rows from {table_name}"
            }
        except Exception as e:
            logger.error(f"get_table_sample failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "row_count": 0
            }

    def refresh_schema(self, db_name: str) -> Dict[str, Any]:
        """Refresh schema cache for a database

        Args:
            db_name: Database name

        Returns:
            Dict with success status
        """
        try:
            self.pool_manager.refresh_schema(db_name)
            return {
                "success": True,
                "message": f"Schema cache refreshed for {db_name}"
            }
        except Exception as e:
            logger.error(f"refresh_schema failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def test_connection(self, db_name: str) -> Dict[str, Any]:
        """Test database connection

        Args:
            db_name: Database name

        Returns:
            Dict with connection status
        """
        try:
            is_connected = self.pool_manager.test_connection(db_name)
            return {
                "success": is_connected,
                "message": f"Connection to {db_name} is {'active' if is_connected else 'failed'}"
            }
        except Exception as e:
            logger.error(f"test_connection failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
