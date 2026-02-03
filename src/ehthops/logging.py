"""
Logging utilities for the EHT HOPS pipeline.
"""

import logging


def setup_logging(verbose=False, logger_name='ehthops'):
    """
    Setup logging configuration for the EHT HOPS pipeline.
    
    Args:
        verbose (bool): If True, set logging level to DEBUG, otherwise INFO
        logger_name (str): Name of the logger to create
        
    Returns:
        logging.Logger: Configured logger instance
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(logger_name)


def get_logger(name='ehthops'):
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Name of the logger
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
