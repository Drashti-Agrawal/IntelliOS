"""
IntelliOS Core Module

This module contains core system components:
- Digital DNA state management
- Topic definitions and categorization
- LangGraph workflow orchestration
- State persistence and retrieval
"""

from .topics import TOPICS, TOPIC_EXAMPLES
from .ddna_state import (
    DigitalDNAState,
    DeviceContext,
    ApplicationState,
    BrowserState,
    TerminalSession,
    FileContext,
    UserPreferences,
    TaskIntent,
    ExecutionPlan,
    ExecutionLog,
    create_initial_state,
    update_state_timestamp,
    add_agent_message,
    get_state_summary
)

__all__ = [
    # Topics
    'TOPICS', 
    'TOPIC_EXAMPLES',
    
    # Digital DNA State
    'DigitalDNAState',
    'DeviceContext',
    'ApplicationState', 
    'BrowserState',
    'TerminalSession',
    'FileContext',
    'UserPreferences',
    'TaskIntent',
    'ExecutionPlan',
    'ExecutionLog',
    
    # State management functions
    'create_initial_state',
    'update_state_timestamp', 
    'add_agent_message',
    'get_state_summary'
]
