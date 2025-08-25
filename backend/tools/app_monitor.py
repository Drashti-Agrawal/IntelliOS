"""
Application Monitor Tool for IntelliOS

This tool provides functionality to monitor running applications, their states,
resource usage, and window information.
"""

import os
import sys
import psutil
import asyncio
import platform
from typing import Dict, Any, Optional, List
from datetime import datetime

from .base_tool import BaseTool, ToolResult, ToolStatus

class AppMonitor(BaseTool):
    """
    Tool for monitoring running applications and their states.
    """
    
    def __init__(self):
        super().__init__(
            name="AppMonitor",
            description="Monitor running applications, their states, and resource usage",
            timeout=30.0
        )
        
        self.capabilities = [
            "list_running_apps",
            "get_app_info",
            "monitor_resource_usage",
            "get_window_info",
            "get_process_tree",
            "monitor_app_performance"
        ]
        
        self.requirements = ["psutil"]
        
        # Cache for performance
        self._app_cache = {}
        self._cache_timeout = 5.0  # seconds
    
    def _initialize(self):
        """Initialize tool-specific components."""
        self.system = platform.system().lower()
        self.logger.info(f"AppMonitor initialized for {self.system}")
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate monitor parameters."""
        # For list_running_apps, no parameters required
        if "action" not in kwargs:
            return True
        
        action = kwargs["action"]
        if action == "get_app_info" and "app_name" not in kwargs:
            return False
        elif action == "monitor_resource_usage" and "app_name" not in kwargs:
            return False
        
        return True
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the app monitor tool.
        
        Args:
            action: Action to perform (list_running_apps, get_app_info, monitor_resource_usage)
            app_name: Name of the application to monitor (for specific actions)
            include_system: Whether to include system processes (default: False)
            detailed: Whether to include detailed information (default: True)
            
        Returns:
            ToolResult with monitoring information
        """
        action = kwargs.get("action", "list_running_apps")
        app_name = kwargs.get("app_name")
        include_system = kwargs.get("include_system", False)
        detailed = kwargs.get("detailed", True)
        
        if action == "list_running_apps":
            return await self._list_running_apps(include_system, detailed)
        elif action == "get_app_info":
            return await self._get_app_info(app_name, detailed)
        elif action == "monitor_resource_usage":
            return await self._monitor_resource_usage(app_name)
        elif action == "get_window_info":
            return await self._get_window_info(app_name)
        elif action == "get_process_tree":
            return await self._get_process_tree(app_name)
        else:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=f"Unknown action: {action}"
            )
    
    async def _list_running_apps(self, include_system: bool = False, detailed: bool = True) -> ToolResult:
        """List all running applications."""
        try:
            apps = []
            system_processes = set()
            
            # Get system processes to filter out
            if not include_system:
                system_processes = self._get_system_processes()
            
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name']
                    
                    # Skip system processes if not requested
                    if not include_system and proc_name in system_processes:
                        continue
                    
                    app_info = {
                        "pid": proc_info['pid'],
                        "name": proc_name,
                        "exe": proc_info['exe'],
                        "cmdline": proc_info['cmdline'],
                        "cpu_percent": proc_info['cpu_percent'],
                        "memory_percent": proc_info['memory_percent']
                    }
                    
                    if detailed:
                        # Get additional information
                        try:
                            proc_obj = psutil.Process(proc_info['pid'])
                            app_info.update({
                                "create_time": datetime.fromtimestamp(proc_obj.create_time()).isoformat(),
                                "status": proc_obj.status(),
                                "num_threads": proc_obj.num_threads(),
                                "memory_info": {
                                    "rss": proc_obj.memory_info().rss,
                                    "vms": proc_obj.memory_info().vms
                                }
                            })
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    apps.append(app_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "apps": apps,
                    "total_count": len(apps),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=f"Failed to list running apps: {str(e)}"
            )
    
    async def _get_app_info(self, app_name: str, detailed: bool = True) -> ToolResult:
        """Get detailed information about a specific application."""
        try:
            matching_procs = []
            
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    if app_name.lower() in proc_name:
                        app_info = {
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "exe": proc_info['exe'],
                            "cmdline": proc_info['cmdline']
                        }
                        
                        if detailed:
                            try:
                                proc_obj = psutil.Process(proc_info['pid'])
                                app_info.update({
                                    "create_time": datetime.fromtimestamp(proc_obj.create_time()).isoformat(),
                                    "status": proc_obj.status(),
                                    "num_threads": proc_obj.num_threads(),
                                    "cpu_percent": proc_obj.cpu_percent(),
                                    "memory_percent": proc_obj.memory_percent(),
                                    "memory_info": {
                                        "rss": proc_obj.memory_info().rss,
                                        "vms": proc_obj.memory_info().vms
                                    },
                                    "connections": len(proc_obj.connections()),
                                    "open_files": len(proc_obj.open_files())
                                })
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                        
                        matching_procs.append(app_info)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not matching_procs:
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    data={
                        "app_name": app_name,
                        "processes": [],
                        "message": "No running processes found"
                    }
                )
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "app_name": app_name,
                    "processes": matching_procs,
                    "process_count": len(matching_procs),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=f"Failed to get app info: {str(e)}"
            )
    
    async def _monitor_resource_usage(self, app_name: str) -> ToolResult:
        """Monitor resource usage for a specific application."""
        try:
            total_cpu = 0.0
            total_memory = 0.0
            total_memory_rss = 0
            total_memory_vms = 0
            process_count = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    if app_name.lower() in proc_name:
                        process_count += 1
                        total_cpu += proc_info['cpu_percent'] or 0.0
                        total_memory += proc_info['memory_percent'] or 0.0
                        
                        # Get detailed memory info
                        try:
                            proc_obj = psutil.Process(proc_info['pid'])
                            mem_info = proc_obj.memory_info()
                            total_memory_rss += mem_info.rss
                            total_memory_vms += mem_info.vms
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if process_count == 0:
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    data={
                        "app_name": app_name,
                        "message": "No running processes found",
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            # Get system-wide info for comparison
            system_cpu = psutil.cpu_percent(interval=1)
            system_memory = psutil.virtual_memory()
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "app_name": app_name,
                    "process_count": process_count,
                    "resource_usage": {
                        "cpu_percent": total_cpu,
                        "memory_percent": total_memory,
                        "memory_rss_bytes": total_memory_rss,
                        "memory_vms_bytes": total_memory_vms,
                        "memory_rss_mb": total_memory_rss / (1024 * 1024),
                        "memory_vms_mb": total_memory_vms / (1024 * 1024)
                    },
                    "system_info": {
                        "system_cpu_percent": system_cpu,
                        "system_memory_percent": system_memory.percent,
                        "system_memory_available": system_memory.available
                    },
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=f"Failed to monitor resource usage: {str(e)}"
            )
    
    async def _get_window_info(self, app_name: str) -> ToolResult:
        """Get window information for an application."""
        try:
            # This is a placeholder for window management
            # In a full implementation, this would use platform-specific APIs
            # like win32gui on Windows or X11 on Linux
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "app_name": app_name,
                    "windows": [],
                    "message": "Window information not yet implemented",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=f"Failed to get window info: {str(e)}"
            )
    
    async def _get_process_tree(self, app_name: str) -> ToolResult:
        """Get the process tree for an application."""
        try:
            process_trees = []
            
            for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower()
                    
                    if app_name.lower() in proc_name:
                        tree = self._build_process_tree(proc_info['pid'])
                        process_trees.append(tree)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "app_name": app_name,
                    "process_trees": process_trees,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=f"Failed to get process tree: {str(e)}"
            )
    
    def _build_process_tree(self, pid: int) -> Dict[str, Any]:
        """Build a process tree starting from a given PID."""
        try:
            proc = psutil.Process(pid)
            children = []
            
            for child in proc.children(recursive=True):
                try:
                    children.append({
                        "pid": child.pid,
                        "name": child.name(),
                        "status": child.status()
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "pid": pid,
                "name": proc.name(),
                "status": proc.status(),
                "children": children
            }
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {"pid": pid, "error": "Process not accessible"}
    
    def _get_system_processes(self) -> set:
        """Get a set of system process names to filter out."""
        system_processes = {
            # Windows system processes
            "svchost.exe", "lsass.exe", "winlogon.exe", "csrss.exe", "wininit.exe",
            "services.exe", "spoolsv.exe", "explorer.exe", "taskmgr.exe",
            
            # Common system processes across platforms
            "system", "init", "systemd", "kthreadd", "ksoftirqd", "migration",
            "watchdog", "kworker", "events", "kblockd", "ata_sff", "khubd",
            "scsi_eh", "usb-storage", "usbhid", "hid-generic", "hiddev",
            "input", "sound", "snd", "snd-pcm", "snd-mixer", "snd-timer",
            "snd-page-alloc", "snd-hwdep", "snd-rawmidi", "snd-seq", "snd-seq-device",
            "snd-timer", "snd-page-alloc", "snd-hwdep", "snd-rawmidi", "snd-seq",
            "snd-seq-device", "snd-timer", "snd-page-alloc", "snd-hwdep", "snd-rawmidi",
            "snd-seq", "snd-seq-device", "snd-timer", "snd-page-alloc", "snd-hwdep",
            "snd-rawmidi", "snd-seq", "snd-seq-device", "snd-timer", "snd-page-alloc",
            "snd-hwdep", "snd-rawmidi", "snd-seq", "snd-seq-device", "snd-timer",
            "snd-page-alloc", "snd-hwdep", "snd-rawmidi", "snd-seq", "snd-seq-device"
        }
        
        return system_processes
