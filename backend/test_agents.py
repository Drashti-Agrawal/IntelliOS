#!/usr/bin/env python3
"""
Test script for IntelliOS Agentic System

This script tests the core components of the agentic system:
- Digital DNA state creation and management
- Context Monitor Agent functionality
- Agent lifecycle and performance tracking
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ddna_state import (
    DigitalDNAState, 
    DeviceContext, 
    FileContext, 
    create_initial_state,
    get_state_summary
)
from agents import ContextMonitorAgent


async def test_ddna_state():
    """Test Digital DNA state creation and management."""
    print("🧬 Testing Digital DNA State...")
    
    # Create a basic device context
    device_context = DeviceContext(
        device_id="test-device",
        device_type="desktop",
        os_type="windows",
        os_version="10.0.19045",
        screen_resolution={"width": 1920, "height": 1080},
        available_memory=8192,
        cpu_usage=25.5,
        network_status="connected"
    )
    
    # Create a basic file context
    file_context = FileContext(
        downloads_folder="C:\\Users\\Test\\Downloads",
        documents_folder="C:\\Users\\Test\\Documents"
    )
    
    # Create initial state
    state = create_initial_state("test-user", device_context, file_context)
    
    print(f"✅ Created dDNA state for user: {state.user_id}")
    print(f"✅ Session ID: {state.session_id}")
    print(f"✅ Device: {state.device_context.device_type} running {state.device_context.os_type}")
    
    # Test state summary
    summary = get_state_summary(state)
    print(f"✅ State summary: {summary}")
    
    return state


async def test_context_monitor_agent():
    """Test the Context Monitor Agent."""
    print("\n🔍 Testing Context Monitor Agent...")
    
    # Create the agent
    agent = ContextMonitorAgent(config={
        "monitoring_interval": 2.0,
        "max_apps_to_track": 10
    })
    
    print(f"✅ Created agent: {agent.agent_name}")
    print(f"✅ Description: {agent.agent_description}")
    
    # Get agent info
    agent_info = agent.get_agent_info()
    print(f"✅ Agent info: {agent_info['name']} - {agent_info['description']}")
    
    return agent


async def test_agent_execution(agent, state):
    """Test agent execution with the dDNA state."""
    print("\n🚀 Testing Agent Execution...")
    
    try:
        # Execute the agent
        updated_state = await agent.execute(state)
        
        print(f"✅ Agent executed successfully!")
        print(f"✅ Updated state timestamp: {updated_state.timestamp}")
        print(f"✅ Active applications: {len(updated_state.active_applications)}")
        print(f"✅ Browser states: {len(updated_state.browser_state)}")
        print(f"✅ Terminal sessions: {len(updated_state.terminal_sessions)}")
        
        # Show some application details
        if updated_state.active_applications:
            print("\n📱 Top applications:")
            for i, app in enumerate(updated_state.active_applications[:5]):
                print(f"  {i+1}. {app.name} (PID: {app.process_id}, Memory: {app.memory_usage}MB)")
        
        # Show agent messages
        if updated_state.agent_messages:
            print("\n💬 Agent messages:")
            for msg in updated_state.agent_messages[-3:]:  # Last 3 messages
                print(f"  [{msg['timestamp']}] {msg['agent']}: {msg['message']}")
        
        # Get performance metrics
        metrics = agent.get_performance_metrics()
        print(f"\n📊 Performance metrics:")
        print(f"  Execution count: {metrics['execution_count']}")
        print(f"  Average execution time: {metrics['average_execution_time']:.2f}s")
        print(f"  Error count: {metrics['error_count']}")
        
        return updated_state
        
    except Exception as e:
        print(f"❌ Agent execution failed: {str(e)}")
        raise


async def main():
    """Main test function."""
    print("🧪 IntelliOS Agentic System Test")
    print("=" * 50)
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Test dDNA state
        state = await test_ddna_state()
        
        # Test agent creation
        agent = await test_context_monitor_agent()
        
        # Test agent execution
        updated_state = await test_agent_execution(agent, state)
        
        print("\n🎉 All tests passed! The agentic system foundation is working correctly.")
        
        # Show final state summary
        final_summary = get_state_summary(updated_state)
        print(f"\n📋 Final state summary: {final_summary}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
