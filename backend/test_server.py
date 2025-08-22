"""
test_server.py - Simple script to test the IntelliOS API server
"""
import requests
import time
import json
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def print_separator():
    """Print a separator line"""
    print("="*80)

def print_header(text: str):
    """Print a header with the given text"""
    print("\n" + "="*80)
    print(f"{text}")
    print("="*80)

def test_api():
    """Test the IntelliOS API endpoints"""
    try:
        # Check if API is running
        print_header("Checking API Status")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("API is online!")
            print(f"Response: {response.json()}")
        else:
            print(f"API returned status code {response.status_code}")
            return
        
        # Get available topics
        print_header("Available Topics")
        response = requests.get(f"{BASE_URL}/api/topics")
        topics = response.json().get("topics", {})
        
        print(f"Found {len(topics)} topics:")
        for topic, description in topics.items():
            print(f"- {topic}: {description}")
        
        # Start log processing
        print_header("Starting Log Processing")
        # Process last 1 hour of logs, limit to 3 entries
        response = requests.post(
            f"{BASE_URL}/api/process-logs?channel=System&hours=1&limit=3"
        )
        
        if response.status_code == 200:
            print("Log processing started!")
            job_response = response.json()
            print(f"Status: {job_response.get('status')}")
        else:
            print(f"Failed to start log processing. Status code: {response.status_code}")
            return
        
        # Wait for processing to complete
        print("\nWaiting for log processing to complete...")
        attempt = 0
        max_attempts = 10
        
        while attempt < max_attempts:
            time.sleep(2)  # Wait 2 seconds between checks
            attempt += 1
            
            # Check logs
            logs_response = requests.get(f"{BASE_URL}/api/logs")
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                logs = logs_data.get("logs", [])
                
                if logs:
                    print("Processing complete!")
                    break
                else:
                    print(f"Check {attempt}/{max_attempts}: Still processing...")
            else:
                print(f"Failed to get logs. Status code: {logs_response.status_code}")
        
        if attempt >= max_attempts:
            print("Reached maximum attempts. The process might still be running.")
        
        # Get processed logs
        print_header("Processed Logs")
        response = requests.get(f"{BASE_URL}/api/logs")
        
        if response.status_code == 200:
            logs_data = response.json()
            logs = logs_data.get("logs", [])
            
            if logs:
                print(f"Found {len(logs)} processed logs")
                print(f"Total logs processed: {logs_data.get('total_logs_processed')}")
                print(f"Parsed with regex: {logs_data.get('regex_parsed')}")
                print(f"Parsed with LLM: {logs_data.get('llm_parsed')}")
                print(f"Failed to parse: {logs_data.get('failed_to_parse')}")
                
                print_header("Log Entries with Topic Matches")
                for i, log in enumerate(logs, 1):
                    print(f"\n{i}. {log.get('event_type')}: {log.get('summary')}")
                    
                    if 'topic_matches' in log:
                        print("  Topic Matches:")
                        for match in log['topic_matches']:
                            print(f"    - {match.get('topic')} (Score: {match.get('score'):.4f}): {match.get('description')}")
                    
                    print("  Full Log:")
                    for key, value in log.items():
                        if key != 'topic_matches':  # We already printed this above
                            print(f"    {key}: {value}")
            else:
                print("No logs have been processed yet. The background task might still be running.")
        else:
            print(f"Failed to retrieve processed logs. Status code: {response.status_code}")
        
        # Try real-time logs
        print_header("Real-time Logs")
        response = requests.get(f"{BASE_URL}/api/real-time-logs?channel=System&limit=2")
        
        if response.status_code == 200:
            real_time_data = response.json()
            real_time_logs = real_time_data.get("logs", [])
            
            if real_time_logs:
                print(f"Found {len(real_time_logs)} real-time logs")
                
                for i, log in enumerate(real_time_logs, 1):
                    print(f"\n{i}. {log.get('event_type')}: {log.get('summary')}")
                    
                    if 'topic_matches' in log:
                        print("  Topic Matches:")
                        for match in log['topic_matches']:
                            print(f"    - {match.get('topic')} (Score: {match.get('score'):.4f}): {match.get('description')}")
            else:
                print("No real-time logs found")
        else:
            print(f"Failed to get real-time logs. Status code: {response.status_code}")
        
        # Query vector database
        print_header("Querying Vector Database")
        query_text = "network connection"
        response = requests.post(f"{BASE_URL}/api/query-logs?query={query_text}&results=3")
        
        if response.status_code == 200:
            query_data = response.json()
            query_logs = query_data.get("logs", [])
            
            if query_logs:
                print(f"Found {len(query_logs)} logs matching query: '{query_text}'")
                
                for i, log in enumerate(query_logs, 1):
                    print(f"\n{i}. {log.get('event_type')}: {log.get('summary')}")
                    print("  Details:")
                    for key, value in log.items():
                        if key != 'topic_matches':  # Topic matches might not be in query results
                            print(f"    {key}: {value}")
            else:
                print(f"No logs found matching query: '{query_text}'")
        else:
            print(f"Failed to query vector database. Status code: {response.status_code}")
        
        # Get vector database stats
        print_header("Vector Database Stats")
        response = requests.get(f"{BASE_URL}/api/vector-db-stats")
        
        if response.status_code == 200:
            stats_data = response.json()
            stats = stats_data.get("stats", {})
            
            print("Vector Database Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
        else:
            print(f"Failed to get vector database stats. Status code: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API server.")
        print("Make sure the server is running with 'python server.py'")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print_header("IntelliOS API Test Client")
    test_api()
