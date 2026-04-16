"""Agent service wrapper for DataLens with session memory support"""
from agent.agent import NL2SQLAgent
from agent.config import ConfigManager
from agent.memory import SessionMemory
from api.services.mcp_service import MCPService
from typing import Optional, Dict
import re


class AgentService:
    """Service wrapper for NL2SQLAgent with session support"""

    _instance = None

    def __init__(self, config_path: str = "config.json"):
        self.config_manager = ConfigManager(config_path)
        self._agent_cache: dict = {}
        self._memory_store: Dict[str, SessionMemory] = {}  # session_id -> memory
        self.use_mcp = self.config_manager.config.use_mcp

    @classmethod
    def get_instance(cls) -> "AgentService":
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton instance"""
        if cls._instance:
            for agent in cls._instance._agent_cache.values():
                try:
                    agent.close()
                except:
                    pass
        cls._instance = None

    def get_agent(self, db_name: Optional[str] = None, memory: Optional[SessionMemory] = None) -> NL2SQLAgent:
        """Get or create agent for database with optional session memory"""
        actual_db = db_name or self.config_manager.config.current_database
        db_config = self.config_manager.get_database(actual_db)

        if not db_config:
            raise ValueError(f"Database '{actual_db}' not found")

        # Create agent with memory (each agent has its own memory)
        agent = NL2SQLAgent(
            self.config_manager.config.model,
            db_config,
            config_manager=self.config_manager,
            use_mcp=self.use_mcp,
            session_memory=memory  # Pass memory to agent
        )
        return agent

    async def query(self, query: str, db_name: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """
        Execute query and return response

        Args:
            query: User's natural language query
            db_name: Database name (optional, uses default)
            session_id: Session ID for memory continuity (optional)

        Returns:
            Natural language response
        """
        # Get or create memory for session
        if session_id:
            memory = self._memory_store.get(session_id)
            if memory is None:
                memory = SessionMemory()
                memory.session_id = session_id
                self._memory_store[session_id] = memory
        else:
            memory = None

        # Get agent with memory
        agent = self.get_agent(db_name, memory)
        response = await agent.query(query)

        # Update memory store if session
        if session_id and agent.memory:
            self._memory_store[session_id] = agent.memory

        return response

    def clear_session(self, session_id: str) -> bool:
        """
        Clear memory for a specific session

        Args:
            session_id: Session ID to clear

        Returns:
            True if session was found and cleared
        """
        if session_id in self._memory_store:
            del self._memory_store[session_id]
            return True
        return False

    def extract_sql(self, text: str) -> Optional[str]:
        """Extract SQL from response text"""
        # Try code block pattern
        code_block = r"```sql\s*(.*?)\s*```"
        match = re.search(code_block, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try generic code block
        generic_block = r"```\s*(.*?)\s*```"
        match = re.search(generic_block, text, re.DOTALL)
        if match:
            sql = match.group(1).strip()
            if sql.upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                return sql

        return None

    def clear_cache(self, db_name: Optional[str] = None):
        """Clear agent cache"""
        if db_name:
            if db_name in self._agent_cache:
                # Only close if not using MCP (MCP manages connections)
                if not self.use_mcp:
                    try:
                        self._agent_cache[db_name].close()
                    except:
                        pass
                del self._agent_cache[db_name]
        else:
            if not self.use_mcp:
                for agent in self._agent_cache.values():
                    try:
                        agent.close()
                    except:
                        pass
            self._agent_cache.clear()