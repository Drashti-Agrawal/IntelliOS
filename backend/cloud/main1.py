import argparse
from state_manager import State, App, Window, Tab, load_state, save_state, print_state
import sync

def sample_state() -> State:
    """
    Generate a sample state for demonstration.
    """
    return State(apps=[
        App(
            name="Chrome",
            tabs=[
                Tab(url="https://github.com", title="GitHub"),
                Tab(url="https://intellios.ai", title="IntelliOS")
            ]
        ),
        App(
            name="VSCode",
            windows=[
                Window(project="IntelliOS", open_files=["main.py", "state_manager.py"])
            ]
        )
    ])

def main():
    parser = argparse.ArgumentParser(description="IntelliOS State Manager CLI")
    parser.add_argument("command", choices=["save", "load", "push", "pull", "show"], help="Command to run")
    args = parser.parse_args()

    if args.command == "save":
        state = sample_state()
        save_state(state)
        print("Sample state saved to state.json.")
    elif args.command == "load":
        state = load_state()
        print(state)
    elif args.command == "push":
        sync.push_state()
    elif args.command == "pull":
        sync.pull_state()
    elif args.command == "show":
        state = load_state()
        print_state(state)

if __name__ == "__main__":
    main()