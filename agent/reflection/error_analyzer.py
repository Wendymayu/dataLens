"""Error Analyzer - Analyze execution errors and provide suggestions"""

import re
from typing import Dict, Any, List, Optional


class ErrorAnalyzer:
    """
    Analyze SQL execution errors and provide structured information
    """

    ERROR_PATTERNS = {
        "syntax_error": {
            "patterns": [
                r"SQL syntax.*?near '(.+?)'",
                r"syntax error.*?near '(.+?)'",
                r"You have an error in your SQL syntax",
            ],
            "suggestion": "检查 SQL 语法，特别是关键字、括号和引号是否匹配",
            "severity": "high"
        },
        "unknown_column": {
            "patterns": [
                r"Unknown column '(.+?)'",
                r"column '(.+?)' does not exist",
                r"field '(.+?)' not found",
            ],
            "suggestion": "检查字段名是否正确，使用 get_schema 查看表结构",
            "severity": "medium"
        },
        "unknown_table": {
            "patterns": [
                r"Table '(.+?)' doesn't exist",
                r"table '(.+?)' not found",
                r"Unknown table '(.+?)'",
            ],
            "suggestion": "检查表名是否正确，使用 get_schema 查看可用表",
            "severity": "medium"
        },
        "timeout": {
            "patterns": [
                r"Query execution exceeded",
                r"timeout",
                r"execution time",
            ],
            "suggestion": "查询可能过于复杂，尝试添加 LIMIT 或简化条件",
            "severity": "medium"
        },
        "permission_denied": {
            "patterns": [
                r"Access denied",
                r"permission denied",
                r"not authorized",
            ],
            "suggestion": "权限不足，当前用户无法执行此操作",
            "severity": "high"
        },
        "connection_error": {
            "patterns": [
                r"Connection refused",
                r"Can't connect",
                r"Lost connection",
            ],
            "suggestion": "数据库连接问题，请检查网络或配置",
            "severity": "critical"
        },
    }

    def analyze(self, error_message: str) -> Dict[str, Any]:
        """
        Analyze error message and return structured information

        Args:
            error_message: Raw error message string

        Returns:
            {
                "error_type": str,
                "matched_text": str,  # Extracted from pattern
                "suggestion": str,
                "severity": str,
                "raw_error": str,
            }
        """
        error_lower = error_message.lower()

        for error_type, config in self.ERROR_PATTERNS.items():
            for pattern in config["patterns"]:
                match = re.search(pattern, error_message, re.IGNORECASE)
                if match:
                    matched_text = match.group(1) if match.groups() else match.group(0)

                    return {
                        "error_type": error_type,
                        "matched_text": matched_text,
                        "suggestion": config["suggestion"],
                        "severity": config["severity"],
                        "raw_error": error_message,
                    }

        # Unknown error type
        return {
            "error_type": "unknown",
            "matched_text": "",
            "suggestion": "请检查查询语句，或尝试简化查询",
            "severity": "low",
            "raw_error": error_message,
        }

    def get_quick_fix(self, error_type: str, context: Dict[str, Any] = None) -> str:
        """
        Get quick fix suggestion for error type

        Args:
            error_type: Type of error
            context: Additional context (schema, sql, etc.)

        Returns:
            Quick fix suggestion string
        """
        fixes = {
            "syntax_error": "请检查 SQL 语法，确保：\n"
                           "1. 关键字拼写正确\n"
                           "2. 括号成对出现\n"
                           "3. 字符串用引号包裹\n"
                           "4. 语句以分号结尾（可选）",

            "unknown_column": "字段名可能错误，建议：\n"
                             "1. 使用 get_schema 查看表结构\n"
                             "2. 检查字段名大小写\n"
                             "3. 确认是否使用了正确的表别名",

            "unknown_table": "表名可能错误，建议：\n"
                            "1. 使用 get_schema 查看可用表\n"
                            "2. 检查表名拼写\n"
                            "3. 确认数据库选择正确",

            "timeout": "查询超时，建议：\n"
                       "1. 添加 LIMIT 限制结果数量\n"
                       "2. 添加更精确的 WHERE 条件\n"
                       "3. 避免使用 SELECT *",

            "permission_denied": "权限不足，请：\n"
                                "1. 确认当前用户有查询权限\n"
                                "2. 联系管理员授权",

            "connection_error": "连接问题，请：\n"
                               "1. 检查数据库服务是否运行\n"
                               "2. 检查网络连接\n"
                               "3. 使用 test_connection 测试连接",
        }

        return fixes.get(error_type, "请检查查询语句")

    def is_retriable(self, error_type: str) -> bool:
        """Check if error is retriable after correction"""
        # Syntax and unknown column/table errors can be retried
        retriable_types = {"syntax_error", "unknown_column", "unknown_table"}
        return error_type in retriable_types

    def get_related_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL that might be related to error"""
        tables = []
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
            r'INTO\s+(\w+)',
            r'UPDATE\s+(\w+)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            tables.extend(matches)
        return list(set(tables))
