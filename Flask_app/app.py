from datetime import datetime
import json

from pydantic import BaseModel
from flask import Flask, request, jsonify
import joblib
import io,os,sys
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'State_capturing_engine')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Restoration_engine')))
from browser_capture import capture_browser_states
from app_capture import capture_app_states
from browser_restore import restore_browsers
from app_restore import restore_apps

class CaptureResponse(BaseModel):
    status: str
    message: str
    saved_at: str
    file_path: str

app = Flask(__name__)
    

@app.route('/captureState', methods=['GET'])
def capture():
    try:
        state_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..\\State\\state.json"))
        browser_ports_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..\\State\\browser_ports.json"))
        # Ensure output directory exists
        os.makedirs(os.path.dirname(state_file_path), exist_ok=True)

        
        
        # Read browser ports file
        browser_ports_data = {}
        try:
            with open(browser_ports_file_path, 'r', encoding='utf-8') as f:
                browser_ports_data = json.load(f)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

        browsers = []
        apps = []
        #Capture browser states
        try:
            browsers = capture_browser_states(browser_ports_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        # Capture app states
        try:
            apps = capture_app_states()
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        
        # Create state object
        state = {
            "saved_at": datetime.now().isoformat(),
            "user": os.environ.get("USERNAME", ""),
            "browsers": browsers,
            "apps": apps
        }
        
        # Save state to file
        with open(state_file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
            
        return jsonify({
            "status":"success",
            "message":"State captured successfully",
            "saved_at":state["saved_at"],
            "file_path":state_file_path
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
@app.route('/restore_workspace', methods=['GET'])
def restore_workspace():
    """
    Restore system state from a state file
    
    Args:
        request: RestoreRequest containing the path to the state file
        
    Returns:
        RestoreResponse with status and message
        
    Raises:
        HTTPException: If there are any errors during the restoration process
    """
    try:
        
        # state_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..\\Workspaces", str(request.json.get('workspace'))+".json"))
        state_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..\\State\\state.json"))

        if not os.path.exists(state_file_path):
            return jsonify({'error': str(e)}), 400

        # Read state file
        state = {}
        try:
            with open(state_file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

        restoration_details = {
            "browsers_restored": False,
            "apps_restored": False
        }

        # Restore browsers
        try:
            restore_browsers(state)
            restoration_details["browsers_restored"] = True
        except Exception as e:
            return jsonify({'error': str(e)}), 400

        # Restore apps
        try:
            restore_apps(state)
            restoration_details["apps_restored"] = True
        except Exception as e:
            return jsonify({'error': str(e)}), 400

        return jsonify({
            "status":"success",
            "message":"State restored successfully",
            "details":restoration_details
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400
# @app.route('/getWorkspaces', methods=['GET'])
# def getWorkspaces():
#     try: 

#     except Exception as e:
#         return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
