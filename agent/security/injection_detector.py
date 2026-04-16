"""SQL Injection Detection"""

import re
from typing import List, Dict, Any


class InjectionDetector:
    """Detects potential SQL injection attempts"""

    # Common injection patterns
    INJECTION_PATTERNS = [
        # Classic injection
        {
            "pattern": r"\'\s*OR\s+\'",
            "name": "OR-based injection",
            "severity": "high"
        },
        {
            "pattern": r"\'\s*AND\s+\'",
            "name": "AND-based injection",
            "severity": "high"
        },
        # Union injection
        {
            "pattern": r"UNION\s+(ALL\s+)?SELECT",
            "name": "UNION injection",
            "severity": "critical"
        },
        # Comment injection
        {
            "pattern": r"--|\/\*|\*\/",
            "name": "Comment injection",
            "severity": "medium"
        },
        # Stacked queries
        {
            "pattern": r";\s*(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|TRUNCATE)",
            "name": "Stacked query injection",
            "severity": "critical"
        },
        # Boolean-based blind injection
        {
            "pattern": r"(AND|OR)\s+\d+\s*=\s*\d+",
            "name": "Boolean blind injection",
            "severity": "high"
        },
        # Time-based blind injection
        {
            "pattern": r"(SLEEP|BENCHMARK|WAITFOR)\s*\(",
            "name": "Time-based blind injection",
            "severity": "critical"
        },
        # Error-based injection
        {
            "pattern": r"(EXTRACTVALUE|UPDATEXML)\s*\(",
            "name": "Error-based injection",
            "severity": "high"
        },
        # Data exfiltration
        {
            "pattern": r"(INTO\s+OUTFILE|INTO\s+DUMPFILE|LOAD_FILE)",
            "name": "Data exfiltration attempt",
            "severity": "critical"
        },
    ]

    def detect(self, sql: str) -> List[Dict[str, Any]]:
        """
        Detect potential injection patterns

        Returns list of detected patterns with severity
        """
        detected = []

        for pattern_info in self.INJECTION_PATTERNS:
            pattern = pattern_info["pattern"]
            if re.search(pattern, sql, re.IGNORECASE):
                detected.append({
                    "name": pattern_info["name"],
                    "severity": pattern_info["severity"],
                    "pattern": pattern,
                })

        return detected

    def is_safe(self, sql: str) -> bool:
        """Quick check if SQL appears safe"""
        detected = self.detect(sql)
        # Only high/critical severity makes it unsafe
        return not any(d["severity"] in ("high", "critical") for d in detected)

    def get_risk_level(self, sql: str) -> str:
        """Get overall risk level"""
        detected = self.detect(sql)

        if not detected:
            return "low"

        severities = [d["severity"] for d in detected]

        if "critical" in severities:
            return "critical"
        if "high" in severities:
            return "high"
        if "medium" in severities:
            return "medium"

        return "low"