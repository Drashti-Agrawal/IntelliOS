#!/usr/bin/env python3
"""
IntelliOS - Agentic AI Framework for Proactive Workspace Management
Main entry point for the modular system
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def run_api_server():
    """Run the FastAPI server"""
    from api.server import app
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)

def run_log_processor():
    """Run the log processing pipeline"""
    from pipeline.log_processor import parse_arguments, process_logs
    args = parse_arguments()
    
    # Set up logging level
    os.environ['LOG_LEVEL'] = args.log_level
    
    # Calculate fetch time
    from datetime import datetime, timedelta, timezone
    fetch_since = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    
    # Process logs
    parsed_logs = process_logs(args.channel, fetch_since, args.limit)
    
    # Handle vector database operations
    if args.use_vector_db:
        from storage.vector_db import VectorDBManager
        vector_db = VectorDBManager()
        for log in parsed_logs:
            vector_db.add_log(log)
        print(f"Stored {len(parsed_logs)} logs in vector database")
    
    if args.query_vector_db:
        from storage.vector_db import VectorDBManager
        vector_db = VectorDBManager()
        results = vector_db.query_logs(args.query_vector_db, args.query_results)
        print(f"Query results for '{args.query_vector_db}':")
        for result in results:
            print(f"- {result['summary']} (score: {result['score']:.3f})")
    
    if args.clear_vector_db:
        from storage.vector_db import VectorDBManager
        vector_db = VectorDBManager()
        vector_db.clear_all_logs()
        print("Vector database cleared")
    
    if args.print_logs:
        print(f"\nProcessed {len(parsed_logs)} logs:")
        for log in parsed_logs:
            print(f"- {log['summary']}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='IntelliOS - Agentic AI Framework')
    parser.add_argument(
        'command',
        choices=['server', 'process-logs'],
        help='Command to run: server (API server) or process-logs (log processing)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'server':
        print("Starting IntelliOS API server...")
        run_api_server()
    elif args.command == 'process-logs':
        print("Running log processing pipeline...")
        run_log_processor()

if __name__ == "__main__":
    main()
