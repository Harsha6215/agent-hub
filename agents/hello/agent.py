"""
Hello Agent — Example agent for testing the platform.

Echoes back the user's message with a greeting.
"""

from typing import Any

from agents.base import BaseAgent


class HelloAgent(BaseAgent):
    """A simple hello/echo agent for testing."""

    @property
    def name(self) -> str:
        return "Hello World"

    @property
    def slug(self) -> str:
        return "hello"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "A simple greeting agent. Send a name, get a personalized hello back."

    @property
    def category(self) -> str:
        return "demo"

    @property
    def price_per_request(self) -> int:
        return 0  # Free

    def get_input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet",
                    "minLength": 1,
                    "maxLength": 100,
                },
                "language": {
                    "type": "string",
                    "description": "Greeting language",
                    "enum": ["en", "hi", "es", "fr"],
                    "default": "en",
                },
            },
            "required": ["name"],
        }

    def get_output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "greeting": {"type": "string"},
                "agent": {"type": "string"},
                "version": {"type": "string"},
            },
        }

    async def execute(self, input_data: dict[str, Any]) -> dict[str, Any]:
        name = input_data["name"]
        language = input_data.get("language", "en")

        greetings = {
            "en": f"Hello, {name}! Welcome to Agent Hub.",
            "hi": f"नमस्ते, {name}! Agent Hub में आपका स्वागत है।",
            "es": f"¡Hola, {name}! Bienvenido a Agent Hub.",
            "fr": f"Bonjour, {name}! Bienvenue sur Agent Hub.",
        }

        return {
            "greeting": greetings.get(language, greetings["en"]),
            "agent": self.slug,
            "version": self.version,
        }
