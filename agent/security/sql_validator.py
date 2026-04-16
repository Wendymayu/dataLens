"""SQL Validation and Security Check"""

import re
from typing import Tuple, List
from enum import Enum


class QueryType(Enum):
    """Allowed query types"""
    SELECT = "SELECT"
    SHOW = "SHOW"
    DESCRIBE = "DESCRIBE"
    EXPLAIN = "EXPLAIN"
    DESC = "DESC"


class SQLValidator:
    """Validates SQL queries for security and safety"""

    # Dangerous patterns that should never appear
    DANGEROUS_PATTERNS = [
        # SQL injection patterns
        r";\s*DROP",
        r";\s*DELETE",
        r";\s*INSERT",
        r";\s*UPDATE",
        r";\s*ALTER",
        r";\s*CREATE",
        r";\s*TRUNCATE",
        r"--\s*$",  # SQL comment at end
        r"UNION\s+SELECT",
        r"INTO\s+OUTFILE",
        r"INTO\s+DUMPFILE",
        r"LOAD_FILE",
        # Dangerous functions
        r"SLEEP\s*\(",
        r"BENCHMARK\s*\(",
        r"GET_LOCK\s*\(",
    ]

    # Performance warning patterns
    PERFORMANCE_WARNINGS = [
        (r"SELECT\s+\*\s+FROM", "SELECT * may return too many columns"),
        (r"WHERE\s+1\s*=\s*1", "WHERE 1=1 is inefficient"),
        (r"LIKE\s+\'%.*%\'", "LIKE with leading % prevents index usage"),
        (r"OR\s+.*=.*=", "Multiple OR conditions may be slow"),
    ]

    def __init__(self, max_result_rows: int = 100):
        self.max_result_rows = max_result_rows

    def validate(self, sql: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate SQL query

        Returns:
            (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        sql_upper = sql.strip().upper()

        # Check query type
        allowed_prefixes = [qt.value for qt in QueryType]
        is_allowed_type = any(sql_upper.startswith(prefix) for prefix in allowed_prefixes)

        if not is_allowed_type:
            first_word = sql_upper.split()[0] if sql_upper.split() else "EMPTY"
            errors.append(f"Query type '{first_word}' is not allowed. Only {', '.join(allowed_prefixes)} are permitted.")

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, sql_upper, re.IGNORECASE):
                errors.append(f"Potentially dangerous SQL pattern detected: {pattern}")

        # Check for performance issues
        for pattern, message in self.PERFORMANCE_WARNINGS:
            if re.search(pattern, sql, re.IGNORECASE):
                warnings.append(message)

        # Check for LIMIT
        if "LIMIT" not in sql_upper and sql_upper.startswith("SELECT"):
            warnings.append(f"No LIMIT clause. Results will be capped at {self.max_result_rows} rows.")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings

    def get_safe_limit(self, sql: str) -> str:
        """Add LIMIT if not present"""
        sql_upper = sql.strip().upper()

        if "LIMIT" not in sql_upper and sql_upper.startswith("SELECT"):
            # Add safe limit
            return f"{sql.rstrip(';')} LIMIT {self.max_result_rows}"

        return sql


def validate_sql(sql: str) -> Tuple[bool, List[str], List[str]]:
    """
    Quick validation function

    Usage:
        is_valid, errors, warnings = validate_sql(sql)
        if not is_valid:
            raise ValueError(errors[0])
    """
    validator = SQLValidator()
    return validator.validate(sql)