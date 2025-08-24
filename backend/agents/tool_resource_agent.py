"""
Tool & Resource Agent - Manages tool discovery and resource allocation.

This agent is responsible for:
- Discovering available tools and capabilities
- Managing resource allocation and monitoring
- Coordinating tool execution and integration
- Monitoring system performance and resource usage
"""

import os
import psutil
import logging
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from .base_agent import BaseAgent
from core.ddna_state import DigitalDNAState, SystemResources


@dataclass
class ToolInfo:
    """Information about a discovered tool."""
    name: str
    path: str
    version: Optional[str] = None
    description: Optional[str] = None
    category: str = "general"
    is_available: bool = True


@dataclass
class ResourceUsage:
    """Current resource usage information."""
    cpu_percent: float
    memory_percent: float
    memory_available: int  # bytes
    disk_usage_percent: float
    disk_available: int  # bytes
    network_connections: int
    timestamp: datetime


class ToolResourceAgent(BaseAgent):
    """
    Tool & Resource Agent - Manages tools and system resources.
    
    Responsibilities:
    - Discover and catalog available tools
    - Monitor system resource usage
    - Manage resource allocation
    - Coordinate tool execution
    - Monitor system performance
    """
    
    def __init__(self, name: str = "ToolResourceAgent"):
        super().__init__(name, "Manages tool discovery and resource allocation")
        self.discovered_tools: Dict[str, ToolInfo] = {}
        self.resource_history: List[ResourceUsage] = []
        self.max_history_size = 100
        
        # Common tool categories
        self.tool_categories = {
            "development": ["git", "python", "node", "npm", "pip", "conda"],
            "system": ["ps", "top", "df", "du", "ls", "cat"],
            "network": ["curl", "wget", "ping", "nslookup", "netstat"],
            "build": ["make", "cmake", "maven", "gradle", "ant"],
            "database": ["sqlite3", "mysql", "psql", "mongodb"],
            "monitoring": ["htop", "iotop", "nethogs", "iftop"]
        }
        
    def _discover_tools(self) -> Dict[str, ToolInfo]:
        """
        Discover available tools on the system.
        
        Returns:
            Dictionary of discovered tools
        """
        tools = {}
        
        # Check PATH for common tools
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        
        for category, tool_names in self.tool_categories.items():
            for tool_name in tool_names:
                tool_path = self._find_tool_in_path(tool_name, path_dirs)
                if tool_path:
                    version = self._get_tool_version(tool_name, tool_path)
                    tools[tool_name] = ToolInfo(
                        name=tool_name,
                        path=tool_path,
                        version=version,
                        category=category,
                        description=self._get_tool_description(tool_name)
                    )
                    
        # Check for Python packages
        python_tools = self._discover_python_tools()
        tools.update(python_tools)
        
        # Check for Node.js packages
        node_tools = self._discover_node_tools()
        tools.update(node_tools)
        
        return tools
        
    def _find_tool_in_path(self, tool_name: str, path_dirs: List[str]) -> Optional[str]:
        """
        Find a tool in the system PATH.
        
        Args:
            tool_name: Name of the tool to find
            path_dirs: List of PATH directories
            
        Returns:
            Full path to the tool if found, None otherwise
        """
        for path_dir in path_dirs:
            tool_path = Path(path_dir) / tool_name
            if tool_path.exists() and os.access(tool_path, os.X_OK):
                return str(tool_path)
                
        return None
        
    def _get_tool_version(self, tool_name: str, tool_path: str) -> Optional[str]:
        """
        Get version information for a tool.
        
        Args:
            tool_name: Name of the tool
            tool_path: Path to the tool
            
        Returns:
            Version string if available, None otherwise
        """
        try:
            # Common version flags
            version_flags = ["--version", "-v", "-V", "version"]
            
            for flag in version_flags:
                try:
                    result = subprocess.run(
                        [tool_path, flag],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        # Extract version from output
                        output = result.stdout.strip()
                        if output:
                            return output.split()[0] if output.split() else output
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Could not get version for {tool_name}: {e}")
            
        return None
        
    def _get_tool_description(self, tool_name: str) -> str:
        """
        Get a description for a tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool description
        """
        descriptions = {
            "git": "Distributed version control system",
            "python": "Python programming language interpreter",
            "node": "Node.js JavaScript runtime",
            "npm": "Node.js package manager",
            "pip": "Python package installer",
            "conda": "Package and environment manager",
            "ps": "Process status utility",
            "top": "System monitoring tool",
            "df": "Disk space usage utility",
            "du": "Disk usage utility",
            "curl": "Command line tool for transferring data",
            "wget": "Web download utility",
            "make": "Build automation tool",
            "cmake": "Cross-platform build system",
            "sqlite3": "SQLite database command line tool"
        }
        
        return descriptions.get(tool_name, f"Tool: {tool_name}")
        
    def _discover_python_tools(self) -> Dict[str, ToolInfo]:
        """
        Discover Python packages and tools.
        
        Returns:
            Dictionary of Python tools
        """
        python_tools = {}
        
        try:
            # Check for pip
            result = subprocess.run(
                ["pip", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[2:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            package_name = parts[0]
                            version = parts[1]
                            
                            # Only include relevant packages
                            if any(keyword in package_name.lower() for keyword in 
                                  ['langchain', 'fastapi', 'pydantic', 'chromadb', 'psutil']):
                                python_tools[f"python:{package_name}"] = ToolInfo(
                                    name=package_name,
                                    path="pip",
                                    version=version,
                                    category="python_package",
                                    description=f"Python package: {package_name}"
                                )
                                
        except Exception as e:
            self.logger.debug(f"Could not discover Python tools: {e}")
            
        return python_tools
        
    def _discover_node_tools(self) -> Dict[str, ToolInfo]:
        """
        Discover Node.js packages and tools.
        
        Returns:
            Dictionary of Node.js tools
        """
        node_tools = {}
        
        try:
            # Check for npm
            result = subprocess.run(
                ["npm", "list", "--depth=0"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip() and not line.startswith('├──') and not line.startswith('└──'):
                        # Parse npm list output
                        if '@' in line:
                            package_name = line.split('@')[0].strip()
                            version = line.split('@')[1].split()[0]
                            
                            node_tools[f"node:{package_name}"] = ToolInfo(
                                name=package_name,
                                path="npm",
                                version=version,
                                category="node_package",
                                description=f"Node.js package: {package_name}"
                            )
                            
        except Exception as e:
            self.logger.debug(f"Could not discover Node.js tools: {e}")
            
        return node_tools
        
    def _get_system_resources(self) -> ResourceUsage:
        """
        Get current system resource usage.
        
        Returns:
            Current resource usage information
        """
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available = memory.available
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent
        disk_available = disk.free
        
        # Network connections
        network_connections = len(psutil.net_connections())
        
        return ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available=memory_available,
            disk_usage_percent=disk_usage_percent,
            disk_available=disk_available,
            network_connections=network_connections,
            timestamp=datetime.now()
        )
        
    def _update_resource_history(self, usage: ResourceUsage) -> None:
        """
        Update resource usage history.
        
        Args:
            usage: Current resource usage
        """
        self.resource_history.append(usage)
        
        # Keep only the most recent entries
        if len(self.resource_history) > self.max_history_size:
            self.resource_history = self.resource_history[-self.max_history_size:]
            
    async def process(self, state: DigitalDNAState) -> DigitalDNAState:
        """
        Main processing method - discovers tools and monitors resources.
        
        Args:
            state: Current dDNA state
            
        Returns:
            Updated dDNA state with tool and resource information
        """
        self.logger.info("Starting tool discovery and resource monitoring")
        
        # Discover tools
        discovered_tools = self._discover_tools()
        self.discovered_tools.update(discovered_tools)
        self.logger.info(f"Discovered {len(discovered_tools)} tools")
        
        # Get current resource usage
        current_resources = self._get_system_resources()
        self._update_resource_history(current_resources)
        
        # Create system resources object
        system_resources = SystemResources(
            cpu_usage=current_resources.cpu_percent,
            memory_usage=current_resources.memory_percent,
            memory_available=current_resources.memory_available,
            disk_usage=current_resources.disk_usage_percent,
            disk_available=current_resources.disk_available,
            network_connections=current_resources.network_connections,
            available_tools=list(self.discovered_tools.keys()),
            last_updated=datetime.now()
        )
        
        # Update state
        state.system_resources = system_resources
        
        # Add agent message
        from core.ddna_state import add_agent_message
        state = add_agent_message(
            state,
            self.agent_name,
            f"Discovered {len(discovered_tools)} tools, CPU: {current_resources.cpu_percent:.1f}%, Memory: {current_resources.memory_percent:.1f}%",
            "tool_discovery"
        )
        
        self.logger.info("Tool discovery and resource monitoring completed")
        return state
        
    def get_tool_info(self, tool_name: str) -> Optional[ToolInfo]:
        """
        Get information about a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool information if found, None otherwise
        """
        return self.discovered_tools.get(tool_name)
        
    def get_tools_by_category(self, category: str) -> List[ToolInfo]:
        """
        Get all tools in a specific category.
        
        Args:
            category: Tool category
            
        Returns:
            List of tools in the category
        """
        return [
            tool for tool in self.discovered_tools.values()
            if tool.category == category
        ]
        
    def get_resource_history(self, minutes: int = 60) -> List[ResourceUsage]:
        """
        Get resource usage history for the specified time period.
        
        Args:
            minutes: Number of minutes to look back
            
        Returns:
            List of resource usage entries
        """
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        return [
            usage for usage in self.resource_history
            if usage.timestamp.timestamp() > cutoff_time
        ]
        
    def get_resource_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current resource usage.
        
        Returns:
            Dictionary containing resource summary
        """
        if not self.resource_history:
            return {}
            
        latest = self.resource_history[-1]
        
        return {
            "cpu_percent": latest.cpu_percent,
            "memory_percent": latest.memory_percent,
            "memory_available_gb": round(latest.memory_available / (1024**3), 2),
            "disk_usage_percent": latest.disk_usage_percent,
            "disk_available_gb": round(latest.disk_available / (1024**3), 2),
            "network_connections": latest.network_connections,
            "total_tools": len(self.discovered_tools),
            "timestamp": latest.timestamp.isoformat()
        }
        
    def execute_tool(self, tool_name: str, args: List[str] = None) -> Tuple[bool, str]:
        """
        Execute a tool with the given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments to pass to the tool
            
        Returns:
            Tuple of (success, output)
        """
        if tool_name not in self.discovered_tools:
            return False, f"Tool '{tool_name}' not found"
            
        tool_info = self.discovered_tools[tool_name]
        
        if not tool_info.is_available:
            return False, f"Tool '{tool_name}' is not available"
            
        try:
            cmd = [tool_info.path] + (args or [])
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            return False, "Tool execution timed out"
        except Exception as e:
            return False, str(e)
