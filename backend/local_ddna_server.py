"""
local_ddna_server.py - A simplified FastAPI server for accessing local DDNA files
This server only provides endpoints for viewing and searching local DDNA JSON files.
"""
import os
import glob
import json
import logging
from typing import List, Dict, Any, Optional, Union
from fastapi import FastAPI, Query, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DDNA_DIR = os.path.join(BACKEND_DIR, 'local_ddna')

# Initialize FastAPI app
app = FastAPI(
    title="IntelliOS Local DDNA API",
    description="Simplified API for accessing IntelliOS Local DDNA files",
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

# Define Pydantic models
class LocalDDNATopicsResponse(BaseModel):
    topics: List[str]
    count: int
    status: str

class LocalDDNALogEntry(BaseModel):
    event_type: str
    summary: str
    saved_at: str
    timestamp: str
    topic_score: Optional[float] = None
    topic_description: Optional[str] = None
    # Additional fields that might be present based on event_type
    app_name: Optional[str] = None
    exe_path: Optional[str] = None
    pid: Optional[int] = None
    window_count: Optional[int] = None
    captured_at: Optional[str] = None
    browser_name: Optional[str] = None
    url: Optional[str] = None
    domain: Optional[str] = None
    title: Optional[str] = None
    is_active: Optional[bool] = None
    tab_count: Optional[int] = None

class LocalDDNATopicResponse(BaseModel):
    topic: str
    logs: List[Union[LocalDDNALogEntry, Dict[str, Any]]]
    count: int
    total: int
    status: str

class LocalDDNASearchResponse(BaseModel):
    query: str
    results: Dict[str, List[Dict[str, Any]]]
    total_matches: int
    matched_topics: int
    status: str

# Routes
@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint - health check"""
    return {
        "status": "online", 
        "message": "IntelliOS Local DDNA API is running",
        "available_endpoints": [
            "/api/topics", 
            "/api/topic/{topic}", 
            "/api/search", 
            "/api/latest",
            "/api/stats"
        ]
    }

@app.get("/api/topics", response_model=LocalDDNATopicsResponse, tags=["Local DDNA"])
async def get_local_ddna_topics():
    """Get list of available local DDNA topics (JSON files)"""
    try:
        # Check if local DDNA directory exists
        if not os.path.exists(LOCAL_DDNA_DIR):
            return {
                "topics": [],
                "count": 0,
                "status": "warning",
                "message": f"Local DDNA directory not found at: {LOCAL_DDNA_DIR}"
            }
            
        # Get list of JSON files in the local DDNA directory
        json_files = glob.glob(os.path.join(LOCAL_DDNA_DIR, "*.json"))
        
        # Extract topic names from file paths
        topics = [os.path.splitext(os.path.basename(f))[0] for f in json_files]
        topics.sort()  # Sort alphabetically for consistency
        
        return {
            "topics": topics,
            "count": len(topics),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting local DDNA topics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting local DDNA topics: {str(e)}"
        )

@app.get("/api/topic/{topic}", response_model=LocalDDNATopicResponse, tags=["Local DDNA"])
async def get_local_ddna_topic(
    topic: str = Path(..., description="Topic name (without .json extension)"),
    limit: int = Query(100, description="Maximum number of logs to return"),
    offset: int = Query(0, description="Number of logs to skip from the beginning"),
    sort_by: str = Query("timestamp", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)")
):
    """Get logs for a specific local DDNA topic"""
    try:
        # Build file path
        file_path = os.path.join(LOCAL_DDNA_DIR, f"{topic}.json")
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Topic file not found: {topic}.json"
            )
            
        # Read JSON file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid JSON in topic file: {topic}.json"
            )
            
        # Validate sort order
        if sort_order.lower() not in ["asc", "desc"]:
            sort_order = "desc"
        
        # Sort logs
        reverse = sort_order.lower() == "desc"
        logs = sorted(logs, key=lambda x: x.get(sort_by, ""), reverse=reverse)
        
        # Apply pagination
        paginated_logs = logs[offset:offset + limit] if limit > 0 else logs[offset:]
        
        return {
            "topic": topic,
            "logs": paginated_logs,
            "count": len(paginated_logs),
            "total": len(logs),
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting local DDNA topic {topic}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting local DDNA topic {topic}: {str(e)}"
        )

@app.get("/api/search", response_model=LocalDDNASearchResponse, tags=["Local DDNA"])
async def search_local_ddna(
    query: str = Query(..., description="Search query string"),
    case_sensitive: bool = Query(False, description="Case sensitive search"),
    topics: str = Query(None, description="Comma-separated list of topics to search in")
):
    """Search across all local DDNA topic files or specific topics"""
    try:
        # Check if local DDNA directory exists
        if not os.path.exists(LOCAL_DDNA_DIR):
            return {
                "query": query,
                "results": {},
                "total_matches": 0,
                "matched_topics": 0,
                "status": "warning",
                "message": f"Local DDNA directory not found at: {LOCAL_DDNA_DIR}"
            }
        
        # Determine which topics to search
        topic_list = []
        if topics:
            topic_list = [t.strip() for t in topics.split(",")]
            # Validate that specified topics exist
            json_files = [f for f in os.listdir(LOCAL_DDNA_DIR) if f.endswith('.json')]
            available_topics = [os.path.splitext(f)[0] for f in json_files]
            topic_list = [t for t in topic_list if t in available_topics]
        else:
            # Search all topics
            json_files = [f for f in os.listdir(LOCAL_DDNA_DIR) if f.endswith('.json')]
            topic_list = [os.path.splitext(f)[0] for f in json_files]
        
        # Perform search across topics
        results = {}
        total_matches = 0
        
        for topic in topic_list:
            file_path = os.path.join(LOCAL_DDNA_DIR, f"{topic}.json")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                # Search in logs
                topic_matches = []
                for log in logs:
                    # Convert log to string for searching
                    log_str = json.dumps(log, ensure_ascii=False)
                    
                    # Perform search
                    if case_sensitive:
                        if query in log_str:
                            topic_matches.append(log)
                    else:
                        if query.lower() in log_str.lower():
                            topic_matches.append(log)
                
                # Add results if there are matches
                if topic_matches:
                    results[topic] = topic_matches
                    total_matches += len(topic_matches)
            except Exception as e:
                logger.warning(f"Error searching in topic {topic}: {e}")
                # Continue with other topics
                
        return {
            "query": query,
            "results": results,
            "total_matches": total_matches,
            "matched_topics": len(results),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error searching local DDNA: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching local DDNA: {str(e)}"
        )

@app.get("/api/latest", tags=["Local DDNA"])
async def get_latest_local_ddna(
    topics: str = Query(None, description="Comma-separated list of topics to get latest logs from"),
    limit: int = Query(5, description="Number of latest logs per topic")
):
    """Get the latest logs from each topic or specified topics"""
    try:
        # Check if local DDNA directory exists
        if not os.path.exists(LOCAL_DDNA_DIR):
            return {
                "latest_logs": {},
                "status": "warning",
                "message": f"Local DDNA directory not found at: {LOCAL_DDNA_DIR}"
            }
            
        # Determine which topics to get
        topic_list = []
        if topics:
            topic_list = [t.strip() for t in topics.split(",")]
            # Validate that specified topics exist
            json_files = [f for f in os.listdir(LOCAL_DDNA_DIR) if f.endswith('.json')]
            available_topics = [os.path.splitext(f)[0] for f in json_files]
            topic_list = [t for t in topic_list if t in available_topics]
        else:
            # Get from all topics
            json_files = [f for f in os.listdir(LOCAL_DDNA_DIR) if f.endswith('.json')]
            topic_list = [os.path.splitext(f)[0] for f in json_files]
        
        # Get latest logs from each topic
        latest_logs = {}
        
        for topic in topic_list:
            file_path = os.path.join(LOCAL_DDNA_DIR, f"{topic}.json")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                # Sort logs by timestamp in descending order
                logs_sorted = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)
                
                # Get the latest logs up to the limit
                latest_logs[topic] = logs_sorted[:limit]
                
            except Exception as e:
                logger.warning(f"Error getting latest logs from topic {topic}: {e}")
                # Continue with other topics
        
        return {
            "latest_logs": latest_logs,
            "topics_count": len(latest_logs),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting latest local DDNA logs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting latest local DDNA logs: {str(e)}"
        )

@app.get("/api/stats", tags=["Local DDNA"])
async def get_local_ddna_stats():
    """Get statistics about local DDNA data"""
    try:
        # Check if local DDNA directory exists
        if not os.path.exists(LOCAL_DDNA_DIR):
            return {
                "topics": 0,
                "total_logs": 0,
                "logs_by_topic": {},
                "status": "warning",
                "message": f"Local DDNA directory not found at: {LOCAL_DDNA_DIR}"
            }
            
        # Get list of JSON files
        json_files = [f for f in os.listdir(LOCAL_DDNA_DIR) if f.endswith('.json')]
        
        # Calculate statistics
        stats = {
            "topics": len(json_files),
            "logs_by_topic": {},
            "total_logs": 0,
            "logs_by_event_type": {},
            "timestamp_range": {
                "earliest": None,
                "latest": None
            }
        }
        
        for json_file in json_files:
            topic = os.path.splitext(json_file)[0]
            file_path = os.path.join(LOCAL_DDNA_DIR, json_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    
                # Count logs in this topic
                log_count = len(logs)
                stats["logs_by_topic"][topic] = log_count
                stats["total_logs"] += log_count
                
                # Count event types
                for log in logs:
                    event_type = log.get("event_type", "unknown")
                    stats["logs_by_event_type"][event_type] = stats["logs_by_event_type"].get(event_type, 0) + 1
                    
                    # Track timestamp range
                    if log.get("timestamp"):
                        if not stats["timestamp_range"]["earliest"] or log["timestamp"] < stats["timestamp_range"]["earliest"]:
                            stats["timestamp_range"]["earliest"] = log["timestamp"]
                        if not stats["timestamp_range"]["latest"] or log["timestamp"] > stats["timestamp_range"]["latest"]:
                            stats["timestamp_range"]["latest"] = log["timestamp"]
                            
            except Exception as e:
                logger.warning(f"Error processing topic {topic}: {e}")
                stats["logs_by_topic"][topic] = -1  # Indicate error
        
        return {
            **stats,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting local DDNA stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting local DDNA stats: {str(e)}"
        )

if __name__ == "__main__":
    # Run the server
    port = int(os.environ.get("PORT", 8080))  # Changed to port 8080
    print(f"Starting Local DDNA Server on port {port}...")
    print(f"Local DDNA directory: {LOCAL_DDNA_DIR}")
    if not os.path.exists(LOCAL_DDNA_DIR):
        print(f"Warning: Local DDNA directory does not exist at: {LOCAL_DDNA_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=port)