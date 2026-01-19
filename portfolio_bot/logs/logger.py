"""
Logging Configuration for Portfolio Bot

LEARNING NOTES:
---------------
This module sets up structured logging for the application. Good logging is
essential for debugging and monitoring production applications.

Key concepts:
1. Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
2. Log formatting with timestamps and context
3. Module-specific loggers for better filtering

WHAT YOU'LL LEARN:
- Python's logging module basics
- Creating reusable logger factory functions
- Configuring log formats and handlers
"""

import logging
import sys
from typing import Optional

from portfolio_bot.configs.app_config import get_config


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ of the calling module).
              If None, returns the root logger.

    Returns:
        logging.Logger: Configured logger instance.

    Usage:
        from portfolio_bot.logs.logger import get_logger
        logger = get_logger(__name__)
        logger.info("This is an info message")
        logger.error("This is an error", exc_info=True)

    LEARNING NOTE: Using __name__ as the logger name creates a hierarchy
    that matches your module structure, making it easy to filter logs.
    """
    config = get_config()

    # Get or create logger
    logger = logging.getLogger(name or "portfolio_bot")

    # Only configure if not already configured (prevents duplicate handlers)
    if not logger.handlers:
        # Set log level from configuration
        log_level = getattr(logging, config.log_level.upper(), logging.INFO)
        logger.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Create formatter
        # Format: 2024-01-15 10:30:45 | INFO | module_name | Message here
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

        # Prevent propagation to root logger (avoids duplicate logs)
        logger.propagate = False

    return logger


def setup_logging() -> None:
    """
    Initialize logging for the entire application.

    Call this once at application startup (e.g., in main.py).

    LEARNING NOTE: This function configures the root logger and sets
    log levels for noisy third-party libraries.
    """
    config = get_config()
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from third-party libraries
    # These libraries can be very verbose at DEBUG level
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)

    # Log startup message
    logger = get_logger("portfolio_bot")
    logger.info(f"Logging initialized at {config.log_level} level")
