#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from browser_restore import restore_browsers
from app_restore import restore_apps
import uvicorn
from typing import Optional

app = FastAPI(
    title="State Restoration API",
    description="API for restoring browser and application states",
    version="1.0.0"
)

class RestoreRequest(BaseModel):
    state_file_path: str

class RestoreResponse(BaseModel):
    status: str
    message: str
    details: Optional[dict] = None

@app.post("/restore", response_model=RestoreResponse)
async def restore_state(request: RestoreRequest):
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
        if not os.path.exists(request.state_file_path):
            raise HTTPException(
                status_code=404,
                detail=f"State file not found: {request.state_file_path}"
            )

        # Read state file
        try:
            with open(request.state_file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except Exception as e:
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
            raise HTTPException(
                status_code=500,
                detail=f"Error restoring browsers: {str(e)}"
            )

        # Restore apps
        try:
            restore_apps(state)
            restoration_details["apps_restored"] = True
        except Exception as e:
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
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("restore_api:app", host="0.0.0.0", port=5000, reload=True)