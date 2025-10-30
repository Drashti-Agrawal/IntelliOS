"""
browser_capture.py - Module for capturing browser states
"""
import json
import requests

def get_devtools_tabs(base_url):
    """Get tabs information from browser's devtools API"""
    try:
        resp = requests.get(f"{base_url}/json", timeout=1)
        tabs = resp.json()
        formatted_tabs = []
        for tab in tabs:
            if (tab.get('url') and 
                any(tab['url'].startswith(prefix) for prefix in ['https://', 'http://', 'file://', 'chrome://', 'edge://']) and
                not any(tab.get('title', '').startswith(prefix) for prefix in ['https://', 'http://']) and tab.get('type') == 'page'):
                formatted_tabs.append({
                    "url": tab.get("url"),
                    "title": tab.get("title"),
                    "description": tab.get("description", "")
                })
        return formatted_tabs
    except Exception:
        return []

def capture_browser_states(browser_data):
    """Capture states of all browsers"""

    browsers = []
    
    # Process all browser types
    for browser_name, browser_info in browser_data.items():
        browser_windows = []
        browser_exe = browser_info.get("exe")
        
        # Process all profiles for this browser
        for profile_info in browser_info.get("profiles", []):
            # Handle both profile name formats
            profile_path = profile_info.get("profile") or profile_info.get("user_data_dir")
            if not profile_path:
                continue
            
            # Process all instances of this profile
            for instance in profile_info.get("instances", []):
                if instance.get("status") == "active":
                    port = instance["port"]
                    tabs = get_devtools_tabs(f"http://localhost:{port}")
                    
                    if tabs:
                        window = {
                            "profile": profile_path,
                            "debuggingPort": int(port),
                            "tabs": tabs
                        }
                        browser_windows.append(window)
        
        # Add browser to list if it has active windows
        if browser_windows:
            browsers.append({
                "browser": browser_name,  
                "exe": browser_exe,
                "windows": browser_windows
            })
    
    return browsers