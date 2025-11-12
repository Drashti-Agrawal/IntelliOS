#!/usr/bin/env python3

import os
import subprocess
import time
import sys
import psutil
import shutil
from datetime import datetime
try:
    import win32com.client  # type: ignore
except ImportError:  # pragma: no cover - optional convenience dependency
    win32com = None

# Directory to store profile copies
PROFILE_COPIES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profile_copies")

# Default browser paths
EXE_PATHS = {
    "chrome": [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ],
    "msedge": [
        "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    ],
    "opera": [
        "C:\\Users\\jaypa\\AppData\\Local\\Programs\\Opera\\opera.exe",
        "C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Opera\\opera.exe",
    ],
    "brave": [
        "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
        "C:\\Program Files (x86)\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    ],
    "firefox": [
        "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
    ],
}

SHORTCUT_DIRS = [
    os.path.join(os.environ.get("PROGRAMDATA", r"C:\\ProgramData"),
                 "Microsoft", "Windows", "Start Menu", "Programs"),
    os.path.join(os.environ.get("APPDATA", r"C:\\Users\\%USERNAME%\\AppData\\Roaming"),
                 "Microsoft", "Windows", "Start Menu", "Programs"),
]

SHORTCUT_NAMES = {
    "chrome": ["Google Chrome.lnk"],
    "msedge": ["Microsoft Edge.lnk"],
    "firefox": ["Mozilla Firefox.lnk"],
    "opera": ["Opera.lnk"],
    "brave": ["Brave.lnk", "Brave Browser.lnk"],
}


def _expand_path(path):
    return os.path.expandvars(os.path.expanduser(path)) if path else path


def resolve_browser_executable(browser, exe_hint=None):
    """Resolve an executable path for a browser using captured hints, defaults, or shortcuts."""
    candidates = []

    if exe_hint:
        candidates.append(_expand_path(exe_hint))

    for path in EXE_PATHS.get(browser.lower(), []):
        candidates.append(_expand_path(path))

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate

    # attempt to resolve from Start Menu shortcuts
    shortcut_names = SHORTCUT_NAMES.get(browser.lower(), [])
    if shortcut_names and win32com:
        try:
            shell = win32com.client.Dispatch("WScript.Shell")  # type: ignore[attr-defined]
            for directory in SHORTCUT_DIRS:
                if not directory:
                    continue
                for shortcut_name in shortcut_names:
                    shortcut_path = os.path.join(directory, shortcut_name)
                    if os.path.exists(shortcut_path):
                        try:
                            target = shell.CreateShortcut(shortcut_path).Targetpath
                        except Exception:
                            target = None
                        if target and os.path.exists(target):
                            return target
        except Exception:
            pass

    # fallback: try to locate via PATH
    if exe_hint:
        which_resolved = shutil.which(os.path.basename(exe_hint))
        if which_resolved:
            return which_resolved

    # last resort: return hint even if missing
    return exe_hint

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

def restore_browser(browser, windows, exe_hint):
    """Restore browser windows and their tabs"""
    if not windows or len(windows) == 0:
        return

    exe = resolve_browser_executable(browser, exe_hint)
    if not exe or not os.path.exists(exe):
        print(f"Error: Unable to resolve executable for {browser}", file=sys.stderr)
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

def restore_browsers(state):
    """Main function to restore all browsers from state"""
    for browser in state.get('browsers', []):
        exe_hint = browser.get('exe')
        restore_browser(browser.get('browser'), browser.get('windows', []), exe_hint)