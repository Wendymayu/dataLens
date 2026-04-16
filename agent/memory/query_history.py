"""Query History Analysis"""

from typing import List, Dict, Any, Optional
from collections import Counter
from agent.memory.session_memory import QueryRecord


class QueryHistory:
    """
    Analyze query history for patterns and insights
    """

    def __init__(self, queries: List[QueryRecord]):
        """
        Initialize with list of query records

        Args:
            queries: List of QueryRecord objects
        """
        self.queries = queries

    def get_common_tables(self, n: int = 5) -> List[str]:
        """
        Get most frequently queried tables

        Args:
            n: Number of tables to return

        Returns:
            List of table names sorted by frequency
        """
        tables = []
        for q in self.queries:
            if q.sql:
                extracted = self._extract_tables(q.sql)
                tables.extend(extracted)

        counter = Counter(tables)
        return [t for t, _ in counter.most_common(n)]

    def get_failed_patterns(self) -> List[Dict[str, Any]]:
        """
        Analyze failed queries for patterns

        Returns:
            List of pattern dicts with error type and count
        """
        failed = [q for q in self.queries if not q.success]
        if not failed:
            return []

        error_patterns = Counter()
        for q in failed:
            if q.error:
                error_type = self._classify_error(q.error)
                error_patterns[error_type] += 1

        return [
            {"error_type": et, "count": c}
            for et, c in error_patterns.most_common()
        ]

    def get_success_rate(self) -> float:
        """
        Calculate query success rate

        Returns:
            Success rate as percentage (0-100)
        """
        if not self.queries:
            return 0.0

        successful = sum(1 for q in self.queries if q.success)
        return (successful / len(self.queries)) * 100

    def get_avg_result_count(self) -> float:
        """
        Get average result count for successful queries

        Returns:
            Average result count
        """
        successful = [q for q in self.queries if q.success and q.result_count > 0]
        if not successful:
            return 0.0

        return sum(q.result_count for q in successful) / len(successful)

    def suggest_improvements(self) -> List[str]:
        """
        Generate improvement suggestions based on history

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # Check success rate
        rate = self.get_success_rate()
        if rate < 50:
            suggestions.append("成功率较低，建议先了解数据库结构再查询")

        # Check failed patterns
        failed_patterns = self.get_failed_patterns()
        for pattern in failed_patterns[:3]:
            error_type = pattern["error_type"]
            if error_type == "syntax_error":
                suggestions.append("存在 SQL 语法错误，注意检查关键字和括号")
            elif error_type == "unknown_column":
                suggestions.append("字段名错误较多，建议先用 get_schema 查看表结构")
            elif error_type == "unknown_table":
                suggestions.append("表名错误较多，建议先用 get_schema 确认表名")

        # Check if user queries without checking schema
        schema_checks = sum(
            1 for q in self.queries
            if q.sql and "SHOW" in q.sql.upper()
        )
        if len(self.queries) > 5 and schema_checks == 0:
            suggestions.append("建议复杂查询前先查看表结构")

        return suggestions

    def _extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL"""
        import re
        tables = []
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, sql, re.IGNORECASE)
            tables.extend(matches)
        return tables

    def _classify_error(self, error: str) -> str:
        """Classify error type"""
        error_lower = error.lower()

        if "syntax" in error_lower:
            return "syntax_error"
        elif "unknown column" in error_lower or "field" in error_lower:
            return "unknown_column"
        elif "doesn't exist" in error_lower or "not found" in error_lower:
            return "unknown_table"
        elif "timeout" in error_lower:
            return "timeout"
        elif "permission" in error_lower or "access denied" in error_lower:
            return "permission_denied"
        else:
            return "other"
