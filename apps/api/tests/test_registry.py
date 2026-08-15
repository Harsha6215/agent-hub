"""
Tests for the Agent Registry service.
"""

from agents.base import BaseAgent
from agents.hello.agent import HelloAgent
from apps.api.app.services.agent_registry import AgentRegistry


def test_registry_register_and_get():
    """Register an agent and retrieve it."""
    registry = AgentRegistry()
    agent = HelloAgent()
    registry.register(agent)

    assert registry.get("hello") is agent
    assert registry.count == 1


def test_registry_get_nonexistent():
    """Getting a non-existent agent returns None."""
    registry = AgentRegistry()
    assert registry.get("nonexistent") is None


def test_registry_list_active():
    """list_active returns public agents."""
    registry = AgentRegistry()
    agent = HelloAgent()
    registry.register(agent)

    active = registry.list_active()
    assert len(active) == 1
    assert active[0].slug == "hello"


def test_registry_list_by_category():
    """list_active filters by category."""
    registry = AgentRegistry()
    agent = HelloAgent()
    registry.register(agent)

    # HelloAgent category is "demo"
    assert len(registry.list_active(category="demo")) == 1
    assert len(registry.list_active(category="finance")) == 0


def test_registry_unregister():
    """Unregister removes an agent."""
    registry = AgentRegistry()
    agent = HelloAgent()
    registry.register(agent)

    assert registry.unregister("hello") is True
    assert registry.get("hello") is None
    assert registry.count == 0


def test_registry_unregister_nonexistent():
    """Unregistering a non-existent agent returns False."""
    registry = AgentRegistry()
    assert registry.unregister("nonexistent") is False


def test_registry_discover():
    """discover_and_register finds the hello agent."""
    registry = AgentRegistry()
    registry.discover_and_register()
    assert registry.count >= 1
    assert registry.get("hello") is not None


def test_hello_agent_implements_base():
    """HelloAgent properly implements BaseAgent."""
    agent = HelloAgent()
    assert isinstance(agent, BaseAgent)
    assert agent.name == "Hello World"
    assert agent.slug == "hello"
    assert agent.version == "1.0.0"
    assert agent.category == "demo"
    assert agent.price_per_request == 0


def test_hello_agent_schemas():
    """HelloAgent has valid input/output schemas."""
    agent = HelloAgent()
    input_schema = agent.get_input_schema()
    assert input_schema["type"] == "object"
    assert "name" in input_schema["properties"]
    assert "name" in input_schema["required"]

    output_schema = agent.get_output_schema()
    assert output_schema["type"] == "object"
    assert "greeting" in output_schema["properties"]


def test_hello_agent_documentation():
    """get_documentation returns structured docs."""
    agent = HelloAgent()
    docs = agent.get_documentation()
    assert docs["slug"] == "hello"
    assert "input_schema" in docs
    assert "output_schema" in docs
