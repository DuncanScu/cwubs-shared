from __future__ import annotations

import sys
from os import getenv

from loguru import logger


def serialize_log(record: dict) -> str:
    """
    Serialize log record to JSON format for production.
    """
    import json

    log_data = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "message": record["message"],
        "service": "users-service",
    }

    # Add any extra fields from the record
    if record.get("extra"):
        log_data.update(record["extra"])

    # Add exception info if present
    if record.get("exception"):
        log_data["exception"] = record["exception"]

    return json.dumps(log_data)


def setup_logging() -> None:
    """
    Configure application-wide logging using Loguru.
    Uses JSON format for production, human-readable format for local development.
    """
    log_level = getenv("LOG_LEVEL", "INFO").upper()
    environment = getenv("ENVIRONMENT", "development")

    # Remove default logger
    logger.remove()

    if environment == "production":
        # JSON format for production
        logger.add(
            sys.stdout,
            level=log_level,
            serialize=True,
            format=serialize_log,
        )
    else:
        # Human-readable format for development
        logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True,
        )

    # Suppress noisy loggers
    logger.disable("sqlalchemy.engine")
    logger.disable("uvicorn.access")


def get_logger(name: str):
    """
    Get a logger instance for a specific module.
    Returns a contextual logger bound with the module name.
    """
    return logger.bind(name=name)
