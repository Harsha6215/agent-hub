"""
Agent Hub — Agent Registry

All agents live here. Each agent is a folder with an `agent.py`
that exports a class inheriting from BaseAgent.
"""

from agents.base import BaseAgent

__all__ = ["BaseAgent"]
