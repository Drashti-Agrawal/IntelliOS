from state_manager import State

def simulate_restore(state: State):
    """
    Simulate restoring browsers and apps from the given state.
    Prints instructions for each.
    """
    if state.browsers:
        for browser in state.browsers:
            tab_count = sum(len(w.tabs) for w in browser.windows)
            print(f"Open {browser.browser} with {len(browser.windows)} windows and {tab_count} tabs")
    if state.apps:
        for app in state.apps:
            if app.files:
                files = app.files if isinstance(app.files, list) else [app.files]
                print(f"Open {app.name} with files: {', '.join(files)}")
            else:
                print(f"Open {app.name}")