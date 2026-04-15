"""MCP Service management for FastAPI"""
from agent.mcp_client import MCPClientWrapper
from agent.config import ConfigManager
import logging

logger = logging.getLogger(__name__)


class MCPService:
    """Singleton MCP Service for FastAPI"""

    _instance = None
    _mcp_client = None
    _config_manager = None

    @classmethod
    def get_instance(cls, config_path: str = "config.json"):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
            cls._config_manager = ConfigManager(config_path)
            cls._mcp_client = MCPClientWrapper(cls._config_manager)
            logger.info("MCP Service initialized")
        return cls._instance

    @classmethod
    def get_mcp_client(cls) -> MCPClientWrapper:
        """Get MCP Client instance"""
        if cls._mcp_client is None:
            raise RuntimeError("MCP Service not initialized")
        return cls._mcp_client

    @classmethod
    def get_config_manager(cls) -> ConfigManager:
        """Get ConfigManager instance"""
        if cls._config_manager is None:
            raise RuntimeError("MCP Service not initialized")
        return cls._config_manager

    @classmethod
    async def startup(cls, config_path: str = "config.json"):
        """Startup MCP Service"""
        try:
            cls.get_instance(config_path)
            logger.info("MCP Service started successfully")
        except Exception as e:
            logger.error(f"Failed to start MCP Service: {e}")
            raise

    @classmethod
    async def shutdown(cls):
        """Shutdown MCP Service"""
        try:
            if cls._mcp_client:
                await cls._mcp_client.close()
                cls._mcp_client = None
            cls._instance = None
            cls._config_manager = None
            logger.info("MCP Service shutdown successfully")
        except Exception as e:
            logger.error(f"Error during MCP Service shutdown: {e}")

    @classmethod
    def health_check(cls) -> bool:
        """Check MCP Service health"""
        try:
            return cls._mcp_client is not None
        except:
            return False
