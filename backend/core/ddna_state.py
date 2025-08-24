"""
Digital DNA (dDNA) State Management for IntelliOS

This module defines the core state object that represents the user's current
context, workspace state, and digital environment. It serves as the central
data structure passed between agents in the LangGraph workflow.
"""

from typing import TypedDict, List, Dict, Optional, Any, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import json


class DeviceContext(BaseModel):
    """Represents the current device and system context."""
    device_id: str = Field(..., description="Unique identifier for the device")
    device_type: Literal["desktop", "laptop", "tablet", "mobile"] = Field(..., description="Type of device")
    os_type: Literal["windows", "macos", "linux"] = Field(..., description="Operating system")
    os_version: str = Field(..., description="OS version string")
    screen_resolution: Dict[str, int] = Field(..., description="Screen resolution {width, height}")
    available_memory: int = Field(..., description="Available RAM in MB")
    cpu_usage: float = Field(..., description="Current CPU usage percentage")
    network_status: Literal["connected", "disconnected", "limited"] = Field(..., description="Network connectivity status")
    battery_level: Optional[float] = Field(None, description="Battery level percentage (if applicable)")
    is_plugged_in: Optional[bool] = Field(None, description="Whether device is plugged in")


class ApplicationState(BaseModel):
    """Represents the state of a running application."""
    name: str = Field(..., description="Application name")
    process_id: int = Field(..., description="Process ID")
    window_title: Optional[str] = Field(None, description="Current window title")
    is_focused: bool = Field(False, description="Whether this app has focus")
    focus_time: int = Field(0, description="Time spent focused in seconds")
    memory_usage: int = Field(0, description="Memory usage in MB")
    cpu_usage: float = Field(0.0, description="CPU usage percentage")
    file_path: Optional[str] = Field(None, description="Path to the application executable")
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BrowserState(BaseModel):
    """Represents browser state including tabs and sessions."""
    browser_name: str = Field(..., description="Browser name (chrome, firefox, edge, etc.)")
    tabs: List[Dict[str, Any]] = Field(default_factory=list, description="List of open tabs")
    active_tab_index: int = Field(0, description="Index of the currently active tab")
    bookmarks: List[Dict[str, Any]] = Field(default_factory=list, description="Recent bookmarks")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Recent browsing history")


class TerminalSession(BaseModel):
    """Represents a terminal/shell session."""
    session_id: str = Field(..., description="Unique session identifier")
    terminal_type: str = Field(..., description="Terminal type (cmd, powershell, bash, etc.)")
    current_directory: str = Field(..., description="Current working directory")
    command_history: List[str] = Field(default_factory=list, description="Recent commands")
    active_processes: List[Dict[str, Any]] = Field(default_factory=list, description="Running processes")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Environment variables")


class FileContext(BaseModel):
    """Represents file system context and recent file operations."""
    recent_files: List[Dict[str, Any]] = Field(default_factory=list, description="Recently accessed files")
    open_files: List[Dict[str, Any]] = Field(default_factory=list, description="Currently open files")
    clipboard_content: Optional[str] = Field(None, description="Current clipboard content")
    downloads_folder: str = Field(..., description="Path to downloads folder")
    documents_folder: str = Field(..., description="Path to documents folder")


class UserPreferences(BaseModel):
    """Represents user preferences and settings."""
    theme: Literal["light", "dark", "auto"] = Field("auto", description="UI theme preference")
    language: str = Field("en", description="Preferred language")
    timezone: str = Field(..., description="User's timezone")
    notification_settings: Dict[str, bool] = Field(default_factory=dict, description="Notification preferences")
    workspace_layouts: Dict[str, Any] = Field(default_factory=dict, description="Saved workspace layouts")
    automation_preferences: Dict[str, bool] = Field(default_factory=dict, description="Automation preferences")


class TaskIntent(BaseModel):
    """Represents the user's current task or intent."""
    primary_intent: str = Field(..., description="Primary task intent (e.g., 'coding', 'meeting', 'research')")
    secondary_intents: List[str] = Field(default_factory=list, description="Secondary or related intents")
    project_context: Optional[str] = Field(None, description="Current project or context")
    urgency_level: Literal["low", "medium", "high", "critical"] = Field("medium", description="Task urgency")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in minutes")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")


class ExecutionPlan(BaseModel):
    """Represents a plan for workspace configuration or automation."""
    plan_id: str = Field(..., description="Unique plan identifier")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="List of execution steps")
    status: Literal["pending", "in_progress", "completed", "failed"] = Field("pending", description="Plan status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    priority: Literal["low", "medium", "high"] = Field("medium", description="Plan priority")


class WorkspaceContext(BaseModel):
    """Represents workspace configuration and context."""
    workspace_type: str = Field(..., description="Type of workspace (python, javascript, etc.)")
    workspace_path: str = Field(..., description="Path to the workspace")
    project_structure: Dict[str, Any] = Field(default_factory=dict, description="Project structure information")
    dependencies: Dict[str, List[str]] = Field(default_factory=dict, description="Project dependencies")
    ide_configuration: Dict[str, Any] = Field(default_factory=dict, description="IDE configuration")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")


class SystemResources(BaseModel):
    """Represents system resource usage and available tools."""
    cpu_usage: float = Field(..., description="Current CPU usage percentage")
    memory_usage: float = Field(..., description="Current memory usage percentage")
    memory_available: int = Field(..., description="Available memory in bytes")
    disk_usage: float = Field(..., description="Current disk usage percentage")
    disk_available: int = Field(..., description="Available disk space in bytes")
    network_connections: int = Field(..., description="Number of network connections")
    available_tools: List[str] = Field(default_factory=list, description="List of available tools")
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")


class ExecutionLog(BaseModel):
    """Represents execution history and logs."""
    entries: List[Dict[str, Any]] = Field(default_factory=list, description="Execution log entries")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Error logs")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="Warning logs")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")


class DigitalDNAState(BaseModel):
    """
    Digital DNA State - The central state object for the IntelliOS agentic system.
    
    This represents the complete real-time context of the user's digital environment,
    including device state, applications, workspace context, and user intent.
    """
    
    # Core identifiers
    user_id: str = Field(..., description="Unique user identifier")
    session_id: str = Field(..., description="Current session identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    
    # Device and system context
    device_context: DeviceContext = Field(..., description="Current device context")
    
    # Application and workspace state
    active_applications: List[ApplicationState] = Field(default_factory=list, description="Currently running applications")
    browser_state: List[BrowserState] = Field(default_factory=list, description="Browser states")
    terminal_sessions: List[TerminalSession] = Field(default_factory=list, description="Active terminal sessions")
    
    # File and content context
    file_context: FileContext = Field(..., description="File system context")
    
    # User preferences and settings
    user_preferences: UserPreferences = Field(..., description="User preferences")
    
    # Task and intent information
    current_task_intent: Optional[TaskIntent] = Field(None, description="Current task intent")
    
    # Execution and automation
    execution_plan: Optional[ExecutionPlan] = Field(None, description="Current execution plan")
    execution_log: ExecutionLog = Field(default_factory=ExecutionLog, description="Execution history")
    
    # Workspace and system context
    workspace_context: Optional[WorkspaceContext] = Field(None, description="Workspace configuration and context")
    system_resources: Optional[SystemResources] = Field(None, description="System resource usage and available tools")
    
    # Agent communication
    agent_messages: List[Dict[str, Any]] = Field(default_factory=list, description="Inter-agent messages")
    feedback: Optional[str] = Field(None, description="User feedback or notes")
    
    # Metadata
    version: str = Field("1.0.0", description="dDNA state version")
    source: str = Field("intellios", description="Source system")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


# Convenience functions for state management
def create_initial_state(user_id: str = "default_user", device_context: DeviceContext = None, file_context: FileContext = None) -> DigitalDNAState:
    """Create an initial dDNA state with basic information."""
    session_id = f"{user_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    
    # Create default device context if not provided
    if device_context is None:
        import platform
        import psutil
        
        device_context = DeviceContext(
            device_id=f"device_{platform.node()}",
            device_type="desktop",
            os_type=platform.system().lower(),
            os_version=platform.version(),
            screen_resolution={"width": 1920, "height": 1080},
            available_memory=psutil.virtual_memory().available // (1024 * 1024),  # MB
            cpu_usage=psutil.cpu_percent(),
            network_status="connected"
        )
    
    # Create default file context if not provided
    if file_context is None:
        import os
        file_context = FileContext(
            downloads_folder=os.path.expanduser("~/Downloads"),
            documents_folder=os.path.expanduser("~/Documents")
        )
    
    return DigitalDNAState(
        user_id=user_id,
        session_id=session_id,
        device_context=device_context,
        file_context=file_context,
        user_preferences=UserPreferences(
            timezone=str(datetime.now().astimezone().tzinfo)
        )
    )


def update_state_timestamp(state: DigitalDNAState) -> DigitalDNAState:
    """Update the timestamp of the state."""
    state.timestamp = datetime.now(timezone.utc)
    return state


def add_agent_message(state: DigitalDNAState, agent_name: str, message: str, message_type: str = "info") -> DigitalDNAState:
    """Add a message to the agent communication log."""
    state.agent_messages.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent_name,
        "message": message,
        "type": message_type
    })
    return state


def get_state_summary(state: DigitalDNAState) -> Dict[str, Any]:
    """Get a summary of the current state for logging or debugging."""
    return {
        "user_id": state.user_id,
        "session_id": state.session_id,
        "timestamp": state.timestamp.isoformat(),
        "device_type": state.device_context.device_type,
        "os_type": state.device_context.os_type,
        "active_apps_count": len(state.active_applications),
        "browser_count": len(state.browser_state),
        "terminal_sessions_count": len(state.terminal_sessions),
        "current_task": state.current_task_intent.primary_intent if state.current_task_intent else None,
        "execution_plan_status": state.execution_plan.status if state.execution_plan else None
    }


# Export the main state class and key components
__all__ = [
    "DigitalDNAState",
    "DeviceContext", 
    "ApplicationState",
    "BrowserState",
    "TerminalSession",
    "FileContext",
    "UserPreferences",
    "TaskIntent",
    "ExecutionPlan",
    "WorkspaceContext",
    "SystemResources",
    "ExecutionLog",
    "create_initial_state",
    "update_state_timestamp",
    "add_agent_message",
    "get_state_summary"
]
