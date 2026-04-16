"""Session Memory - Track queries within a session"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


@dataclass
class QueryRecord:
    """Record of a single query execution"""
    timestamp: datetime
    natural_query: str      # User's original question
    sql: Optional[str] = None
    success: bool = False
    result_count: int = 0
    error: Optional[str] = None
    answer: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "natural_query": self.natural_query,
            "sql": self.sql,
            "success": self.success,
            "result_count": self.result_count,
            "error": self.error,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QueryRecord":
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            natural_query=data["natural_query"],
            sql=data.get("sql"),
            success=data.get("success", False),
            result_count=data.get("result_count", 0),
            error=data.get("error"),
            answer=data.get("answer"),
        )


class SessionMemory:
    """
    Session-level memory management

    Tracks queries, results, and discovered patterns within a session.
    Does NOT persist across sessions (privacy-friendly).
    """

    MAX_QUERIES = 20  # Maximum queries to remember per session

    def __init__(self):
        self.queries: List[QueryRecord] = []
        self.discovered_patterns: Dict[str, Any] = {}
        self.current_schema: Optional[str] = None
        self.tables_used: List[str] = []
        self.session_id: Optional[str] = None
        self.created_at: datetime = datetime.now()

    def add_query(self, record: QueryRecord) -> None:
        """
        Add a query record to memory

        Args:
            record: QueryRecord to add
        """
        self.queries.append(record)

        # Keep only recent queries
        if len(self.queries) > self.MAX_QUERIES:
            self.queries = self.queries[-self.MAX_QUERIES:]

        # Track tables used
        if record.sql:
            tables = self._extract_tables(record.sql)
            for table in tables:
                if table not in self.tables_used:
                    self.tables_used.append(table)

    def get_recent_queries(self, n: int = 5) -> List[QueryRecord]:
        """
        Get the most recent N queries

        Args:
            n: Number of queries to return

        Returns:
            List of recent QueryRecords
        """
        return self.queries[-n:] if self.queries else []

    def get_successful_queries(self, n: int = 5) -> List[QueryRecord]:
        """
        Get recent successful queries

        Args:
            n: Maximum number to return

        Returns:
            List of successful QueryRecords
        """
        successful = [q for q in self.queries if q.success]
        return successful[-n:] if successful else []

    def get_failed_queries(self, n: int = 3) -> List[QueryRecord]:
        """
        Get recent failed queries

        Args:
            n: Maximum number to return

        Returns:
            List of failed QueryRecords
        """
        failed = [q for q in self.queries if not q.success]
        return failed[-n:] if failed else []

    def remember_pattern(self, pattern_type: str, pattern: Any) -> None:
        """
        Remember a discovered pattern

        Args:
            pattern_type: Type of pattern (e.g., "table_usage", "common_filters")
            pattern: The pattern data
        """
        if pattern_type not in self.discovered_patterns:
            self.discovered_patterns[pattern_type] = []

        self.discovered_patterns[pattern_type].append(pattern)

    def get_context_for_query(self) -> str:
        """
        Generate context string for next query

        Returns:
            Formatted context string with relevant history
        """
        parts = []

        # Add schema if available
        if self.current_schema:
            parts.append(f"数据库结构：\n{self.current_schema[:500]}...")

        # Add recent successful queries
        successful = self.get_successful_queries(3)
        if successful:
            parts.append("最近成功的查询：")
            for q in successful:
                parts.append(f"- {q.natural_query}")
                if q.sql:
                    parts.append(f"  SQL: {q.sql[:100]}...")

        # Add tables used
        if self.tables_used:
            parts.append(f"本次会话使用过的表：{', '.join(self.tables_used)}")

        return "\n".join(parts) if parts else "无历史上下文"

    def set_schema(self, schema: str) -> None:
        """Store the current database schema"""
        self.current_schema = schema

    def get_last_result_count(self) -> int:
        """Get result count from last query"""
        if self.queries:
            return self.queries[-1].result_count
        return 0

    def get_last_answer(self) -> Optional[str]:
        """Get answer from last query"""
        if self.queries:
            return self.queries[-1].answer
        return None

    def _extract_tables(self, sql: str) -> List[str]:
        """Extract table names from SQL"""
        import re
        # Simple extraction - FROM and JOIN clauses
        tables = []
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
            r'from\s+(\w+)',
            r'join\s+(\w+)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, sql)
            tables.extend(matches)
        return list(set(tables))

    def clear(self) -> None:
        """Clear all memory"""
        self.queries.clear()
        self.discovered_patterns.clear()
        self.tables_used.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize memory to dictionary"""
        return {
            "queries": [q.to_dict() for q in self.queries],
            "discovered_patterns": self.discovered_patterns,
            "current_schema": self.current_schema,
            "tables_used": self.tables_used,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionMemory":
        """Deserialize memory from dictionary"""
        memory = cls()
        memory.queries = [QueryRecord.from_dict(q) for q in data.get("queries", [])]
        memory.discovered_patterns = data.get("discovered_patterns", {})
        memory.current_schema = data.get("current_schema")
        memory.tables_used = data.get("tables_used", [])
        memory.session_id = data.get("session_id")
        if data.get("created_at"):
            memory.created_at = datetime.fromisoformat(data["created_at"])
        return memory
