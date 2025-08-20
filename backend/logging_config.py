import os
import logging
import logging.handlers
from datetime import datetime

# Create log directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Log file name with timestamp
log_file = os.path.join(log_dir, f'intellios_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Define two logging levels
LOG_LEVELS = {
    "1": logging.INFO,     # Minimal logging
    "2": logging.DEBUG     # Comprehensive logging
}

def setup_logging(level="1"):
    """
    Configure logging for the application.
    
    Args:
        level: "1" for minimal logging, "2" for comprehensive logging
    """
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
    if level == "1":  # Minimal format
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
    root_logger.info(f"Logging initialized at {'MINIMAL' if level == '1' else 'COMPREHENSIVE'} level")
    if level == "2":
        root_logger.debug("Debug logging is enabled")
        
    return root_logger
