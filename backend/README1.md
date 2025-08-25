# IntelliOS Log Processing System

This system provides automated log parsing for Windows Event Logs using a hybrid funnel approach:
1. First attempts parsing with deterministic regex patterns
2. Falls back to LLM-based parsing for logs that don't match patterns

## Setup

### Prerequisites
- Python 3.8+
- Windows Operating System (for Windows Event Log access)
- Groq API key for LLM fallback

### Installation

1. Install required packages:
```
pip install win32evtlog groq instructor pydantic
```

2. Set environment variables:
```
# For PowerShell:
$env:GROQ_API_KEY = "your-groq-api-key"

# For CMD:
set GROQ_API_KEY=your-groq-api-key
```

## Usage

Run the script with minimal logging (default):
```
python main.py
```

Run with comprehensive logging:
```
python main.py --log-level 2
```

Specify a different Windows Event Log channel:
```
python main.py --channel Application
```

Process logs from a specific time range:
```
python main.py --hours 12
```

Combine options:
```
python main.py --log-level 2 --channel Security --hours 48
```

## Log Levels

- **Level 1 (Minimal)**: Basic information about processing stages and results
- **Level 2 (Comprehensive)**: Detailed debugging information, including regex matches and parsing details

## Architecture

The system follows a hybrid funnel architecture:
1. `log_fetcher.py`: Retrieves logs from Windows Event Logs
2. `regex_parsers.py`: Contains regex patterns for deterministic parsing
3. `llm_layer.py`: Provides LLM-based parsing using Groq's API
4. `config.py`: Defines the schema for structured log output
5. `main.py`: Orchestrates the entire process
6. `logging_config.py`: Configures the logging system

## Output

Logs are stored in the `logs` directory with timestamps in the filename.
