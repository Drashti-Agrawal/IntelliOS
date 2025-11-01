"""
browser_capture.py - Module for capturing browser states
"""
import os
import json
import requests
from datetime import datetime, timezone
# requires: pip install websocket-client
import time
from websocket import create_connection
from datetime import datetime, timezone

def get_tab_launch_time(ws_url, timeout=5.0):
    """
    Connects to a single tab via WebSocket and retrieves performance.timeOrigin.
    Returns an ISO timestamp string (UTC) or None on failure.
    """
    if not ws_url:
        print("[ERROR] WebSocket URL is empty or invalid")
        return None
        
    print(f"\n[INFO] Connecting to WebSocket: {ws_url}")
    try:
        # Add additional headers that might be required for authentication
        headers = {
            "Origin": "http://localhost",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        ws = create_connection(ws_url, timeout=timeout, header=headers)
        print("[DEBUG] WebSocket connection established.")

        # Enable Runtime domain
        ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        print("[DEBUG] Sent Runtime.enable command.")
        time.sleep(0.5)  # wait briefly for the context to initialize

        # Evaluate JS expression
        request = {
            "id": 2,
            "method": "Runtime.evaluate",
            "params": {
                "expression": "performance.timeOrigin",
                "returnByValue": True
            }
        }
        ws.send(json.dumps(request))
        print("[DEBUG] Sent Runtime.evaluate command for performance.timeOrigin.")

        # Wait for result
        while True:
            msg = ws.recv()
            data = json.loads(msg)
            # Uncomment for detailed debugging:
            # print("[RAW MESSAGE]", json.dumps(data, indent=2))

            if data.get("id") == 2:
                val = data.get("result", {}).get("result", {}).get("value")
                if val is not None:
                    ts = float(val)
                    dt = datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)
                    print(f"[SUCCESS] Launch time found: {dt.isoformat()}")
                    return dt.isoformat()
                else:
                    print("[WARN] performance.timeOrigin returned None or undefined.")
                    return None

    except Exception as e:
        print(f"[ERROR] Failed to get timeOrigin: {e}")
        return None
    finally:
        try:
            ws.close()
            print("[DEBUG] WebSocket connection closed.")
        except Exception:
            pass

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
                    "id": tab.get("id"),
                    "url": tab.get("url"),
                    "title": tab.get("title"),
                    "description": tab.get("description", ""),
                    "tab_launched_at": get_tab_launch_time(tab.get("webSocketDebuggerUrl"))
                })
        return formatted_tabs
    except Exception:
        return []

def _parse_ts(ts):
    """Parse timestamp string or numeric to a timezone-aware datetime in UTC.

    Supports ISO-8601 strings handled by datetime.fromisoformat and numeric
    epoch seconds.
    Returns None if parsing fails.
    """
    if ts is None:
        return None
    # If already a datetime, normalize
    if isinstance(ts, datetime):
        if ts.tzinfo is None:
            return ts.replace(tzinfo=timezone.utc)
        return ts.astimezone(timezone.utc)

    # Try ISO format
    try:
        dt = datetime.fromisoformat(str(ts))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        pass

    # Try numeric epoch
    try:
        f = float(ts)
        return datetime.fromtimestamp(f, tz=timezone.utc)
    except Exception:
        return None


def capture_browser_states(browser_data):
    """Capture states of all browsers.

    If the environment variable `LAST_CAPTURED` is set (ISO or epoch), only
    instances with `launched_at` > LAST_CAPTURED will be included. If
    `launched_at` is missing for an instance, it will be included.
    """

    last_captured_str = os.environ.get('LAST_CAPTURED')
    last_captured_ts = _parse_ts(last_captured_str) if last_captured_str else None

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
                if instance.get("status") != "active":
                    continue

                launched_at_raw = instance.get("launched_at")
                launched_at_ts = _parse_ts(launched_at_raw)

                # If LAST_CAPTURED is set and we have a launched_at, include only newer instances
                if last_captured_ts and launched_at_ts:
                    if not (launched_at_ts > last_captured_ts):
                        # skip instances launched at or before last_captured
                        continue

                port = instance.get("port")
                try:
                    port_int = int(port)
                except Exception:
                    port_int = None

                tabs = get_devtools_tabs(f"http://localhost:{port_int}") if port_int else []

                if tabs:
                    window = {
                        "profile": profile_path,
                        "debuggingPort": int(port_int) if port_int else None,
                        "tabs": tabs,
                        "window_launched_at": launched_at_raw
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

if __name__ == "__main__":
    get_tab_launch_time("ws://localhost:9222/devtools/page/1BFD30030A13EDAAE9253A4CFFB61C06")