#!/usr/bin/env python3

"""
===========================================
 Restore-State.py
 Reopens browsers + apps/files from state.json
===========================================
"""

import json
import os
import subprocess
import time
import sys
import psutil
import shutil
from datetime import datetime
import win32gui, win32con, win32process

# Directory to store profile copies
PROFILE_COPIES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile_copies")

# Default parameters
EXE_PATHS = {
    "chrome": "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "msedge": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "opera": "C:\\Users\\jaypa\\AppData\\Local\\Programs\\Opera\\opera.exe"
}

STATE_FILE = "D:\\Major\\IntelliOS\\State\\state.json"

def is_port_in_use(port):
    """Check if a port is already in use."""
    if not port:
        return False
    try:
        port = int(port)
        for proc in psutil.process_iter(['connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except (ValueError, TypeError):
        return False
    return False

def is_profile_in_use(profile_path):
    """Check if a browser profile is currently in use."""
    if not profile_path:
        return False
        
    # Create the profile directory if it doesn't exist
    os.makedirs(profile_path, exist_ok=True)
    
    try:
        lock_file = os.path.join(profile_path, "Lock")
        if os.path.exists(lock_file):
            try:
                # Try to delete the lock file - if we can, profile isn't truly locked
                os.remove(lock_file)
                return False
            except (PermissionError, OSError):
                # If we can't delete it, profile is in use
                return True
        
        # Check for running browser processes using this profile
        for proc in psutil.process_iter(['cmdline']):
            try:
                cmdline = proc.cmdline()
                if any(profile_path.lower() in arg.lower() for arg in cmdline if isinstance(arg, str)):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue
    except Exception as e:
        print(f"Error checking profile usage: {str(e)}")
        return False
    
    return False

def create_profile_copy(original_profile):
    """Create a copy of the browser profile with a new name."""
    if not original_profile:
        return None
    
    try:
        # Create timestamp-based profile name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        profile_name = f"profile_copy_{timestamp}"
        new_profile_path = os.path.join(PROFILE_COPIES_DIR, profile_name)
        
        # Create the copies directory if it doesn't exist
        os.makedirs(PROFILE_COPIES_DIR, exist_ok=True)
        
        # Create the basic profile structure
        print(f"Creating new profile at {new_profile_path}")
        os.makedirs(new_profile_path, exist_ok=True)
        os.makedirs(os.path.join(new_profile_path, "Default"), exist_ok=True)
        
        # If original profile exists, try to copy essential files
        if os.path.exists(original_profile):
            # List of essential directories to copy
            essential_dirs = [
                "Default/Bookmarks",
                "Default/Preferences",
                "Default/Favicons",
                "Default/History",
                "Default/Login Data",
                "Default/Web Data"
            ]
            
            for item in essential_dirs:
                src = os.path.join(original_profile, item)
                dst = os.path.join(new_profile_path, item)
                dst_dir = os.path.dirname(dst)
                
                if os.path.exists(src):
                    try:
                        # Ensure the destination directory exists
                        os.makedirs(dst_dir, exist_ok=True)
                        # Try to copy the file
                        if os.path.isfile(src):
                            shutil.copy2(src, dst)
                    except (PermissionError, OSError) as e:
                        print(f"Warning: Could not copy {item}: {str(e)}")
                        continue
        
        return new_profile_path
    except Exception as e:
        print(f"Warning: Error while creating profile copy: {str(e)}")
        # Even if we hit some errors, return the new profile path if it was created
        if os.path.exists(new_profile_path):
            return new_profile_path
        return None

def restore_browser(browser, windows, exe):
    """Restore browser windows and their tabs"""
    print(exe)
    if not windows or len(windows) == 0:
        return

    # Open each window as a separate browser window and pass URLs
    for window in windows:
        urls = []
        for tab in window['tabs']:
            if (tab.get('url') and 
                any(tab['url'].startswith(prefix) for prefix in ['https://', 'http://', 'file://', 'chrome://', 'edge://']) and
                not any(tab.get('title', '').startswith(prefix) for prefix in ['https://', 'http://'])):
                urls.append(tab['url'])
        
        if len(urls) == 0:
            continue
        
        
        # Check if debugging port is in use
        debugging_port = window.get('debuggingPort')
        if is_port_in_use(debugging_port):
            print(f"Error: Debugging port {debugging_port} is already in use", file=sys.stderr)
            continue
            
        # Handle profile path
        original_profile = window.get('profile')
        profile_path = original_profile
        
        print(f"Checking profile: {original_profile}")
        if original_profile:
            if is_profile_in_use(original_profile):
                print(f"Profile {original_profile} is in use, creating a copy...")
                new_profile = create_profile_copy(original_profile)
                if new_profile:
                    profile_path = new_profile
                    print(f"Successfully created new profile copy at: {profile_path}")
                else:
                    print(f"Error: Could not create profile copy for {original_profile}", file=sys.stderr)
                    continue
            else:
                print(f"Profile {original_profile} is not in use, using it directly")
        
        # Start a new window with multiple tabs
        try:
            args = [
                exe,
                f"--remote-debugging-port={debugging_port}",
                f"--user-data-dir={profile_path}",
                "--args",
                "--new-window",
                "--no-first-run",
                "--no-default-browser-check",
            ]
            subprocess.Popen(args + urls)
            time.sleep(0.3)
        except Exception as e:
            print(f"Error launching {browser}: {str(e)}", file=sys.stderr)


# def restore_window_position(hwnd, window_info):
#     if not window_info:
#         return
        
#     # Set window position and size
#     if window_info.get("position") and window_info.get("size"):
#         pos = window_info["position"]
#         size = window_info["size"]
#         win32gui.MoveWindow(
#             hwnd, 
#             pos["x"], 
#             pos["y"], 
#             size["width"], 
#             size["height"], 
#             True
#         )
    
#     # Set window state
#     state = window_info.get("state", "normal")
#     if state == "maximized":
#         win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
#     elif state == "minimized":
#         win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
#     else:
#         win32gui.ShowWindow(hwnd, win32con.SW_NORMAL)

def restore_app_files(exe, items, name, window_info=None):
    """Restore applications and their associated files"""
    if not exe or not os.path.exists(exe):
        # Try just the process name if exe missing
        exe = name
    
    if not items or len(items) == 0:
        # If no files, just open the app
        try:
            subprocess.Popen([exe])
            return
        except Exception as e:
            print(f"Error launching {name}: {str(e)}", file=sys.stderr)
            return

    # Some apps prefer one process with multiple args (Word/Excel), others prefer separate instances
    one_shot_apps = ["WINWORD.EXE", "EXCEL.EXE", "POWERPNT.EXE", "Acrobat.exe", "AcroRd32.exe"]
    process = None
    try:
        if name in one_shot_apps:
            process = subprocess.Popen([exe] + items)
        else:
            for item in items:
                subprocess.Popen([exe, item])
                time.sleep(0.1)

        # Wait briefly for the window to appear
        time.sleep(1)
        
        # Find the main window
        # def find_window(hwnd, _):
        #     if win32gui.IsWindowVisible(hwnd):
        #         _, pid = win32process.GetWindowThreadProcessId(hwnd)
        #         if pid == process.pid:
        #             restore_window_position(hwnd, window_info)
        #             return False
        #     return True
            
        # win32gui.EnumWindows(find_window, None)

    except Exception as e:
        print(f"Error launching {name} with items: {str(e)}", file=sys.stderr)

def main():
    # Check if state file exists
    if not os.path.exists(STATE_FILE):
        print(f"Error: State file not found: {STATE_FILE}", file=sys.stderr)
        sys.exit(1)

    # Read state file
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception as e:
        print(f"Error reading state file: {str(e)}", file=sys.stderr)
        sys.exit(1)

    # Restore browsers
    for browser in state.get('browsers', []):
        exe = browser.get('exe')
        if exe in [None, ""]:
            if not browser.get('browser') in EXE_PATHS.keys():
                print("Can't find the executable path for ", browser.get('browser'))
                continue
            else:
                exe = EXE_PATHS.get(browser.get('browser'))

        restore_browser(browser.get('browser'), browser.get('windows', []), exe)
        # if browser['browser'] == 'chrome':
        #     restore_browser('chrome', browser.get('windows', []), CHROME_PATH)
        # elif browser['browser'] == 'edge':
        #     restore_browser('edge', browser.get('windows', []), EDGE_PATH)

    # Restore apps
    for app in state.get('apps', []):
        # Filter out non-existing files (moved/deleted)
        existing_items = [f for f in app.get('items', []) if os.path.exists(f)]
        restore_app_files(app.get('exe'), existing_items, app.get('name'), app.get('windowInfo'))

if __name__ == "__main__":
    main()