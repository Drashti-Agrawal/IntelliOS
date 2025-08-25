"""
Base Tool Framework for IntelliOS OS-Level Tools

This module provides the foundation for all OS-level tools used by the agentic AI system.
"""

import os
import sys
import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.logging_config import setup_logging

# Set up logger
logger = logging.getLogger(__name__)

class ToolStatus(Enum):
    """Status of tool execution"""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    NOT_SUPPORTED = "not_supported"

@dataclass
class ToolResult:
    """Result of a tool execution"""
    status: ToolStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class ToolError(Exception):
    """Custom exception for tool-related errors"""
    def __init__(self, message: str, tool_name: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.tool_name = tool_name
        self.details = details or {}
        super().__init__(self.message)

class BaseTool(ABC):
    """
    Base class for all OS-level tools in the IntelliOS system.
    
    This class provides a common interface and functionality for all tools,
    including error handling, logging, and result formatting.
    """
    
    def __init__(self, name: str, description: str, timeout: float = 30.0):
        """
        Initialize the base tool.
        
        Args:
            name: Name of the tool
            description: Description of what the tool does
            timeout: Maximum execution time in seconds
        """
        self.name = name
        self.description = description
        self.timeout = timeout
        self.logger = logging.getLogger(f"intellios.tool.{name}")
        
        # Tool capabilities
        self.capabilities = []
        self.requirements = []
        
        # Initialize tool-specific components
        self._initialize()
    
    def _initialize(self):
        """Initialize tool-specific components. Override in subclasses."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult: Result of the execution
        """
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate the input parameters for the tool.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            bool: True if parameters are valid, False otherwise
        """
        return True
    
    def get_capabilities(self) -> List[str]:
        """Get list of tool capabilities."""
        return self.capabilities.copy()
    
    def get_requirements(self) -> List[str]:
        """Get list of tool requirements."""
        return self.requirements.copy()
    
    def is_supported(self) -> bool:
        """
        Check if the tool is supported on the current system.
        
        Returns:
            bool: True if supported, False otherwise
        """
        return True
    
    async def execute_with_timeout(self, **kwargs) -> ToolResult:
        """
        Execute the tool with timeout handling.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult: Result of the execution
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate parameters
            if not self.validate_parameters(**kwargs):
                return ToolResult(
                    status=ToolStatus.FAILED,
                    error="Invalid parameters",
                    execution_time=0.0
                )
            
            # Check if tool is supported
            if not self.is_supported():
                return ToolResult(
                    status=ToolStatus.NOT_SUPPORTED,
                    error=f"Tool {self.name} is not supported on this system",
                    execution_time=0.0
                )
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self.execute(**kwargs),
                timeout=self.timeout
            )
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            result.execution_time = execution_time
            
            self.logger.info(f"Tool {self.name} executed successfully in {execution_time:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Tool {self.name} timed out after {execution_time:.2f}s")
            return ToolResult(
                status=ToolStatus.TIMEOUT,
                error=f"Tool execution timed out after {self.timeout}s",
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Tool {self.name} failed: {str(e)}")
            return ToolResult(
                status=ToolStatus.FAILED,
                error=str(e),
                execution_time=execution_time
            )
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the tool.
        
        Returns:
            Dict containing tool information
        """
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "requirements": self.requirements,
            "supported": self.is_supported(),
            "timeout": self.timeout
        }
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
