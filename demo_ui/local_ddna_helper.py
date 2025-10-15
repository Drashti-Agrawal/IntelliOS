"""
local_ddna_helper.py - Helper functions to access local DDNA data without requiring the server
"""
import os
import glob
import json
from typing import List, Dict, Any, Optional

# Define paths
BACKEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
LOCAL_DDNA_DIR = os.path.join(BACKEND_DIR, 'local_ddna')


def get_local_ddna_topics() -> Dict[str, Any]:
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
        return {
            "topics": [],
            "count": 0,
            "status": "error",
            "message": f"Error getting local DDNA topics: {str(e)}"
        }


def get_local_ddna_topic(
    topic: str,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "timestamp",
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """Get logs for a specific local DDNA topic"""
    try:
        # Build file path
        file_path = os.path.join(LOCAL_DDNA_DIR, f"{topic}.json")
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "topic": topic,
                "logs": [],
                "count": 0,
                "total": 0,
                "status": "error",
                "message": f"Topic file not found: {topic}.json"
            }
            
        # Read JSON file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            return {
                "topic": topic,
                "logs": [],
                "count": 0,
                "total": 0,
                "status": "error",
                "message": f"Invalid JSON in topic file: {topic}.json"
            }
            
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
    except Exception as e:
        return {
            "topic": topic,
            "logs": [],
            "count": 0,
            "total": 0,
            "status": "error",
            "message": f"Error getting local DDNA topic {topic}: {str(e)}"
        }


def get_latest_local_ddna(topics: Optional[List[str]] = None, limit: int = 5) -> Dict[str, Any]:
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
            # Validate that specified topics exist
            json_files = [f for f in os.listdir(LOCAL_DDNA_DIR) if f.endswith('.json')]
            available_topics = [os.path.splitext(f)[0] for f in json_files]
            topic_list = [t for t in topics if t in available_topics]
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
                # Continue with other topics
                pass
        
        return {
            "latest_logs": latest_logs,
            "topics_count": len(latest_logs),
            "status": "success"
        }
    except Exception as e:
        return {
            "latest_logs": {},
            "topics_count": 0,
            "status": "error",
            "message": f"Error getting latest local DDNA logs: {str(e)}"
        }


def get_local_ddna_stats() -> Dict[str, Any]:
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
                stats["logs_by_topic"][topic] = -1  # Indicate error
        
        return {
            **stats,
            "status": "success"
        }
    except Exception as e:
        return {
            "topics": 0,
            "total_logs": 0,
            "logs_by_topic": {},
            "status": "error",
            "message": f"Error getting local DDNA stats: {str(e)}"
        }


def search_local_ddna(
    query: str,
    case_sensitive: bool = False,
    topics: Optional[List[str]] = None
) -> Dict[str, Any]:
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
            # Validate that specified topics exist
            json_files = [f for f in os.listdir(LOCAL_DDNA_DIR) if f.endswith('.json')]
            available_topics = [os.path.splitext(f)[0] for f in json_files]
            topic_list = [t for t in topics if t in available_topics]
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
                # Continue with other topics
                pass
                
        return {
            "query": query,
            "results": results,
            "total_matches": total_matches,
            "matched_topics": len(results),
            "status": "success"
        }
    except Exception as e:
        return {
            "query": query,
            "results": {},
            "total_matches": 0,
            "matched_topics": 0,
            "status": "error",
            "message": f"Error searching local DDNA: {str(e)}"
        }
