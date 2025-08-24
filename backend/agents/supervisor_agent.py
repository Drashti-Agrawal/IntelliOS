"""
Supervisor Agent - Orchestrates and coordinates all other agents in the IntelliOS system.

This agent acts as the central coordinator, managing the workflow between different
specialized agents and ensuring the overall system operates efficiently.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .base_agent import BaseAgent
from core.ddna_state import DigitalDNAState


class AgentStatus(Enum):
    """Status of an agent in the system."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class AgentInfo:
    """Information about an agent in the system."""
    name: str
    agent: BaseAgent
    status: AgentStatus
    last_run: Optional[datetime] = None
    error_count: int = 0
    priority: int = 1  # Higher number = higher priority


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent - Central coordinator for all IntelliOS agents.
    
    Responsibilities:
    - Manages agent lifecycle and execution order
    - Monitors agent health and performance
    - Coordinates inter-agent communication
    - Handles error recovery and fallback strategies
    - Maintains system-wide state consistency
    """
    
    def __init__(self, name: str = "SupervisorAgent"):
        super().__init__(name, "Orchestrates and coordinates all other agents in the IntelliOS system")
        self.agents: Dict[str, AgentInfo] = {}
        self.execution_queue: List[str] = []
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
    def register_agent(self, agent: BaseAgent, priority: int = 1) -> None:
        """
        Register an agent with the supervisor.
        
        Args:
            agent: The agent instance to register
            priority: Execution priority (higher = more important)
        """
        agent_info = AgentInfo(
            name=agent.agent_name,
            agent=agent,
            status=AgentStatus.IDLE,
            priority=priority
        )
        self.agents[agent.agent_name] = agent_info
        self.logger.info(f"Registered agent: {agent.agent_name} with priority {priority}")
        
    def unregister_agent(self, agent_name: str) -> None:
        """Remove an agent from the supervisor."""
        if agent_name in self.agents:
            del self.agents[agent_name]
            self.logger.info(f"Unregistered agent: {agent_name}")
            
    def get_agent_status(self, agent_name: str) -> Optional[AgentStatus]:
        """Get the current status of an agent."""
        if agent_name in self.agents:
            return self.agents[agent_name].status
        return None
        
    def set_agent_priority(self, agent_name: str, priority: int) -> None:
        """Update the priority of an agent."""
        if agent_name in self.agents:
            self.agents[agent_name].priority = priority
            self.logger.info(f"Updated priority for {agent_name}: {priority}")
            
    def _build_execution_queue(self) -> List[str]:
        """Build execution queue based on agent priorities and dependencies."""
        # Sort agents by priority (highest first)
        sorted_agents = sorted(
            self.agents.items(),
            key=lambda x: x[1].priority,
            reverse=True
        )
        
        # Filter out disabled agents
        active_agents = [
            name for name, info in sorted_agents
            if info.status != AgentStatus.DISABLED
        ]
        
        return active_agents
        
    async def execute_agent(self, agent_name: str, state: DigitalDNAState) -> bool:
        """
        Execute a single agent with error handling and retries.
        
        Args:
            agent_name: Name of the agent to execute
            state: Current dDNA state
            
        Returns:
            True if execution succeeded, False otherwise
        """
        if agent_name not in self.agents:
            self.logger.error(f"Agent not found: {agent_name}")
            return False
            
        agent_info = self.agents[agent_name]
        agent = agent_info.agent
        
        # Update status
        agent_info.status = AgentStatus.RUNNING
        agent_info.last_run = datetime.now()
        
        try:
            self.logger.info(f"Executing agent: {agent_name}")
            
            # Execute the agent
            result = await agent.execute(state)
            
            if result:
                agent_info.status = AgentStatus.COMPLETED
                agent_info.error_count = 0
                self.logger.info(f"Agent {agent_name} completed successfully")
                return True
            else:
                agent_info.status = AgentStatus.FAILED
                agent_info.error_count += 1
                self.logger.error(f"Agent {agent_name} failed")
                return False
                
        except Exception as e:
            agent_info.status = AgentStatus.FAILED
            agent_info.error_count += 1
            self.logger.error(f"Agent {agent_name} failed with exception: {e}")
            return False
            
    async def execute_with_retry(self, agent_name: str, state: DigitalDNAState) -> bool:
        """
        Execute an agent with automatic retry on failure.
        
        Args:
            agent_name: Name of the agent to execute
            state: Current dDNA state
            
        Returns:
            True if execution succeeded after retries, False otherwise
        """
        agent_info = self.agents[agent_name]
        
        for attempt in range(self.max_retries):
            if attempt > 0:
                self.logger.info(f"Retry attempt {attempt} for agent {agent_name}")
                await asyncio.sleep(self.retry_delay)
                
            success = await self.execute_agent(agent_name, state)
            if success:
                return True
                
        # If all retries failed, disable the agent
        agent_info.status = AgentStatus.DISABLED
        self.logger.error(f"Agent {agent_name} disabled after {self.max_retries} failed attempts")
        return False
        
    async def execute_workflow(self, state: DigitalDNAState) -> DigitalDNAState:
        """
        Execute the complete agent workflow.
        
        Args:
            state: Initial dDNA state
            
        Returns:
            Updated dDNA state after all agents have executed
        """
        self.logger.info("Starting agent workflow execution")
        
        # Add supervisor message to state
        from core.ddna_state import add_agent_message
        state = add_agent_message(
            state, 
            self.agent_name,
            "Starting agent workflow execution",
            "workflow_start"
        )
        
        # Build execution queue
        execution_queue = self._build_execution_queue()
        
        if not execution_queue:
            self.logger.warning("No active agents to execute")
            return state
            
        # Execute agents in priority order
        for agent_name in execution_queue:
            success = await self.execute_with_retry(agent_name, state)
            
            if not success:
                # Add error message to state
                state = add_agent_message(
                    state,
                    self.agent_name,
                    f"Agent {agent_name} failed execution",
                    "agent_error"
                )
                
        # Add completion message
        state = add_agent_message(
            state,
            self.agent_name,
            "Agent workflow execution completed",
            "workflow_complete"
        )
        
        self.logger.info("Agent workflow execution completed")
        return state
        
    async def process(self, state: DigitalDNAState) -> DigitalDNAState:
        """
        Main processing method - orchestrates all agents.
        
        Args:
            state: Current dDNA state
            
        Returns:
            Updated dDNA state
        """
        # Execute the complete workflow
        return await self.execute_workflow(state)
        
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get overall system health information.
        
        Returns:
            Dictionary containing health metrics
        """
        total_agents = len(self.agents)
        active_agents = sum(1 for info in self.agents.values() 
                          if info.status != AgentStatus.DISABLED)
        failed_agents = sum(1 for info in self.agents.values() 
                          if info.status == AgentStatus.FAILED)
        disabled_agents = sum(1 for info in self.agents.values() 
                            if info.status == AgentStatus.DISABLED)
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "failed_agents": failed_agents,
            "disabled_agents": disabled_agents,
            "health_percentage": (active_agents / total_agents * 100) if total_agents > 0 else 0,
            "agent_statuses": {
                name: info.status.value for name, info in self.agents.items()
            }
        }
        
    def get_agent_metrics(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed metrics for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dictionary containing agent metrics or None if agent not found
        """
        if agent_name not in self.agents:
            return None
            
        agent_info = self.agents[agent_name]
        
        return {
            "name": agent_name,
            "status": agent_info.status.value,
            "priority": agent_info.priority,
            "last_run": agent_info.last_run.isoformat() if agent_info.last_run else None,
            "error_count": agent_info.error_count,
            "execution_time": getattr(agent_info.agent, 'last_execution_time', None),
            "performance_metrics": agent_info.agent.get_performance_metrics()
        }
