"""Base Agent Interface for DataLens"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class AgentResult:
    """Result of an agent execution"""
    success: bool
    answer: str
    sql: Optional[str] = None
    result_count: int = 0
    error: Optional[str] = None
    steps: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ToolDefinition:
    """Definition of a tool available to the agent"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base class for all agents"""

    def __init__(
        self,
        model_config: Any,
        db_name: str,
        mcp_client: Any = None
    ):
        self.model_config = model_config
        self.db_name = db_name
        self.mcp_client = mcp_client

    @abstractmethod
    async def query(self, user_query: str, **kwargs) -> AgentResult:
        """
        Process user query and return result

        Args:
            user_query: Natural language query from user
            **kwargs: Additional context (memory, schema, etc.)

        Returns:
            AgentResult with answer and execution details
        """
        pass

    @abstractmethod
    def get_available_tools(self) -> List[ToolDefinition]:
        """Return list of tools available to this agent"""
        pass

    def _get_tools_description(self) -> str:
        """Generate human-readable tools description"""
        tools = self.get_available_tools()
        descriptions = []
        for tool in tools:
            params_str = ", ".join(tool.required)
            descriptions.append(
                f"- {tool.name}({params_str}): {tool.description}"
            )
        return "\n".join(descriptions)
