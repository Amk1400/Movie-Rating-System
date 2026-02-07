import os
import logging
from logging.config import dictConfig


def setup_logging() -> None:
    """Configure application logging (console output)."""
    level = os.getenv("LOG_LEVEL", "INFO").upper()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": level,
                }
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
        }
    )

    # Optional: reduce uvicorn access noise or keep consistent level
    logging.getLogger("uvicorn.access").setLevel(os.getenv("UVICORN_ACCESS_LOG_LEVEL", level))