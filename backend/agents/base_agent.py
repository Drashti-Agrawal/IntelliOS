"""
Base Agent Class for IntelliOS

This module defines the base agent class that all IntelliOS agents inherit from.
It provides common functionality, logging, and interface for agent operations.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json

from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig

from core.ddna_state import DigitalDNAState, add_agent_message


class BaseAgent(ABC):
    """
    Base class for all IntelliOS agents.
    
    This class provides common functionality for:
    - State management
    - Logging and monitoring
    - Agent communication
    - Error handling
    - Performance tracking
    """
    
    def __init__(self, agent_name: str, agent_description: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Unique name for this agent
            agent_description: Description of the agent's purpose
            config: Agent-specific configuration
        """
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.config = config or {}
        
        # Set up logging
        self.logger = logging.getLogger(f"intellios.agent.{agent_name}")
        
        # Performance tracking
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.error_count = 0
        
        # Agent state
        self.is_active = True
        self.last_execution = None
        
        self.logger.info(f"Initialized {agent_name}: {agent_description}")
    
    @abstractmethod
    async def process(self, state: DigitalDNAState, **kwargs) -> DigitalDNAState:
        """
        Process the current state and return an updated state.
        
        This is the main method that each agent must implement.
        
        Args:
            state: Current Digital DNA state
            **kwargs: Additional arguments specific to the agent
            
        Returns:
            Updated Digital DNA state
        """
        pass
    
    def pre_process(self, state: DigitalDNAState, **kwargs) -> DigitalDNAState:
        """
        Pre-processing hook called before the main process method.
        
        Args:
            state: Current Digital DNA state
            **kwargs: Additional arguments
            
        Returns:
            State after pre-processing
        """
        # Add agent activation message
        state = add_agent_message(
            state, 
            self.agent_name, 
            f"Agent {self.agent_name} starting processing",
            "info"
        )
        
        self.logger.debug(f"Pre-processing for {self.agent_name}")
        return state
    
    def post_process(self, state: DigitalDNAState, **kwargs) -> DigitalDNAState:
        """
        Post-processing hook called after the main process method.
        
        Args:
            state: Current Digital DNA state
            **kwargs: Additional arguments
            
        Returns:
            State after post-processing
        """
        # Add completion message
        state = add_agent_message(
            state,
            self.agent_name,
            f"Agent {self.agent_name} completed processing",
            "info"
        )
        
        self.logger.debug(f"Post-processing for {self.agent_name}")
        return state
    
    async def execute(self, state: DigitalDNAState, **kwargs) -> DigitalDNAState:
        """
        Execute the agent with full lifecycle management.
        
        Args:
            state: Current Digital DNA state
            **kwargs: Additional arguments
            
        Returns:
            Updated Digital DNA state
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            # Pre-processing
            state = self.pre_process(state, **kwargs)
            
            # Main processing
            state = await self.process(state, **kwargs)
            
            # Post-processing
            state = self.post_process(state, **kwargs)
            
            # Update performance metrics
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.execution_count += 1
            self.total_execution_time += execution_time
            self.last_execution = start_time
            
            self.logger.info(f"{self.agent_name} executed successfully in {execution_time:.2f}s")
            
            return state
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error in {self.agent_name}: {str(e)}", exc_info=True)
            
            # Add error message to state
            state = add_agent_message(
                state,
                self.agent_name,
                f"Error: {str(e)}",
                "error"
            )
            
            raise
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this agent.
        
        Returns:
            Dictionary containing performance metrics
        """
        avg_execution_time = (
            self.total_execution_time / self.execution_count 
            if self.execution_count > 0 else 0.0
        )
        
        return {
            "agent_name": self.agent_name,
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_execution_time,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.execution_count, 1),
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "is_active": self.is_active
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about this agent.
        
        Returns:
            Dictionary containing agent information
        """
        return {
            "name": self.agent_name,
            "description": self.agent_description,
            "config": self.config,
            "performance": self.get_performance_metrics()
        }
    
    def validate_state(self, state: DigitalDNAState) -> bool:
        """
        Validate that the state is compatible with this agent.
        
        Args:
            state: Digital DNA state to validate
            
        Returns:
            True if state is valid, False otherwise
        """
        try:
            # Basic validation - ensure required fields exist
            if not hasattr(state, 'user_id') or not state.user_id:
                self.logger.warning(f"{self.agent_name}: Invalid state - missing user_id")
                return False
            
            if not hasattr(state, 'device_context') or not state.device_context:
                self.logger.warning(f"{self.agent_name}: Invalid state - missing device_context")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"{self.agent_name}: State validation error: {str(e)}")
            return False
    
    def log_state_summary(self, state: DigitalDNAState, prefix: str = ""):
        """
        Log a summary of the current state for debugging.
        
        Args:
            state: Digital DNA state to summarize
            prefix: Optional prefix for log messages
        """
        summary = {
            "user_id": state.user_id,
            "session_id": state.session_id,
            "device_type": state.device_context.device_type,
            "active_apps": len(state.active_applications),
            "browsers": len(state.browser_state),
            "terminals": len(state.terminal_sessions),
            "current_task": state.current_task_intent.primary_intent if state.current_task_intent else None
        }
        
        self.logger.debug(f"{prefix}State summary: {json.dumps(summary, indent=2)}")
    
    def create_llm_messages(self, state: DigitalDNAState, user_message: str) -> List[BaseMessage]:
        """
        Create a list of LangChain messages for LLM interaction.
        
        Args:
            state: Current Digital DNA state
            user_message: User's message or instruction
            
        Returns:
            List of LangChain messages
        """
        messages = []
        
        # Add system message with agent context
        system_message = f"""You are {self.agent_name}, an AI agent in the IntelliOS system.

Your role: {self.agent_description}

Current context:
- User: {state.user_id}
- Device: {state.device_context.device_type} running {state.device_context.os_type}
- Active applications: {len(state.active_applications)}
- Current task: {state.current_task_intent.primary_intent if state.current_task_intent else 'None'}

Respond based on your role and the current context."""
        
        messages.append(HumanMessage(content=system_message))
        messages.append(AIMessage(content=f"I understand. I am {self.agent_name} and I'm ready to help."))
        messages.append(HumanMessage(content=user_message))
        
        return messages
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.agent_name}: {self.agent_description}"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return f"<{self.__class__.__name__}(name='{self.agent_name}', active={self.is_active})>"


# Export the base agent class
__all__ = ["BaseAgent"]
