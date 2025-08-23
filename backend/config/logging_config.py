import os
import logging
import logging.handlers
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

# Set default values for required environment variables
if 'VECTOR_DB_PATH' not in os.environ:
    os.environ['VECTOR_DB_PATH'] = 'vector_db'
if 'LOG_LEVEL' not in os.environ:
    os.environ['LOG_LEVEL'] = 'INFO'

# Create log directory if it doesn't exist - use path from environment or default
log_dir = os.getenv("LOG_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'))
os.makedirs(log_dir, exist_ok=True)

# Log file name with timestamp
log_file = os.path.join(log_dir, f'intellios_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Define logging levels mapping
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    # For backwards compatibility
    "1": logging.INFO,     # Minimal logging
    "2": logging.DEBUG     # Comprehensive logging
}

def setup_logging(level=None):
    """
    Configure logging for the application.
    
    Args:
        level: Logging level string ("DEBUG", "INFO", etc.) or legacy level ("1", "2")
               If None, uses the LOG_LEVEL from environment variables
    """
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")
    
    # Get the numeric logging level
    numeric_level = LOG_LEVELS.get(level, logging.INFO)
    
    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create handlers
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(numeric_level)
    
    # Create formatters
    if numeric_level == logging.INFO:  # Minimal format
        log_format = '%(asctime)s [%(levelname)s] %(message)s'
    else:  # Comprehensive format
        log_format = '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
    
    formatter = logging.Formatter(log_format)
    
    # Set formatters
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Log the level being used
    root_logger.info(f"Logging initialized at {logging.getLevelName(numeric_level)} level")
    if numeric_level == logging.DEBUG:
        root_logger.debug("Debug logging is enabled")
        
    return root_logger
