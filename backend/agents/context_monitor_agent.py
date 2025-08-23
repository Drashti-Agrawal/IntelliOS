"""
Context Monitor Agent for IntelliOS

This agent is responsible for monitoring and gathering real-time information about:
- Device context (CPU, memory, network, etc.)
- Running applications and their states
- Browser sessions and tabs
- Terminal sessions
- File system activity
- User input patterns
"""

import asyncio
import logging
import psutil
import platform
import socket
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import os

from .base_agent import BaseAgent
from core.ddna_state import (
    DigitalDNAState, 
    DeviceContext, 
    ApplicationState, 
    BrowserState,
    TerminalSession,
    FileContext,
    add_agent_message
)


class ContextMonitorAgent(BaseAgent):
    """
    Context Monitor Agent - Gathers real-time system and user context.
    
    This agent monitors the user's digital environment and updates the dDNA state
    with current information about device status, applications, and user activity.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Context Monitor Agent."""
        super().__init__(
            agent_name="ContextMonitor",
            agent_description="Monitors and gathers real-time system context, application states, and user activity",
            config=config or {}
        )
        
        # Configuration
        self.monitoring_interval = self.config.get("monitoring_interval", 5.0)  # seconds
        self.max_apps_to_track = self.config.get("max_apps_to_track", 20)
        self.max_browser_tabs = self.config.get("max_browser_tabs", 50)
        
        # Initialize monitoring state
        self.last_device_context = None
        self.last_applications = []
        
        self.logger.info("Context Monitor Agent initialized")
    
    async def process(self, state: DigitalDNAState, **kwargs) -> DigitalDNAState:
        """
        Process the current state and gather updated context information.
        
        Args:
            state: Current Digital DNA state
            **kwargs: Additional arguments
            
        Returns:
            Updated Digital DNA state with fresh context information
        """
        self.logger.debug("Starting context monitoring process")
        
        try:
            # Gather device context
            device_context = await self._gather_device_context()
            state.device_context = device_context
            
            # Gather application states
            applications = await self._gather_application_states()
            state.active_applications = applications
            
            # Gather browser states (if available)
            browser_states = await self._gather_browser_states()
            state.browser_state = browser_states
            
            # Gather terminal sessions (if available)
            terminal_sessions = await self._gather_terminal_sessions()
            state.terminal_sessions = terminal_sessions
            
            # Update file context
            file_context = await self._gather_file_context()
            state.file_context = file_context
            
            # Add monitoring message
            state = add_agent_message(
                state,
                self.agent_name,
                f"Updated context: {len(applications)} apps, {len(browser_states)} browsers, {len(terminal_sessions)} terminals",
                "info"
            )
            
            self.logger.debug(f"Context monitoring completed: {len(applications)} applications tracked")
            return state
            
        except Exception as e:
            self.logger.error(f"Error in context monitoring: {str(e)}")
            state = add_agent_message(
                state,
                self.agent_name,
                f"Context monitoring error: {str(e)}",
                "error"
            )
            raise
    
    async def _gather_device_context(self) -> DeviceContext:
        """Gather current device and system context."""
        try:
            # Get system information
            system_info = platform.uname()
            
            # Get memory information
            memory = psutil.virtual_memory()
            
            # Get CPU information
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Get network status
            network_status = self._get_network_status()
            
            # Get battery information (if available)
            battery_info = self._get_battery_info()
            
            # Get screen resolution (Windows-specific for now)
            screen_resolution = self._get_screen_resolution()
            
            # Determine device type
            device_type = self._determine_device_type()
            
            # Determine OS type
            os_type = self._determine_os_type(system_info.system)
            
            device_context = DeviceContext(
                device_id=socket.gethostname(),
                device_type=device_type,
                os_type=os_type,
                os_version=system_info.release,
                screen_resolution=screen_resolution,
                available_memory=int(memory.available / (1024 * 1024)),  # Convert to MB
                cpu_usage=cpu_percent,
                network_status=network_status,
                battery_level=battery_info.get("level"),
                is_plugged_in=battery_info.get("plugged_in")
            )
            
            return device_context
            
        except Exception as e:
            self.logger.error(f"Error gathering device context: {str(e)}")
            # Return a basic device context with available information
            return DeviceContext(
                device_id=socket.gethostname(),
                device_type="desktop",
                os_type="windows",
                os_version="unknown",
                screen_resolution={"width": 1920, "height": 1080},
                available_memory=0,
                cpu_usage=0.0,
                network_status="connected"
            )
    
    async def _gather_application_states(self) -> List[ApplicationState]:
        """Gather information about currently running applications."""
        try:
            applications = []
            
            # Get all running processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'create_time']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage and take top processes
            processes.sort(key=lambda x: x['memory_info'].rss if x['memory_info'] else 0, reverse=True)
            top_processes = processes[:self.max_apps_to_track]
            
            for proc_info in top_processes:
                try:
                    # Get additional process information
                    proc = psutil.Process(proc_info['pid'])
                    
                    # Get window title (Windows-specific)
                    window_title = self._get_window_title(proc_info['pid'])
                    
                    # Determine if process has focus (simplified)
                    is_focused = self._is_process_focused(proc_info['pid'])
                    
                    app_state = ApplicationState(
                        name=proc_info['name'],
                        process_id=proc_info['pid'],
                        window_title=window_title,
                        is_focused=is_focused,
                        focus_time=0,  # Would need to track over time
                        memory_usage=int(proc_info['memory_info'].rss / (1024 * 1024)) if proc_info['memory_info'] else 0,
                        cpu_usage=proc_info['cpu_percent'] or 0.0,
                        file_path=proc.exe() if hasattr(proc, 'exe') else None,
                        start_time=datetime.fromtimestamp(proc_info['create_time'], tz=timezone.utc)
                    )
                    
                    applications.append(app_state)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return applications
            
        except Exception as e:
            self.logger.error(f"Error gathering application states: {str(e)}")
            return []
    
    async def _gather_browser_states(self) -> List[BrowserState]:
        """Gather information about browser sessions and tabs."""
        try:
            browser_states = []
            
            # For now, we'll create a basic browser state
            # In a full implementation, this would integrate with browser APIs
            # or use tools like Selenium to gather actual tab information
            
            # Check for common browsers
            common_browsers = ['chrome.exe', 'firefox.exe', 'msedge.exe', 'opera.exe']
            
            for browser_name in common_browsers:
                # Check if browser is running
                browser_running = any(
                    proc.name().lower() == browser_name.lower() 
                    for proc in psutil.process_iter(['name'])
                )
                
                if browser_running:
                    browser_state = BrowserState(
                        browser_name=browser_name.replace('.exe', ''),
                        tabs=[],  # Would be populated by browser integration
                        active_tab_index=0,
                        bookmarks=[],
                        history=[]
                    )
                    browser_states.append(browser_state)
            
            return browser_states
            
        except Exception as e:
            self.logger.error(f"Error gathering browser states: {str(e)}")
            return []
    
    async def _gather_terminal_sessions(self) -> List[TerminalSession]:
        """Gather information about terminal sessions."""
        try:
            terminal_sessions = []
            
            # Check for common terminal processes
            terminal_processes = ['cmd.exe', 'powershell.exe', 'bash.exe', 'zsh.exe']
            
            for terminal_name in terminal_processes:
                # Find running terminal processes
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'].lower() == terminal_name.lower():
                            # Get current directory (if possible)
                            current_dir = self._get_process_working_directory(proc.info['pid'])
                            
                            terminal_session = TerminalSession(
                                session_id=f"{terminal_name}_{proc.info['pid']}",
                                terminal_type=terminal_name.replace('.exe', ''),
                                current_directory=current_dir or "unknown",
                                command_history=[],
                                active_processes=[],
                                environment_variables={}
                            )
                            terminal_sessions.append(terminal_session)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            return terminal_sessions
            
        except Exception as e:
            self.logger.error(f"Error gathering terminal sessions: {str(e)}")
            return []
    
    async def _gather_file_context(self) -> FileContext:
        """Gather file system context information."""
        try:
            # Get user directories
            user_home = os.path.expanduser("~")
            downloads_folder = os.path.join(user_home, "Downloads")
            documents_folder = os.path.join(user_home, "Documents")
            
            # Get recent files (simplified - would need more sophisticated tracking)
            recent_files = []
            open_files = []
            
            # Get clipboard content (would need clipboard integration)
            clipboard_content = None
            
            file_context = FileContext(
                recent_files=recent_files,
                open_files=open_files,
                clipboard_content=clipboard_content,
                downloads_folder=downloads_folder,
                documents_folder=documents_folder
            )
            
            return file_context
            
        except Exception as e:
            self.logger.error(f"Error gathering file context: {str(e)}")
            # Return basic file context
            user_home = os.path.expanduser("~")
            return FileContext(
                recent_files=[],
                open_files=[],
                clipboard_content=None,
                downloads_folder=os.path.join(user_home, "Downloads"),
                documents_folder=os.path.join(user_home, "Documents")
            )
    
    def _get_network_status(self) -> str:
        """Get current network connectivity status."""
        try:
            # Try to connect to a known host
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return "connected"
        except OSError:
            return "disconnected"
    
    def _get_battery_info(self) -> Dict[str, Any]:
        """Get battery information if available."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "level": battery.percent,
                    "plugged_in": battery.power_plugged
                }
        except Exception:
            pass
        
        return {"level": None, "plugged_in": None}
    
    def _get_screen_resolution(self) -> Dict[str, int]:
        """Get screen resolution (Windows-specific implementation)."""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
            height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
            return {"width": width, "height": height}
        except Exception:
            # Fallback to common resolution
            return {"width": 1920, "height": 1080}
    
    def _determine_device_type(self) -> str:
        """Determine the type of device."""
        try:
            # Check if it's a laptop by looking for battery
            battery = psutil.sensors_battery()
            if battery:
                return "laptop"
            
            # Check screen resolution for clues
            screen_res = self._get_screen_resolution()
            if screen_res["width"] < 1024 or screen_res["height"] < 768:
                return "tablet"
            
            return "desktop"
        except Exception:
            return "desktop"
    
    def _determine_os_type(self, system: str) -> str:
        """Determine the OS type."""
        system_lower = system.lower()
        if "windows" in system_lower:
            return "windows"
        elif "darwin" in system_lower:
            return "macos"
        elif "linux" in system_lower:
            return "linux"
        else:
            return "windows"  # Default
    
    def _get_window_title(self, pid: int) -> Optional[str]:
        """Get window title for a process (Windows-specific)."""
        try:
            import win32gui
            import win32process
            
            def enum_windows_callback(hwnd, titles):
                try:
                    _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if found_pid == pid:
                        title = win32gui.GetWindowText(hwnd)
                        if title:
                            titles.append(title)
                except Exception:
                    pass
                return True
            
            titles = []
            win32gui.EnumWindows(enum_windows_callback, titles)
            return titles[0] if titles else None
            
        except ImportError:
            # win32gui not available
            return None
        except Exception:
            return None
    
    def _is_process_focused(self, pid: int) -> bool:
        """Check if a process has focus (simplified implementation)."""
        # This is a simplified check - in a real implementation,
        # you'd need to track window focus events
        return False
    
    def _get_process_working_directory(self, pid: int) -> Optional[str]:
        """Get the working directory of a process."""
        try:
            proc = psutil.Process(pid)
            return proc.cwd()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None


# Export the agent class
__all__ = ["ContextMonitorAgent"]
