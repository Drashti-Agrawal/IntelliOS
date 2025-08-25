# IntelliOS Log Processing System

Quick reference guide for the Windows Event Log processing system with hybrid parsing, vector database integration, and topic matching.

## Setup

```powershell
pip install pywin32 groq pydantic instructor chromadb sentence-transformers
```

## Commands by Purpose

### Basic Log Processing

```powershell
# Process System logs with minimal logging
python main.py

# Process System logs with comprehensive logging
python main.py --log-level 2

# Process Application logs
python main.py --channel Application

# Process logs from last 12 hours
python main.py --hours 12

# Process limited number of logs
python main.py --limit 10

# Print parsed logs to console
python main.py --print-logs
```

### Vector Database & Topic Matching

```powershell
# Store logs in vector database
python main.py --use-vector-db

# Process and show topic matches for logs
python main.py --channel System --limit 10 --use-vector-db --print-logs

# Control number of topic matches shown
python main.py --channel System --limit 10 --use-vector-db --print-logs --topic-matches 5

# Query vector database for similar logs
python main.py --query-vector-db "HTTP requests" --query-results 3

# Clear vector database
python main.py --clear-vector-db
```

### Common Combinations

```powershell
# Small sample for testing
python main.py --channel System --hours 1 --limit 5 --print-logs

# Complete processing with topic matching
python main.py --channel System --log-level 2 --limit 100 --use-vector-db --print-logs
```

## Command Arguments Reference

| Argument | Purpose | Default |
|----------|---------|---------|
| `--log-level 1` | Minimal logging | Default |
| `--log-level 2` | Detailed logging | |
| `--channel System` | Process System logs | Default |
| `--channel Application` | Process Application logs | |
| `--hours 24` | Last 24 hours of logs | Default |
| `--limit 10` | Process only 10 logs | |
| `--print-logs` | Show results in console | |
| `--use-vector-db` | Store in vector database | |
| `--query-vector-db "text"` | Search vector database | |
| `--query-results 5` | Return 5 search results | Default |
| `--clear-vector-db` | Reset vector database | |
| `--topic-matches 3` | Show 3 topic matches per log | Default |

## Topics Available

The system matches logs against the following predefined topics:

- `security`: Security-related events including authentication, authorization
- `system_startup`: System startup, boot, and initialization events
- `system_shutdown`: System shutdown, restart, and power-off events
- `service_operations`: Service start, stop, pause, and configuration events
- `application_lifecycle`: Application start, stop, crash, and update events
- `network_activity`: Network connections and communication events
- `driver_operations`: Device driver installation, updates, and issues
- `hardware_events`: Hardware-related events including device connections
- `updates`: System and application update events
- `user_sessions`: User login, logout, and session-related events
- `disk_activity`: Disk operations, errors, and storage-related events
- `performance_issues`: Performance bottlenecks and resource usage
- `system_errors`: Critical system errors and failures
- `application_errors`: Application crashes, hangs, and errors
- `maintenance`: System maintenance and cleanup activities
