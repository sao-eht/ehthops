"""
Logging utilities for the EHT HOPS pipeline.
"""

import logging


def setup_logging(verbose: bool = False, logger_name: str = 'ehthops') -> logging.Logger:
    """
    Setup logging configuration for the EHT HOPS pipeline.
    
    Args:
        verbose: If True, set logging level to DEBUG, otherwise INFO
        logger_name: Name of the logger to create
        
    Returns:
        Configured logger instance
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(logger_name)


def get_logger(name: str = 'ehthops') -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
