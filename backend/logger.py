"""
logger.py - Logging Configuration
Centralized logging for the application
"""

import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Log file paths
ERROR_LOG = os.path.join(LOG_DIR, 'error.log')
INFO_LOG = os.path.join(LOG_DIR, 'info.log')
API_LOG = os.path.join(LOG_DIR, 'api.log')

def setup_logging():
    """Setup and configure logging for the application."""
    
    # Create logger
    logger = logging.getLogger('meeting_scheduler')
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Error Log Handler (WARNING and above)
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(detailed_formatter)
    
    # Info Log Handler (INFO and above)
    info_handler = logging.handlers.RotatingFileHandler(
        INFO_LOG,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(detailed_formatter)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(detailed_formatter)
    
    # Add handlers to logger
    logger.addHandler(error_handler)
    logger.addHandler(info_handler)
    logger.addHandler(console_handler)
    
    return logger

def setup_api_logger():
    """Setup separate logger for API requests/responses."""
    
    api_logger = logging.getLogger('api_logger')
    api_logger.setLevel(logging.INFO)
    
    # API formatter - more concise
    api_formatter = logging.Formatter(
        '%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # API Log Handler
    api_handler = logging.handlers.RotatingFileHandler(
        API_LOG,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(api_formatter)
    
    api_logger.addHandler(api_handler)
    
    return api_logger

# Initialize loggers
logger = setup_logging()
api_logger = setup_api_logger()

# Convenience functions
def log_info(message):
    """Log info level message."""
    logger.info(message)

def log_warning(message):
    """Log warning level message."""
    logger.warning(message)

def log_error(message, exc_info=False):
    """Log error level message."""
    logger.error(message, exc_info=exc_info)

def log_debug(message):
    """Log debug level message."""
    logger.debug(message)

def log_api_request(method, endpoint, user_id=None, status=None):
    """Log API request."""
    user_info = f" | User: {user_id}" if user_id else ""
    status_info = f" | Status: {status}" if status else ""
    api_logger.info(f"{method} {endpoint}{user_info}{status_info}")

def log_api_error(method, endpoint, error_message, user_id=None):
    """Log API error."""
    user_info = f" | User: {user_id}" if user_id else ""
    api_logger.error(f"{method} {endpoint} | Error: {error_message}{user_info}")

if __name__ == '__main__':
    # Test logging
    log_info("Application started")
    log_debug("Debug message")
    log_warning("Warning message")
    try:
        1 / 0
    except:
        log_error("An error occurred", exc_info=True)
    
    print("\n✅ Logging system initialized")
    print(f"  Error log: {ERROR_LOG}")
    print(f"  Info log: {INFO_LOG}")
    print(f"  API log: {API_LOG}")
