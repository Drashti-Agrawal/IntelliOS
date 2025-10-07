import subprocess
import json
import os
import sys
from pathlib import Path
import psutil

# Constants
BASE_DEBUG_PORT = 9222
PORTS_FILE = "browser_ports.json"
SUPPORTED_BROWSERS = {
    'chrome': {
        'windows': r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        'darwin': '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        'linux': 'google-chrome'
    },
    'edge': {
        'windows': r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        'darwin': '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        'linux': 'microsoft-edge'
    }
}

def load_port_data():
    """Load existing port assignments from the JSON file."""
    try:
        if os.path.exists(PORTS_FILE):
            with open(PORTS_FILE, 'r') as f:
                return json.load(f)
        return {"browsers": {}}
    except json.JSONDecodeError:
        print(f"Error: Corrupted {PORTS_FILE} file. Creating new one.")
        return {"browsers": {}}

def save_port_data(data):
    """Save port assignments to the JSON file."""
    try:
        with open(PORTS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving port data: {e}")

def find_next_available_port(port_data):
    """Find the next available debugging port."""
    used_ports = set()
    for browser_info in port_data["browsers"].values():
        used_ports.update(int(port) for port in browser_info["ports"])
    
    port = BASE_DEBUG_PORT
    while port in used_ports:
        port += 1
    return port

def is_port_in_use(port):
    """Check if a port is already in use."""
    for proc in psutil.process_iter(['connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def launch_browser(browser_name, profile_name):
    """Launch browser with remote debugging enabled for the specified profile."""
    browser_name = browser_name.lower()
    
    # Validate browser
    if browser_name not in SUPPORTED_BROWSERS:
        print(f"Error: Unsupported browser '{browser_name}'. Supported browsers: {', '.join(SUPPORTED_BROWSERS.keys())}")
        return False

    # Get browser path based on OS
    platform = sys.platform
    if platform.startswith('win'):
        platform = 'windows'
    elif platform.startswith('darwin'):
        platform = 'darwin'
    else:
        platform = 'linux'

    browser_path = SUPPORTED_BROWSERS[browser_name][platform]
    
    # Load existing port data
    port_data = load_port_data()
    if "browsers" not in port_data:
        port_data["browsers"] = {}

    # Initialize browser data if not exists
    browser_key = f"{browser_name}_{profile_name}"
    if browser_key not in port_data["browsers"]:
        port_data["browsers"][browser_key] = {"ports": []}

    # Find next available port
    debug_port = find_next_available_port(port_data)
    
    # Verify port is not in use
    while is_port_in_use(debug_port):
        debug_port += 1

    try:
        # Prepare command line arguments
        args = [
            browser_path,
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={profile_name}",
            "--no-first-run",
            "--no-default-browser-check"
        ]

        # Launch browser
        subprocess.Popen(args)
        
        # Update port data
        port_data["browsers"][browser_key]["ports"].append(str(debug_port))
        save_port_data(port_data)
        
        print(f"Successfully launched {browser_name} with profile '{profile_name}' on debug port {debug_port}")
        return True

    except FileNotFoundError:
        print(f"Error: Browser executable not found at {browser_path}")
    except Exception as e:
        print(f"Error launching browser: {e}")
    return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python browser_launcher.py <browser_name> <profile_name>")
        print("Supported browsers:", ", ".join(SUPPORTED_BROWSERS.keys()))
        sys.exit(1)

    browser_name = sys.argv[1]
    profile_name = sys.argv[2]
    
    launch_browser(browser_name, profile_name)

if __name__ == "__main__":
    main()