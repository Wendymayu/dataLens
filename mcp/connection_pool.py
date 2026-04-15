"""Connection pool management for MySQL databases"""
import mysql.connector
from mysql.connector import pooling, Error
from typing import Dict, List, Any, Optional
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class ConnectionPoolManager:
    """Manages MySQL connection pools for multiple databases"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._pools: Dict[str, pooling.MySQLConnectionPool] = {}
        self._configs: Dict[str, dict] = {}
        self._schema_cache: Dict[str, tuple] = {}  # (schema, timestamp)
        self._cache_ttl = 300  # 5 minutes
        self._initialized = True

    def add_database(self, name: str, host: str, port: int, user: str,
                     password: str, database: str, pool_size: int = 5):
        """Add a database configuration and create connection pool"""
        try:
            config = {
                'host': host,
                'port': port,
                'user': user,
                'password': password,
                'database': database,
            }

            # Create connection pool
            pool = pooling.MySQLConnectionPool(
                pool_name=f"pool_{name}",
                pool_size=pool_size,
                pool_reset_session=True,
                **config
            )

            self._pools[name] = pool
            self._configs[name] = config
            logger.info(f"Created connection pool for database: {name}")

        except Error as e:
            logger.error(f"Failed to create connection pool for {name}: {e}")
            raise Exception(f"Connection pool creation failed: {e}")

    def get_connection(self, db_name: str):
        """Get a connection from the pool"""
        if db_name not in self._pools:
            raise ValueError(f"Database '{db_name}' not configured")

        try:
            return self._pools[db_name].get_connection()
        except Error as e:
            logger.error(f"Failed to get connection for {db_name}: {e}")
            raise Exception(f"Connection acquisition failed: {e}")

    def execute_query(self, db_name: str, sql: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        # Security check: only allow read-only queries
        sql_upper = sql.strip().upper()
        allowed_keywords = ('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN', 'DESC')
        if not sql_upper.startswith(allowed_keywords):
            raise ValueError(f"Only read-only queries are allowed. Query starts with: {sql_upper.split()[0]}")

        connection = None
        try:
            connection = self.get_connection(db_name)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()

            # Limit results to 100 rows
            if len(results) > 100:
                logger.warning(f"Query returned {len(results)} rows, truncating to 100")
                results = results[:100]

            return results

        except Error as e:
            logger.error(f"Query execution failed for {db_name}: {e}")
            raise Exception(f"Query execution failed: {e}")
        finally:
            if connection:
                connection.close()

    def get_schema(self, db_name: str, use_cache: bool = True) -> str:
        """Get database schema information with caching"""
        import time

        # Check cache
        if use_cache and db_name in self._schema_cache:
            schema, timestamp = self._schema_cache[db_name]
            if time.time() - timestamp < self._cache_ttl:
                logger.debug(f"Using cached schema for {db_name}")
                return schema

        connection = None
        try:
            connection = self.get_connection(db_name)
            cursor = connection.cursor()

            # Get database name
            config = self._configs[db_name]
            database = config['database']

            # Get all tables
            cursor.execute(
                f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
                f"WHERE TABLE_SCHEMA = '{database}'"
            )
            tables = cursor.fetchall()

            schema_info = f"Database: {database}\n\nTables:\n"

            for (table_name,) in tables:
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                schema_info += f"\n{table_name}:\n"

                for col in columns:
                    col_name, col_type, col_null, col_key, col_default, col_extra = col

                    # Get enum values if applicable
                    if col_type.startswith('enum'):
                        try:
                            cursor.execute(f"""
                                SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS
                                WHERE TABLE_SCHEMA = '{database}'
                                AND TABLE_NAME = '{table_name}'
                                AND COLUMN_NAME = '{col_name}'
                            """)
                            enum_info = cursor.fetchone()
                            if enum_info:
                                col_type = enum_info[0]
                        except:
                            pass

                    schema_info += f"  - {col_name} ({col_type})\n"
                    if col_key == 'PRI':
                        schema_info += f"    [主键]\n"
                    elif col_key == 'MUL':
                        schema_info += f"    [可筛选/索引字段]\n"

            cursor.close()

            # Update cache
            self._schema_cache[db_name] = (schema_info, time.time())
            logger.info(f"Schema cached for {db_name}")

            return schema_info

        except Error as e:
            logger.error(f"Schema retrieval failed for {db_name}: {e}")
            raise Exception(f"Schema retrieval failed: {e}")
        finally:
            if connection:
                connection.close()

    def get_table_sample(self, db_name: str, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample data from a table"""
        if limit > 20:
            limit = 20  # Max 20 rows

        sql = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_query(db_name, sql)

    def refresh_schema(self, db_name: str):
        """Manually refresh schema cache"""
        if db_name in self._schema_cache:
            del self._schema_cache[db_name]
        logger.info(f"Schema cache cleared for {db_name}")

    def test_connection(self, db_name: str) -> bool:
        """Test database connection"""
        connection = None
        try:
            connection = self.get_connection(db_name)
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except:
            return False
        finally:
            if connection:
                connection.close()

    def close_all(self):
        """Close all connection pools"""
        for name, pool in self._pools.items():
            try:
                # Connection pools don't have a direct close method
                # Connections are closed when they're returned to the pool
                logger.info(f"Connection pool for {name} will be cleaned up")
            except Exception as e:
                logger.error(f"Error closing pool for {name}: {e}")

        self._pools.clear()
        self._configs.clear()
        self._schema_cache.clear()
