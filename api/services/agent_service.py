"""Agent service wrapper for DataLens"""
from agent.agent import NL2SQLAgent
from agent.config import ConfigManager
from typing import Optional
import re


class AgentService:
    """Service wrapper for NL2SQLAgent"""

    _instance = None

    def __init__(self, config_path: str = "config.json"):
        self.config_manager = ConfigManager(config_path)
        self._agent_cache: dict = {}

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

    def get_agent(self, db_name: Optional[str] = None) -> NL2SQLAgent:
        """Get or create agent for database"""
        actual_db = db_name or self.config_manager.config.current_database
        db_config = self.config_manager.get_database(actual_db)

        if not db_config:
            raise ValueError(f"Database '{actual_db}' not found")

        # Create new agent each time to ensure fresh connection
        if actual_db in self._agent_cache:
            try:
                self._agent_cache[actual_db].close()
            except:
                pass

        agent = NL2SQLAgent(
            self.config_manager.config.model,
            db_config
        )
        self._agent_cache[actual_db] = agent
        return agent

    def query(self, query: str, db_name: Optional[str] = None) -> str:
        """Execute query and return response"""
        agent = self.get_agent(db_name)
        return agent.query(query)

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
                try:
                    self._agent_cache[db_name].close()
                except:
                    pass
                del self._agent_cache[db_name]
        else:
            for agent in self._agent_cache.values():
                try:
                    agent.close()
                except:
                    pass
            self._agent_cache.clear()