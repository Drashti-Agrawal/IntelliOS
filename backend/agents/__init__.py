"""
IntelliOS Agents Package

This package contains all the agentic AI agents for the IntelliOS system.
Each agent is responsible for specific aspects of workspace management and
user context understanding.
"""

from .base_agent import BaseAgent
from .context_monitor_agent import ContextMonitorAgent
from .supervisor_agent import SupervisorAgent, AgentStatus, AgentInfo
from .workspace_config_agent import WorkspaceConfigAgent
from .tool_resource_agent import ToolResourceAgent, ToolInfo, ResourceUsage
from .state_sync_agent import StateSyncAgent, StateVersion, SyncStatus

__all__ = [
    # Base classes
    "BaseAgent",
    
    # Core agents
    "ContextMonitorAgent",
    "SupervisorAgent",
    "WorkspaceConfigAgent", 
    "ToolResourceAgent",
    "StateSyncAgent",
    
    # Supporting classes
    "AgentStatus",
    "AgentInfo",
    "ToolInfo", 
    "ResourceUsage",
    "StateVersion",
    "SyncStatus"
]
