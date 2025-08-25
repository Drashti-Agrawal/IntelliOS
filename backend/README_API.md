# IntelliOS API Server

This API server provides REST endpoints for the IntelliOS Log Processing System. It allows you to process Windows Event Logs, match them with topics, and query them through a convenient API.

## Installation

### Prerequisites
- Python 3.8+
- Windows Operating System (for Windows Event Log access)
- Groq API key for LLM fallback
- Required Python packages

### Install Required Packages

```
pip install pywin32 groq instructor pydantic sentence-transformers chromadb fastapi uvicorn
```

## Starting the Server

```
python server.py
```

The server will start on port 8000 by default. You can access the API documentation at http://localhost:8000/docs.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/topics` | GET | List available topics |
| `/api/process-logs` | POST | Start processing logs in the background |
| `/api/logs` | GET | Get logs processed by the background task |
| `/api/real-time-logs` | GET | Process logs in real-time |
| `/api/query-logs` | POST | Query logs in vector DB |
| `/api/vector-db-stats` | GET | Get DB statistics |
| `/api/clear-vector-db` | POST | Clear vector DB |

## Usage Examples

### Processing Logs (Background)

```
POST http://localhost:8000/api/process-logs?channel=System&hours=1&limit=10
```

Parameters:
- `channel`: Windows Event Log channel to process (default: System)
- `hours`: Process logs from the last N hours (default: 1)
- `limit`: Maximum number of logs to process (default: 10)
- `with_topics`: Whether to match logs with topics (default: true)

### Getting Processed Logs

```
GET http://localhost:8000/api/logs
```

### Processing Logs (Real-time)

```
GET http://localhost:8000/api/real-time-logs?channel=System&hours=1&limit=5
```

Parameters:
- Same as for `/api/process-logs`

### Querying Logs

```
POST http://localhost:8000/api/query-logs?query=network%20connection&results=3
```

Parameters:
- `query`: Text to search for in logs
- `results`: Number of results to return (default: 5)

### Getting Vector Database Stats

```
GET http://localhost:8000/api/vector-db-stats
```

### Clearing Vector Database

```
POST http://localhost:8000/api/clear-vector-db
```

## Testing the API

A test script is provided to test all API endpoints:

```
python test_server.py
```

This script will:
1. Check if the API is running
2. Get available topics
3. Start log processing
4. Wait for processing to complete
5. Get processed logs
6. Try real-time log processing
7. Query the vector database
8. Get vector database stats
