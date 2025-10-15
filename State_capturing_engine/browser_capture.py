"""
browser_capture.py - Module for capturing browser states
"""
import json
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

def get_devtools_tabs(base_url):
    """Get tabs information from browser's devtools API"""
    try:
        logger.info(f"Attempting to connect to browser at {base_url}")
        
        # Try /json/list endpoint first (Chrome standard)
        try:
            # Increase timeout to give Chrome more time to respond
            resp = requests.get(f"{base_url}/json/list", timeout=10)
            if resp.status_code == 200:
                logger.info(f"Successfully connected to {base_url}/json/list")
                tabs = resp.json()
                logger.info(f"Retrieved {len(tabs)} raw tabs from {base_url}/json/list")
            else:
                logger.warning(f"Failed to get tabs from {base_url}/json/list, status code: {resp.status_code}")
                # Fallback to /json endpoint
                resp = requests.get(f"{base_url}/json", timeout=10)
                if resp.status_code == 200:
                    logger.info(f"Successfully connected to {base_url}/json")
                    tabs = resp.json()
                    logger.info(f"Retrieved {len(tabs)} raw tabs from {base_url}/json")
                else:
                    logger.warning(f"Failed to get tabs from {base_url}/json, status code: {resp.status_code}")
                    return []
        except requests.RequestException as e:
            logger.warning(f"Request error connecting to {base_url}: {str(e)}")
            return []
            
        formatted_tabs = []
        
        for tab in tabs:
            tab_url = tab.get('url', '')
            tab_type = tab.get('type', '')
            
            if tab_url and tab_type == 'page':
                valid_url = any(tab_url.startswith(prefix) for prefix in [
                    'https://', 'http://', 'file://', 'chrome://', 
                    'edge://', 'about:', 'brave://', 'firefox:'
                ])
                
                if valid_url:
                    formatted_tabs.append({
                        "url": tab.get("url"),
                        "title": tab.get("title"),
                        "description": tab.get("description", ""),
                        "favicon": tab.get("favIconUrl", ""),
                        "active": tab.get("active", False)
                    })
                    logger.debug(f"Found tab: {tab.get('title')} ({tab.get('url')})")
        
        logger.info(f"Processed {len(formatted_tabs)} valid tabs from {base_url}")
        return formatted_tabs
    except Exception as e:
        logger.error(f"Error getting tabs from {base_url}: {str(e)}")
        return []

def capture_browser_states(browser_data):
    """Capture states of all browsers"""
    if not browser_data:
        logger.warning("No browser data provided")
        
        # Try default Chrome on port 9222 as fallback
        logger.info("Trying default Chrome on port 9222 as fallback")
        tabs = get_devtools_tabs("http://localhost:9222")
        if tabs:
            logger.info(f"Found {len(tabs)} tabs on default Chrome port 9222")
            return [{
                "browser": "chrome",
                "exe": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "windows": [{"profile": "Default", "debuggingPort": 9222, "tabs": tabs}]
            }]
        return []

    browsers = []
    logger.info(f"Processing browser data for {len(browser_data)} browsers")
    
    # Process all browser types
    for browser_name, browser_info in browser_data.items():
        logger.info(f"Processing browser: {browser_name}")
        browser_windows = []
        browser_exe = browser_info.get("exe")
        
        if not browser_exe:
            logger.warning(f"No exe path for {browser_name}, skipping")
            continue
            
        # Process all profiles for this browser
        profiles = browser_info.get("profiles", [])
        if not profiles:
            logger.warning(f"No profiles found for {browser_name}")
            
            # Try direct port check if specified in browser_info
            direct_port = browser_info.get("port")
            if direct_port:
                logger.info(f"Trying direct port {direct_port} for {browser_name}")
                tabs = get_devtools_tabs(f"http://localhost:{direct_port}")
                if tabs:
                    window = {
                        "profile": "Default",
                        "debuggingPort": int(direct_port),
                        "tabs": tabs
                    }
                    browser_windows.append(window)
            
        # Process each profile
        for profile_info in profiles:
            logger.info(f"Processing profile for {browser_name}: {profile_info}")
            # Handle both profile name formats
            profile_path = profile_info.get("profile") or profile_info.get("user_data_dir")
            if not profile_path:
                logger.warning(f"No profile path for {browser_name} profile, skipping")
                continue
            
            # Process all instances of this profile
            instances = profile_info.get("instances", [])
            if not instances:
                logger.warning(f"No instances found for {browser_name} profile {profile_path}")
                continue
                
            for instance in instances:
                instance_status = instance.get("status", "")
                port = instance.get("port")
                
                logger.info(f"Processing instance for {browser_name}, status: {instance_status}, port: {port}")
                
                if instance_status == "active" and port:
                    logger.info(f"Connecting to {browser_name} on port {port}")
                    tabs = get_devtools_tabs(f"http://localhost:{port}")
                    
                    if tabs:
                        logger.info(f"Found {len(tabs)} tabs for {browser_name} on port {port}")
                        window = {
                            "profile": profile_path,
                            "debuggingPort": int(port),
                            "tabs": tabs
                        }
                        browser_windows.append(window)
                    else:
                        logger.warning(f"No tabs found for {browser_name} on port {port}")
        
        # Add browser to list if it has active windows
        if browser_windows:
            browsers.append({
                "browser": browser_name,  
                "exe": browser_exe,
                "windows": browser_windows
            })
            logger.info(f"Added {browser_name} with {len(browser_windows)} windows")
        else:
            logger.warning(f"No windows captured for {browser_name}")
    
    # ALWAYS try direct connection regardless of previous browser detection or status
    logger.info("ALWAYS attempting direct connection to Chrome debugging ports")
    
    import time
    import socket
    import requests
    
    # Try multiple common debugging ports with more aggressive retry strategy
    for port in [9222, 9223, 9224]:
        try:
            # First check if the port is open with a socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3)  # Longer timeout
                result = s.connect_ex(('localhost', port))
                logger.info(f"Socket check for port {port} result: {result}")
                
                if result == 0:  # Port is open
                    logger.info(f"Port {port} is open, attempting to get tabs")
                    
                    # Try to connect multiple times with increasing timeouts
                    for attempt in range(3):
                        try:
                            # Try a direct HTTP request first
                            timeout = 5 * (attempt + 1)  # 5, 10, 15 seconds
                            logger.info(f"Attempt {attempt+1} with timeout {timeout}s")
                            resp = requests.get(f"http://localhost:{port}/json/version", timeout=timeout)
                            
                            if resp.status_code == 200:
                                logger.info(f"DevTools API is responsive on port {port}")
                                tabs = get_devtools_tabs(f"http://localhost:{port}")
                                
                                if tabs:
                                    logger.info(f"Found {len(tabs)} tabs on port {port}")
                                    browsers.append({
                                        "browser": "chrome" if port == 9222 else "edge" if port == 9223 else "browser",
                                        "exe": "",
                                        "windows": [{"profile": "Default", "debuggingPort": port, "tabs": tabs}]
                                    })
                                    break  # Success, exit retry loop
                                else:
                                    logger.warning(f"No tabs found on port {port} despite successful connection")
                            else:
                                logger.warning(f"Port {port} returned status code {resp.status_code}")
                                
                        except Exception as e:
                            logger.warning(f"Attempt {attempt+1} failed for port {port}: {str(e)}")
                            time.sleep(1)  # Brief pause before retry
                else:
                    logger.info(f"Port {port} is not open")
                    
        except Exception as e:
            logger.error(f"Error checking port {port}: {e}")
    
    logger.info(f"Captured {len(browsers)} browsers with tabs")
    return browsers