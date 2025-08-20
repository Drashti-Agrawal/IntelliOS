# config.py
from pydantic import BaseModel, Field
from typing import Optional, Literal

# Logging is now configured in main.py

class ActivityLog(BaseModel):
    """Schema for a single structured log event."""
    event_type: Literal[
        "file_interaction", 
        "app_lifecycle", 
        "system_event", 
        "application_crash", 
        "service_event", 
        "power_event", 
        "dcom_event", 
        "file_system_event", 
        "unknown"
    ] = Field(
        ..., description="The high-level category of the event."
    )
    event_subtype: Optional[str] = Field(None, description="A more specific categorization within the event type.")
    app_name: Optional[str] = Field(None, description="The name of the application involved.")
    file_path: Optional[str] = Field(None, description="The full path to the file involved.")
    status: Optional[str] = Field(None, description="Status or result of the event.")
    operation_code: Optional[str] = Field(None, description="Operation code for events that use them.")
    summary: str = Field(..., description="A brief, factual summary of the log entry.")
