import logging
import os

# Create a logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),  # General log file
        logging.FileHandler('logs/error.log', mode='w'),  # Error log file
        logging.FileHandler('logs/warning.log', mode='w'),  # Warning log file
        logging.FileHandler('logs/info.log', mode='w'),  # Info log file
        logging.FileHandler('logs/debug.log', mode='w'),  # Debug log file
        logging.StreamHandler()  # Output to console
    ]
)

# Create loggers for different levels
app_logger = logging.getLogger('app')
error_logger = logging.getLogger('error')
warning_logger = logging.getLogger('warning')
info_logger = logging.getLogger('info')
debug_logger = logging.getLogger('debug')

# Set specific levels for each logger
app_logger.setLevel(logging.DEBUG)
error_logger.setLevel(logging.ERROR)
warning_logger.setLevel(logging.WARNING)
info_logger.setLevel(logging.INFO)
debug_logger.setLevel(logging.DEBUG)

# Add specific handlers to each logger
app_log_handler = logging.FileHandler('logs/app.log')
error_log_handler = logging.FileHandler('logs/error.log')
warning_log_handler = logging.FileHandler('logs/warning.log')
info_log_handler = logging.FileHandler('logs/info.log')
debug_log_handler = logging.FileHandler('logs/debug.log')

app_logger.addHandler(app_log_handler)
error_logger.addHandler(error_log_handler)
warning_logger.addHandler(warning_log_handler)
info_logger.addHandler(info_log_handler)
debug_logger.addHandler(debug_log_handler)

# Example usage of loggers
app_logger.info("Application started")
error_logger.error("This is an error message")
warning_logger.warning("This is a warning message")
info_logger.info("This is an informational message")
debug_logger.debug("This is a debug message")
