"""
server.py - FastAPI server for IntelliOS log processing system
Provides endpoints for real-time log processing and topic matching
"""
import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import json
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'State_capturing_engine')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Restoration_engine')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Configure_browsers')))
from browser_capture import capture_browser_states
from app_capture import capture_app_states
from browser_restore import restore_browsers
from app_restore import restore_apps
from create_browser_shortcuts import create_browser_shortcuts

# Load environment variables
load_dotenv()

# Add parent directory to path to import IntelliOS modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logging_config import setup_logging

# Set up the logger
logger = logging.getLogger(__name__)
setup_logging()  # Use environment variable LOG_LEVEL


# Initialize FastAPI app
app = FastAPI(
    title="IntelliOS API",
    description="API for IntelliOS Log Processing System",
    version="1.0.0",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define response models



class RestoreResponse(BaseModel):
    status: str
    message: str
    details: Optional[Dict[str, bool]] = None


class CaptureResponse(BaseModel):
    status: str
    message: str
    state: Optional[Dict[str, Any]] = None
    


# Routes
@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint - health check"""
    return {"status": "online", "message": "IntelliOS API is running"}
    
@app.get("/api/create_shortcuts")
async def create_shortcuts():
    try:
        create_browser_shortcuts()
        return {
            "status": "success",
            "message": "Shortcuts successfully created"
        }
    except Exception as e:
        logger.error(f"Error creating shortcuts : {e}")
        raise HTTPException(status_code=500, detail=f"Error creating shortcuts : {str(e)}")

# State Restoration endpoints
@app.post("/api/capture", response_model=CaptureResponse, tags=["State Management"])
async def capture_state():
    """
    Capture current system state and save it to a file
    
    Args:
        request: CaptureRequest containing paths for state.json and browser_ports.json
        
    Returns:
        CaptureResponse with status and message
    """
    try:
        state_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..\\State\\state.json"))
        browser_ports_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..\\State\\browser_ports.json"))
        # Ensure output directory exists
        os.makedirs(os.path.dirname(state_file_path), exist_ok=True)

        if not os.path.exists(browser_ports_file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Browser ports file not found: {browser_ports_file_path}"
            )
        
        # Read browser ports file
        browser_ports_data = {}
        try:
            with open(browser_ports_file_path, 'r', encoding='utf-8') as f:
                browser_ports_data = json.load(f)
        except Exception as e:
            logger.error(f"Error reading browser ports file: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error reading browser ports file: {str(e)}"
            )

        browsers = []
        apps = []
        #Capture browser states
        try:
            browsers = capture_browser_states(browser_ports_data)
        except Exception as e:
            logger.error(f"Error capturing browser states: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error capturing browser states: {str(e)}"
            )
        # Capture app states
        try:
            apps = capture_app_states()
        except Exception as e:
            logger.error(f"Error capturing app states: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error capturing app states: {str(e)}"
            )
        
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
            
        return CaptureResponse(
            status="success",
            message="State captured successfully",
            state=state
        )
            
    except Exception as e:
        logger.error(f"Error capturing state: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error capturing state: {str(e)}"
        )

@app.post("/api/restore", response_model=RestoreResponse, tags=["State Management"])
async def restore_state():
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
        state_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..\\State\\state.json"))

        if not os.path.exists(state_file_path):
            raise HTTPException(
                status_code=404,
                detail=f"State file not found: {state_file_path}"
            )

        # Read state file
        state = {}
        try:
            with open(state_file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except Exception as e:
            logger.error(f"Error reading state file: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error reading state file: {str(e)}"
            )

        restoration_details = {
            "browsers_restored": False,
            "apps_restored": False
        }

        # Restore browsers
        try:
            restore_browsers(state)
            restoration_details["browsers_restored"] = True
        except Exception as e:
            logger.error(f"Error restoring browsers: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error restoring browsers: {str(e)}"
            )

        # Restore apps
        try:
            restore_apps(state)
            restoration_details["apps_restored"] = True
        except Exception as e:
            logger.error(f"Error restoring apps: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error restoring apps: {str(e)}"
            )

        return RestoreResponse(
            status="success",
            message="State restored successfully",
            details=restoration_details
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in restore_state: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

if __name__ == "__main__":
    # Run the server
    # Note: reload=True watches the project files and restarts the process on any
    # file change. Many components write files under the repository (for
    # example state.json, logs, or vector DB files) which can trigger an
    # endless restart loop. For development use the CLI with --reload when
    # needed; here we disable reload to avoid watch-induced restart storms.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="127.0.0.1", port=port, reload=False)
