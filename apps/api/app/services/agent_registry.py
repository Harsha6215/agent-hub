"""
AgentRegistry — Discovers, registers, and manages agents.

Agents are auto-discovered from the `agents/` package on startup.
"""

import importlib
import inspect
import json
import pkgutil

import structlog

from typing import Any

from agents.base import BaseAgent
from apps.api.app.core.cache import cache_get, cache_set, cache_delete

logger = structlog.get_logger(__name__)

CACHE_PREFIX = "agent:"
CACHE_TTL = 300  # 5 minutes


class AgentRegistry:
    """Singleton registry of all available agents."""

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Register an agent instance."""
        if agent.slug in self._agents:
            logger.warning("agent.duplicate_slug", slug=agent.slug)
            return
        self._agents[agent.slug] = agent
        logger.info("agent.registered", slug=agent.slug, name=agent.name, version=agent.version)

    def get(self, slug: str) -> BaseAgent | None:
        """Get an agent by slug."""
        return self._agents.get(slug)

    async def get_cached_docs(self, slug: str) -> dict[str, Any] | None:
        """Get agent docs from Redis cache, falling back to registry."""
        cache_key = f"{CACHE_PREFIX}{slug}:docs"
        cached = await cache_get(cache_key)
        if cached:
            return json.loads(cached)

        agent = self.get(slug)
        if agent:
            docs = agent.get_documentation()
            await cache_set(cache_key, json.dumps(docs), expire=CACHE_TTL)
            return docs
        return None

    def list_active(self, category: str | None = None) -> list[BaseAgent]:
        """List all active public agents, optionally filtered by category."""
        agents = [a for a in self._agents.values() if a.is_public]
        if category:
            agents = [a for a in agents if a.category == category]
        return agents

    def unregister(self, slug: str) -> bool:
        """Remove an agent from the registry."""
        if slug in self._agents:
            del self._agents[slug]
            logger.info("agent.unregistered", slug=slug)
            return True
        return False

    @property
    def count(self) -> int:
        return len(self._agents)

    def discover_and_register(self) -> None:
        """Auto-discover agents from the agents/ package."""
        import agents as agents_pkg

        for importer, modname, ispkg in pkgutil.iter_modules(agents_pkg.__path__):
            if not ispkg:
                continue  # Only look at sub-packages (folders)
            try:
                module = importlib.import_module(f"agents.{modname}.agent")
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseAgent) and obj is not BaseAgent:
                        instance = obj()
                        self.register(instance)
            except (ImportError, AttributeError, TypeError) as e:
                logger.warning("agent.discovery_failed", module=modname, error=str(e))


# Singleton instance
registry = AgentRegistry()
