"""Database connection and query execution"""
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional
from agent.config import DatabaseConfig


class DatabaseManager:
    """Manages MySQL database connections and queries"""

    def __init__(self, db_config: DatabaseConfig):
        self.config = db_config
        self.connection = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
            )
        except Error as e:
            raise Exception(f"Database connection failed: {e}")

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dicts"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            raise Exception(f"Query execution failed: {e}")

    def get_schema(self) -> str:
        """Get database schema information"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{self.config.database}'")
            tables = cursor.fetchall()

            schema_info = f"Database: {self.config.database}\n\nTables:\n"

            for (table_name,) in tables:
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                schema_info += f"\n{table_name}:\n"
                for col in columns:
                    col_name, col_type, col_null, col_key, col_default, col_extra = col

                    # 对于 enum 类型，获取具体取值
                    if col_type.startswith('enum'):
                        try:
                            cursor.execute(f"""
                                SELECT COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS
                                WHERE TABLE_SCHEMA = '{self.config.database}'
                                AND TABLE_NAME = '{table_name}'
                                AND COLUMN_NAME = '{col_name}'
                            """)
                            enum_info = cursor.fetchone()
                            if enum_info:
                                col_type = enum_info[0]  # 例如: enum('普通会员','VIP会员','黄金会员','钻石会员')
                        except:
                            pass

                    schema_info += f"  - {col_name} ({col_type})\n"
                    if col_key == 'PRI':
                        schema_info += f"    [主键]\n"
                    elif col_key == 'MUL':
                        schema_info += f"    [可筛选/索引字段]\n"

            cursor.close()
            return schema_info
        except Error as e:
            raise Exception(f"Schema retrieval failed: {e}")

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            if self.connection and self.connection.is_connected():
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
                return True
        except Error:
            return False
        return False
