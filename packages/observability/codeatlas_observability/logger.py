import logging
import sys

def get_logger(service_name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Creates and configures a standard stream logger for services.
    
    :param service_name: Name of the active service (e.g. 'api', 'analyzer')
    :param level: Minimum logging severity level
    :return: Configured logging.Logger instance
    """
    logger = logging.getLogger(service_name)
    
    # Avoid duplicate handlers if already configured
    if not logger.handlers:
        logger.setLevel(level)
        
        # Format string: [TIMESTAMP] [SERVICE_NAME] [LEVEL]: MESSAGE
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(name)s] [%(levelname)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Print output to stdout
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger