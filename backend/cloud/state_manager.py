from typing import List, Optional, Union
from pydantic import BaseModel, ValidationError
import json

class Tab(BaseModel):
    url: str
    title: str
    active: Optional[bool] = None
    pinned: Optional[bool] = None

class Window(BaseModel):
    windowId: str
    tabs: List[Tab]

class Browser(BaseModel):
    browser: str
    port: Optional[int] = None
    windows: List[Window]

class App(BaseModel):
    name: str
    pid: Optional[int] = None
    exe: Optional[str] = None
    cmdline: Optional[str] = None
    files: Optional[Union[str, List[str]]] = None
    mainWindow: Optional[str] = None

class State(BaseModel):
    saved_at: Optional[str] = None
    user: Optional[str] = None
    browsers: Optional[List[Browser]] = []
    apps: Optional[List[App]] = []

def load_state(filename: str = "state.json") -> State:
    """Load state from a JSON file and validate using pydantic."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return State(**data)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading state: {e}")
        raise
    except ValidationError as ve:
        print(f"Schema validation error: {ve}")
        raise

def save_state(state: State, filename: str = "state.json"):
    """Save state to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(state.dict(), f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")
        raise

def print_state(state: State):
    """Pretty print the state: browsers, windows, tabs, and apps."""
    print(f"User: {state.user}")
    print(f"Saved at: {state.saved_at}")
    print("\nBrowsers:")
    if state.browsers:
        for browser in state.browsers:
            print(f"  Browser: {browser.browser} (port: {browser.port})")
            for window in browser.windows:
                print(f"    Window ID: {window.windowId}")
                for tab in window.tabs:
                    print(f"      Tab: '{tab.title}' ({tab.url})")
    print("\nApps:")
    if state.apps:
        for app in state.apps:
            print(f"  App: {app.name} (pid: {app.pid})")
            if app.files:
                if isinstance(app.files, list):
                    print(f"    Files: {', '.join(app.files)}")
                else:
                    print(f"    File: {app.files}")
            if app.mainWindow:
                print(f"    Main Window: {app.mainWindow}")