import os
import logging

# Configure logging
log_dir = './log'
log_file = 'log.log'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if not logger.handlers:
    # Define the format of log messages
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s"
    )
    
    # Create the file handler
    file_path = os.path.join(log_dir, log_file)
    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(formatter)
    
    # (Optional) You could also add a StreamHandler to output to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


