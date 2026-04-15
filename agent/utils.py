"""Utility functions for DataLens"""
import logging
import sys
from typing import Any
import json
from rich.console import Console


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def setup_windows_encoding():
    """Configure Windows console to use UTF-8 encoding.

    Windows console defaults to cp1252/gbk, causing UTF-8 emoji and unicode to fail.
    This wraps stdout/stderr with UTF-8 encoding to fix the issue.
    """
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def get_console() -> Console:
    """Get a configured Console instance with Windows compatibility."""
    return Console(force_terminal=True, legacy_windows=False)


def get_logger(name: str):
    """Get a logger instance"""
    return logging.getLogger(name)


def serialize_result(data: Any) -> str:
    """Serialize result to JSON string"""
    try:
        return json.dumps(data, default=str, indent=2)
    except (TypeError, ValueError):
        return str(data)


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text
