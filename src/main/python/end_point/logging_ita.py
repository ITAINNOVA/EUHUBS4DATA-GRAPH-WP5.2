
import os
import logging

def configure():
    """
    Configures the logger based on the environment variable LOGLEVEL.
    
    Returns:
        logger (logging.Logger): The configured logger object.
    """
    # Get the log level from the environment variable LOGLEVEL, default to DEBUG if not set
    LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG').upper()
    
    # Create the logger object
    logger = logging.getLogger("logging_ita")
    logger.setLevel(logging.DEBUG)
    logger.setLevel(level=LOGLEVEL)
    
    # Create the console handler and set the log level
    ch = logging.StreamHandler()
    ch.setLevel(level=LOGLEVEL)
    
    # Create the formatter
    formatter = logging.Formatter(
        "%(asctime)s;%(levelname)s;%(lineno)d;%(filename)s;%(message)s", "%Y-%m-%d %H:%M:%S")
    
    # Add the formatter to the console handler
    ch.setFormatter(formatter)
    
    # Add the console handler to the logger if it doesn't already have handlers
    if not logger.hasHandlers():
        logger.addHandler(ch)
    
    return logger

application_logger = configure()