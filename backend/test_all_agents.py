"""
Comprehensive test script for all IntelliOS agents.

This script tests the complete agentic system including:
- Supervisor Agent orchestration
- All specialized agents (Context Monitor, Workspace Config, Tool Resource, State Sync)
- Agent coordination and communication
- dDNA state management
"""

import asyncio
import logging
from datetime import datetime

from core.ddna_state import create_initial_state, get_state_summary
from agents import (
    SupervisorAgent, ContextMonitorAgent, WorkspaceConfigAgent,
    ToolResourceAgent, StateSyncAgent
)
from config.logging_config import setup_logging


async def test_supervisor_agent():
    """Test the Supervisor Agent with all other agents."""
    print("\n" + "="*60)
    print("TESTING SUPERVISOR AGENT")
    print("="*60)
    
    # Create supervisor
    supervisor = SupervisorAgent()
    
    # Create and register all agents with different priorities
    context_agent = ContextMonitorAgent()
    workspace_agent = WorkspaceConfigAgent()
    tool_agent = ToolResourceAgent()
    sync_agent = StateSyncAgent()
    
    # Register agents with priorities (higher = more important)
    supervisor.register_agent(context_agent, priority=5)      # Highest priority
    supervisor.register_agent(workspace_agent, priority=4)
    supervisor.register_agent(tool_agent, priority=3)
    supervisor.register_agent(sync_agent, priority=2)         # Lowest priority
    
    print(f"Registered {len(supervisor.agents)} agents:")
    for name, info in supervisor.agents.items():
        print(f"  - {name}: priority {info.priority}, status {info.status.value}")
    
    # Get system health
    health = supervisor.get_system_health()
    print(f"\nSystem Health: {health['health_percentage']:.1f}% healthy")
    print(f"Active agents: {health['active_agents']}/{health['total_agents']}")
    
    return supervisor


async def test_individual_agents():
    """Test each agent individually."""
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL AGENTS")
    print("="*60)
    
    # Create initial state
    state = create_initial_state()
    print(f"Initial state created: {get_state_summary(state)}")
    
    # Test Context Monitor Agent
    print("\n--- Testing Context Monitor Agent ---")
    context_agent = ContextMonitorAgent()
    state = await context_agent.execute(state)
    print(f"Context updated: {get_state_summary(state)}")
    
    # Test Workspace Config Agent
    print("\n--- Testing Workspace Config Agent ---")
    workspace_agent = WorkspaceConfigAgent()
    state = await workspace_agent.execute(state)
    print(f"Workspace configured: {get_state_summary(state)}")
    
    # Test Tool Resource Agent
    print("\n--- Testing Tool Resource Agent ---")
    tool_agent = ToolResourceAgent()
    state = await tool_agent.execute(state)
    print(f"Tools discovered: {get_state_summary(state)}")
    
    # Test State Sync Agent
    print("\n--- Testing State Sync Agent ---")
    sync_agent = StateSyncAgent()
    state = await sync_agent.execute(state)
    print(f"State synchronized: {get_state_summary(state)}")
    
    return state


async def test_agent_coordination():
    """Test agent coordination through the supervisor."""
    print("\n" + "="*60)
    print("TESTING AGENT COORDINATION")
    print("="*60)
    
    # Create supervisor with all agents
    supervisor = await test_supervisor_agent()
    
    # Create initial state
    state = create_initial_state()
    print(f"\nInitial state: {get_state_summary(state)}")
    
    # Execute complete workflow
    print("\nExecuting complete agent workflow...")
    start_time = datetime.now()
    
    state = await supervisor.execute_workflow(state)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\nWorkflow completed in {duration:.2f} seconds")
    print(f"Final state: {get_state_summary(state)}")
    
    # Check agent statuses
    print("\nAgent Statuses:")
    for name, info in supervisor.agents.items():
        print(f"  - {name}: {info.status.value}")
        if info.last_run:
            print(f"    Last run: {info.last_run.strftime('%H:%M:%S')}")
        if info.error_count > 0:
            print(f"    Errors: {info.error_count}")
    
    # Get final system health
    health = supervisor.get_system_health()
    print(f"\nFinal System Health: {health['health_percentage']:.1f}% healthy")
    
    return state, supervisor


async def test_agent_features():
    """Test specific features of each agent."""
    print("\n" + "="*60)
    print("TESTING AGENT FEATURES")
    print("="*60)
    
    # Test Workspace Config Agent features
    print("\n--- Workspace Config Features ---")
    workspace_agent = WorkspaceConfigAgent()
    workspace_info = workspace_agent.get_workspace_info()
    print(f"Workspace type: {workspace_info['workspace_type']}")
    print(f"Workspace path: {workspace_info['workspace_path']}")
    print(f"Supported types: {workspace_agent.get_supported_workspace_types()}")
    
    # Test Tool Resource Agent features
    print("\n--- Tool Resource Features ---")
    tool_agent = ToolResourceAgent()
    resource_summary = tool_agent.get_resource_summary()
    if resource_summary:
        print(f"CPU usage: {resource_summary['cpu_percent']:.1f}%")
        print(f"Memory usage: {resource_summary['memory_percent']:.1f}%")
        print(f"Available memory: {resource_summary['memory_available_gb']} GB")
        print(f"Total tools: {resource_summary['total_tools']}")
    
    # Test State Sync Agent features
    print("\n--- State Sync Features ---")
    sync_agent = StateSyncAgent()
    sync_status = sync_agent.get_sync_status()
    print(f"Firebase available: {sync_status['firebase_available']}")
    print(f"Total versions: {sync_status['total_versions']}")
    print(f"Last sync: {sync_status['last_sync']}")
    
    # Test tool execution
    print("\n--- Tool Execution Test ---")
    success, output = tool_agent.execute_tool("python", ["--version"])
    if success:
        print(f"Python version: {output.strip()}")
    else:
        print(f"Tool execution failed: {output}")


async def test_error_handling():
    """Test error handling and recovery."""
    print("\n" + "="*60)
    print("TESTING ERROR HANDLING")
    print("="*60)
    
    supervisor = SupervisorAgent()
    
    # Create a mock agent that fails
    class FailingAgent(ContextMonitorAgent):
        def __init__(self, name: str = "FailingAgent"):
            super().__init__(config={})  # Pass empty config dict
            self.agent_name = name  # Override the agent name
            
        async def process(self, state):
            raise Exception("Simulated agent failure")
    
    # Register failing agent
    failing_agent = FailingAgent("FailingAgent")
    supervisor.register_agent(failing_agent, priority=1)
    
    # Try to execute
    state = create_initial_state()
    print("Testing agent failure handling...")
    
    success = await supervisor.execute_agent("FailingAgent", state)
    print(f"Agent execution result: {success}")
    
    # Check retry mechanism
    print("Testing retry mechanism...")
    success = await supervisor.execute_with_retry("FailingAgent", state)
    print(f"Retry result: {success}")
    
    # Check agent status
    status = supervisor.get_agent_status("FailingAgent")
    print(f"Agent status after failures: {status.value}")


async def main():
    """Main test function."""
    print("INTELLIOS AGENTIC SYSTEM TEST")
    print("="*60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test individual agents
        state = await test_individual_agents()
        
        # Test agent coordination
        state, supervisor = await test_agent_coordination()
        
        # Test specific features
        await test_agent_features()
        
        # Test error handling
        await test_error_handling()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Final summary
        print(f"\nFinal State Summary:")
        print(f"  - Device: {state.device_context.device_id if state.device_context else 'Unknown'}")
        print(f"  - Workspace: {state.workspace_context.workspace_type if state.workspace_context else 'Unknown'}")
        print(f"  - Tools: {len(state.system_resources.available_tools) if state.system_resources else 0}")
        print(f"  - Agent messages: {len(state.agent_messages)}")
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        logging.exception("Test error")
        raise


if __name__ == "__main__":
    # Setup logging
    setup_logging("DEBUG")
    
    # Run tests
    asyncio.run(main())
