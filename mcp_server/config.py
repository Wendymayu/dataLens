"""MCP configuration management"""
from pydantic import BaseModel
from typing import Dict, Optional


class MCPDatabaseConfig(BaseModel):
    """Database configuration for MCP Server"""
    name: str
    host: str
    port: int = 3306
    user: str
    password: str
    database: str
    pool_size: int = 5


class MCPServerConfig(BaseModel):
    """MCP Server configuration"""
    databases: Dict[str, MCPDatabaseConfig] = {}
    schema_cache_ttl: int = 300  # 5 minutes
    max_result_rows: int = 100
    log_level: str = "INFO"
