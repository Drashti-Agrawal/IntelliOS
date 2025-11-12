"""
Test script for workspace sync functionality
"""
import json
import requests
from typing import Dict, Any

# Remote API configuration
REMOTE_API_BASE_URL = "https://intellios-database.onrender.com"

def sync_workspace_to_remote(username: str, workspace_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sync workspace data to remote DDNA database
    
    Args:
        username: Username for the workspace
        workspace_name: Name of the workspace
        state: State data containing apps, browsers, etc.
        
    Returns:
        Response dict with status and message
    """
    try:
        url = f"{REMOTE_API_BASE_URL}/api/workspace"
        payload = {
            "username": username,
            "workspace_name": workspace_name,
            "state": state
        }
        
        print(f"📤 Sending request to: {url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response body: {response.text}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            return {
                "status": "success",
                "message": result.get("message", "Workspace synced successfully"),
                "response": result
            }
        else:
            return {
                "status": "error",
                "message": f"API returned status {response.status_code}: {response.text}"
            }
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "message": "Request timed out. The remote server might be slow or unavailable."
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Could not connect to remote server. Check your internet connection."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


if __name__ == "__main__":
    # Test data
    test_username = "Jatan"
    test_workspace = "Test Development Workspace"
    test_state = {
        "saved_at": "2025-11-12T15:30:00",
        "user": test_username,
        "workspace_name": test_workspace,
        "apps": ["VS Code", "Chrome", "Terminal"],
        "files": 10,
        "tabs": 5,
        "lastUsed": "2025-11-12 15:30",
        "synced": False
    }
    
    print("🧪 Testing workspace sync to remote DDNA...")
    print("=" * 60)
    
    result = sync_workspace_to_remote(test_username, test_workspace, test_state)
    
    print("=" * 60)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    if result['status'] == 'success':
        print("✅ Test PASSED - Workspace synced successfully!")
    else:
        print(f"❌ Test FAILED - {result['message']}")
