import logging
import os
import sys

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
    
    # Create logger
    logger = logging.getLogger(name)
    
    # If logger already has handlers, assume it's configured
    if logger.handlers:
        return logger
        
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, LOG_LEVEL))
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger
