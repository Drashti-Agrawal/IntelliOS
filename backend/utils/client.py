# """
# client.py - Simple test client for the IntelliOS API
# Demonstrates how to use the API endpoints
# """
# import requests
# import time
# import json
# from typing import Dict, Any
# from rich.console import Console
# from rich.table import Table
# from rich.panel import Panel
# from rich import box

# # API base URL
# BASE_URL = "http://localhost:8000"

# # Initialize Rich console
# console = Console()

# def print_header(text: str):
#     """Print a header with the given text"""
#     console.print(f"\n[bold blue]{text}[/bold blue]")
#     console.print("=" * 80)

# def print_log_entry(log: Dict[str, Any], include_topics: bool = True):
#     """Print a log entry with its topic matches if available"""
#     console.print(f"[bold]{log.get('event_type', 'Unknown')}: {log.get('summary', 'No summary')}[/bold]")
    
#     # Print basic log details
#     details = Table(show_header=False, box=box.SIMPLE)
#     details.add_column("Key", style="cyan")
#     details.add_column("Value")
    
#     for key, value in log.items():
#         if key != "topic_matches" and value is not None:
#             details.add_row(key, str(value))
    
#     console.print(details)
    
#     # Print topic matches if available
#     if include_topics and "topic_matches" in log and log["topic_matches"]:
#         topics_table = Table(title="Topic Matches", box=box.ROUNDED)
#         topics_table.add_column("Topic", style="green")
#         topics_table.add_column("Score", style="yellow")
#         topics_table.add_column("Description")
        
#         for match in log["topic_matches"]:
#             topics_table.add_row(
#                 match.get("topic", ""),
#                 str(match.get("score", "")),
#                 match.get("description", "")
#             )
        
#         console.print(topics_table)
    
#     console.print("\n")

# def test_api():
#     """Test the IntelliOS API endpoints"""
#     try:
#         # Check if API is running
#         print_header("Checking API Status")
#         response = requests.get(f"{BASE_URL}/")
#         if response.status_code == 200:
#             console.print("[green]API is online![/green]")
#         else:
#             console.print("[red]API is not responding correctly.[/red]")
#             return
        
#         # Get available topics
#         print_header("Available Topics")
#         response = requests.get(f"{BASE_URL}/api/topics")
#         topics = response.json().get("topics", {})
        
#         topics_table = Table(title="Available Topics", box=box.ROUNDED)
#         topics_table.add_column("Topic", style="green")
#         topics_table.add_column("Description")
        
#         for topic, description in topics.items():
#             topics_table.add_row(topic, description)
        
#         console.print(topics_table)
        
#         # Start log processing
#         print_header("Starting Log Processing")
#         # Process last 1 hour of logs, limit to 5 entries, include topic matching
#         response = requests.post(
#             f"{BASE_URL}/api/process-logs?channel=System&hours=1&limit=5&with_topics=true"
#         )
        
#         if response.status_code == 200:
#             console.print("[green]Log processing started![/green]")
#             job_response = response.json()
#             console.print(f"Status: {job_response.get('status')}")
#         else:
#             console.print("[red]Failed to start log processing.[/red]")
#             return
        
#         # Wait for processing to complete
#         console.print("\n[yellow]Waiting for log processing to complete...[/yellow]")
#         time.sleep(5)  # Give some time for background processing
        
#         # Get processed logs
#         print_header("Processed Logs")
#         response = requests.get(f"{BASE_URL}/api/logs")
        
#         if response.status_code == 200:
#             logs_data = response.json()
#             logs = logs_data.get("logs", [])
            
#             if logs:
#                 console.print(f"[green]Found {len(logs)} processed logs[/green]")
#                 console.print(f"Total logs processed: {logs_data.get('total_logs_processed')}")
#                 console.print(f"Parsed with regex: {logs_data.get('regex_parsed')}")
#                 console.print(f"Parsed with LLM: {logs_data.get('llm_parsed')}")
#                 console.print(f"Failed to parse: {logs_data.get('failed_to_parse')}")
                
#                 print_header("Log Entries with Topic Matches")
#                 for log in logs:
#                     print_log_entry(log)
#             else:
#                 console.print("[yellow]No logs have been processed yet. The background task might still be running.[/yellow]")
#         else:
#             console.print("[red]Failed to retrieve processed logs.[/red]")
        
#         # Query vector database
#         print_header("Querying Vector Database")
#         query_text = "HTTP requests"
#         response = requests.post(f"{BASE_URL}/api/query-logs?query={query_text}&results=3")
        
#         if response.status_code == 200:
#             query_data = response.json()
#             query_logs = query_data.get("logs", [])
            
#             if query_logs:
#                 console.print(f"[green]Found {len(query_logs)} logs matching query: '{query_text}'[/green]")
                
#                 for log in query_logs:
#                     print_log_entry(log, include_topics=False)  # Topic matches might not be in query results
#             else:
#                 console.print(f"[yellow]No logs found matching query: '{query_text}'[/yellow]")
#         else:
#             console.print("[red]Failed to query vector database.[/red]")
        
#         # Get vector database stats
#         print_header("Vector Database Stats")
#         response = requests.get(f"{BASE_URL}/api/vector-db-stats")
        
#         if response.status_code == 200:
#             stats_data = response.json()
#             stats = stats_data.get("stats", {})
            
#             stats_table = Table(title="Vector Database Statistics", box=box.ROUNDED)
#             stats_table.add_column("Metric", style="cyan")
#             stats_table.add_column("Value", style="yellow")
            
#             for key, value in stats.items():
#                 stats_table.add_row(key, str(value))
            
#             console.print(stats_table)
#         else:
#             console.print("[red]Failed to get vector database stats.[/red]")
        
#     except requests.exceptions.ConnectionError:
#         console.print("[bold red]Error: Could not connect to the API server.[/bold red]")
#         console.print("Make sure the server is running with 'python server.py'")
#     except Exception as e:
#         console.print(f"[bold red]Error: {str(e)}[/bold red]")

# if __name__ == "__main__":
#     print_header("IntelliOS API Test Client")
#     test_api()
