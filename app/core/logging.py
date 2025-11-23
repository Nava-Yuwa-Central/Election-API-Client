"""Logging configuration for the Nepal Entity Service."""

import logging
import sys
from typing import Any, Dict

from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO") -> None:
    """Setup structured JSON logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger()
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Set log level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter for adding context to logs."""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Add extra context to log messages.

        Args:
            msg: Log message
            kwargs: Additional keyword arguments

        Returns:
            Tuple of (message, kwargs)
        """
        # Add request_id if available
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        # Merge with existing extra fields
        kwargs["extra"].update(self.extra)
        
        return msg, kwargs


def get_logger(name: str, **extra: Any) -> LoggerAdapter:
    """Get a logger with extra context.

    Args:
        name: Logger name
        **extra: Additional context fields

    Returns:
        LoggerAdapter instance
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, extra)
