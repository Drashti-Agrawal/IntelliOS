"""
IntelliOS Agents Module

This module contains the agentic AI components:
- Base agent class for all agents
- Specialized agents for different tasks
- Agent orchestration and management
- Agent communication and coordination
"""

from .base_agent import BaseAgent
from .context_monitor_agent import ContextMonitorAgent

__all__ = [
    'BaseAgent',
    'ContextMonitorAgent'
]
