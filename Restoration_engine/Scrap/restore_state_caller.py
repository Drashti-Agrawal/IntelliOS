import subprocess
import os

def restore_state(ps1_path="D:\\Major\\Restoration_engine\\Restore-State.ps1"):
    """
    Calls the Restore-State.ps1 PowerShell script from Python.
    """
    try:
        # Ensure the script exists
        if not os.path.exists(ps1_path):
            raise FileNotFoundError(f"Script not found: {ps1_path}")

        # Run the PowerShell script with ExecutionPolicy Bypass
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps1_path],
            capture_output=True,
            text=True,
            check=True
        )

        print("✅ Restore-State executed successfully.")
        if result.stdout:
            print("Output:\n", result.stdout)
        if result.stderr:
            print("Errors:\n", result.stderr)

    except subprocess.CalledProcessError as e:
        print("❌ Error running script:")
        print(e.stderr)
    except Exception as e:
        print("⚠️ Exception:", str(e))


if __name__ == "__main__":
    restore_state()
