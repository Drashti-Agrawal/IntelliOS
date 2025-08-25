"""
Application Launcher Tool for IntelliOS

This tool provides functionality to launch applications with specific parameters,
monitor their startup, and manage application instances.
"""

import os
import sys
import subprocess
import asyncio
import psutil
import platform
from typing import Dict, Any, Optional, List
from pathlib import Path

from .base_tool import BaseTool, ToolResult, ToolStatus

class AppLauncher(BaseTool):
    """
    Tool for launching applications with specific parameters and monitoring.
    """
    
    def __init__(self):
        super().__init__(
            name="AppLauncher",
            description="Launch applications with specific parameters and monitor startup",
            timeout=60.0
        )
        
        self.capabilities = [
            "launch_application",
            "launch_with_parameters", 
            "launch_with_working_directory",
            "monitor_startup",
            "check_if_running",
            "kill_application"
        ]
        
        self.requirements = ["psutil"]
        
        # Common application paths
        self.common_apps = self._get_common_apps()
    
    def _initialize(self):
        """Initialize tool-specific components."""
        self.system = platform.system().lower()
        self.logger.info(f"AppLauncher initialized for {self.system}")
    
    def _get_common_apps(self) -> Dict[str, Dict[str, str]]:
        """Get common application paths for different operating systems."""
        if self.system == "windows":
            return {
                "notepad": {
                    "path": "notepad.exe",
                    "type": "system"
                },
                "calculator": {
                    "path": "calc.exe", 
                    "type": "system"
                },
                "chrome": {
                    "path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    "type": "installed"
                },
                "vscode": {
                    "path": r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                    "type": "installed"
                },
                "python": {
                    "path": "python.exe",
                    "type": "system"
                }
            }
        elif self.system == "darwin":  # macOS
            return {
                "textedit": {
                    "path": "/Applications/TextEdit.app",
                    "type": "system"
                },
                "calculator": {
                    "path": "/Applications/Calculator.app",
                    "type": "system"
                },
                "chrome": {
                    "path": "/Applications/Google Chrome.app",
                    "type": "installed"
                },
                "vscode": {
                    "path": "/Applications/Visual Studio Code.app",
                    "type": "installed"
                },
                "python": {
                    "path": "python3",
                    "type": "system"
                }
            }
        else:  # Linux
            return {
                "gedit": {
                    "path": "gedit",
                    "type": "system"
                },
                "calculator": {
                    "path": "gnome-calculator",
                    "type": "system"
                },
                "chrome": {
                    "path": "google-chrome",
                    "type": "installed"
                },
                "vscode": {
                    "path": "code",
                    "type": "installed"
                },
                "python": {
                    "path": "python3",
                    "type": "system"
                }
            }
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate launch parameters."""
        required_params = ["app_name"]
        for param in required_params:
            if param not in kwargs:
                return False
        
        app_name = kwargs["app_name"]
        if not isinstance(app_name, str) or not app_name.strip():
            return False
        
        return True
    
    def _find_app_path(self, app_name: str) -> Optional[str]:
        """Find the path to an application."""
        # Check if it's a common app
        if app_name.lower() in self.common_apps:
            app_info = self.common_apps[app_name.lower()]
            path = app_info["path"]
            
            # Handle user-specific paths
            if "{user}" in path:
                path = path.format(user=os.getenv("USERNAME", os.getenv("USER", "")))
            
            # Check if path exists
            if app_info["type"] == "system":
                return path
            elif os.path.exists(path):
                return path
        
        # Check if it's a full path
        if os.path.exists(app_name):
            return app_name
        
        # Check if it's in PATH
        try:
            result = subprocess.run(
                ["which", app_name] if self.system != "windows" else ["where", app_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None
    
    def _is_app_running(self, app_name: str) -> bool:
        """Check if an application is already running."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name.lower() in proc_name:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.warning(f"Error checking if app is running: {e}")
        
        return False
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the app launcher tool.
        
        Args:
            app_name: Name or path of the application to launch
            parameters: Optional parameters to pass to the application
            working_directory: Optional working directory
            wait_for_startup: Whether to wait for the app to start (default: True)
            kill_existing: Whether to kill existing instances (default: False)
            
        Returns:
            ToolResult with launch information
        """
        app_name = kwargs.get("app_name")
        parameters = kwargs.get("parameters", [])
        working_directory = kwargs.get("working_directory")
        wait_for_startup = kwargs.get("wait_for_startup", True)
        kill_existing = kwargs.get("kill_existing", False)
        
        # Find the application path
        app_path = self._find_app_path(app_name)
        if not app_path:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=f"Application '{app_name}' not found"
            )
        
        # Check if app is already running
        is_running = self._is_app_running(app_name)
        if is_running and kill_existing:
            self.logger.info(f"Killing existing instance of {app_name}")
            # TODO: Implement kill functionality
        elif is_running and not kill_existing:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                data={
                    "app_name": app_name,
                    "app_path": app_path,
                    "status": "already_running",
                    "pid": None
                },
                metadata={"message": "Application is already running"}
            )
        
        # Prepare launch command
        cmd = [app_path]
        if parameters:
            if isinstance(parameters, str):
                cmd.extend(parameters.split())
            elif isinstance(parameters, list):
                cmd.extend(parameters)
        
        # Launch the application
        try:
            self.logger.info(f"Launching {app_name} with command: {' '.join(cmd)}")
            
            # Use subprocess.Popen for non-blocking launch
            process = subprocess.Popen(
                cmd,
                cwd=working_directory,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup if requested
            if wait_for_startup:
                await asyncio.sleep(2)  # Give app time to start
                
                # Check if process is still running
                if process.poll() is None:
                    # Process is running
                    result_data = {
                        "app_name": app_name,
                        "app_path": app_path,
                        "status": "started",
                        "pid": process.pid,
                        "command": ' '.join(cmd)
                    }
                    
                    if working_directory:
                        result_data["working_directory"] = working_directory
                    
                    return ToolResult(
                        status=ToolStatus.SUCCESS,
                        data=result_data
                    )
                else:
                    # Process failed to start
                    stdout, stderr = process.communicate()
                    return ToolResult(
                        status=ToolStatus.FAILED,
                        error=f"Application failed to start. Exit code: {process.returncode}",
                        data={
                            "stdout": stdout,
                            "stderr": stderr,
                            "exit_code": process.returncode
                        }
                    )
            else:
                # Don't wait, return immediately
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    data={
                        "app_name": app_name,
                        "app_path": app_path,
                        "status": "launching",
                        "pid": process.pid,
                        "command": ' '.join(cmd)
                    }
                )
                
        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=f"Failed to launch application: {str(e)}"
            )
    
    async def kill_application(self, app_name: str) -> ToolResult:
        """
        Kill a running application.
        
        Args:
            app_name: Name of the application to kill
            
        Returns:
            ToolResult with kill information
        """
        try:
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if app_name.lower() in proc_name:
                        proc.kill()
                        killed_count += 1
                        self.logger.info(f"Killed process {proc.info['pid']} ({proc_name})")
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    self.logger.warning(f"Could not kill process: {e}")
            
            if killed_count > 0:
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    data={
                        "app_name": app_name,
                        "killed_count": killed_count,
                        "status": "killed"
                    }
                )
            else:
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    data={
                        "app_name": app_name,
                        "killed_count": 0,
                        "status": "not_found"
                    },
                    metadata={"message": "No running instances found"}
                )
                
        except Exception as e:
            return ToolResult(
                status=ToolStatus.FAILED,
                error=f"Failed to kill application: {str(e)}"
            )
    
    def get_available_apps(self) -> List[str]:
        """Get list of available applications."""
        return list(self.common_apps.keys())
