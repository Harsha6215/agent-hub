"""
BaseAgent — Abstract base class for all agents in the platform.

To create a new agent:
1. Create a folder: agents/my_agent/
2. Create agents/my_agent/agent.py
3. Implement a class that inherits from BaseAgent
4. The agent will be auto-discovered on startup
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Abstract base class for all registered agents."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent name."""
        ...

    @property
    @abstractmethod
    def slug(self) -> str:
        """URL-safe identifier (e.g., 'gst-calculator')."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Semver version string."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description of what the agent does."""
        ...

    @property
    def category(self) -> str:
        """Agent category for catalog grouping."""
        return "utility"

    @property
    def price_per_request(self) -> int:
        """Cost per request in paisa. 0 = free."""
        return 0

    @property
    def is_public(self) -> bool:
        """Whether this agent shows in the public catalog."""
        return True

    @abstractmethod
    def get_input_schema(self) -> dict[str, Any]:
        """JSON Schema for agent input validation."""
        ...

    @abstractmethod
    def get_output_schema(self) -> dict[str, Any]:
        """JSON Schema for agent output."""
        ...

    @abstractmethod
    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the agent with validated input.

        Args:
            input_data: Validated input matching get_input_schema()

        Returns:
            Output dict matching get_output_schema()

        Raises:
            ValueError: If input is semantically invalid
            Exception: For execution errors
        """
        ...

    def get_documentation(self) -> dict[str, Any]:
        """Auto-generate documentation from agent metadata."""
        return {
            "name": self.name,
            "slug": self.slug,
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "price_per_request": self.price_per_request,
            "is_public": self.is_public,
            "input_schema": self.get_input_schema(),
            "output_schema": self.get_output_schema(),
        }
