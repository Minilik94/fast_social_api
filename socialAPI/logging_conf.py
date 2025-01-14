import json
import logging
from logging.config import dictConfig

from rich.console import Console

from socialAPI.config import DevConfig, config


def obfuscated(email: str, obfuscation_length: int) -> str:
    characters = email[:obfuscation_length]
    first, last = email.split("@")
    return characters + ("*" * (len(first) - obfuscation_length)) + "@" + last


class EmailObfuscationFilter(logging.Filter):
    def __init__(self, name: str = "", obfuscated_length: int = 2) -> None:
        super().__init__(name)
        self.obfuscated_length = obfuscated_length

    def filter(self, record: logging.LogRecord) -> bool:
        if "email" in record.__dict__:
            record.email = obfuscated(record.email, self.obfuscate_length)
        return True


class RichJsonHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.console = Console()

    def emit(self, record):
        try:
            msg = self.format(record)
            try:
                parsed = json.loads(msg)
                self.console.print_json(data=parsed)
            except json.JSONDecodeError:
                self.console.print(msg)
        except Exception:
            self.handleError(record)


def configure_logging() -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "filters": {
                "correlation_id": {
                    "()": "asgi_correlation_id.CorrelationIdFilter",
                    "uuid_length": 32 if isinstance(config, DevConfig) else 8,
                    "default_value": "-",
                },
                "email_obfuscation": {
                    "()": EmailObfuscationFilter,
                    "obfuscated_length": 2 if isinstance(config, DevConfig) else 4,
                },
            },
            "formatters": {
                "console": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "(%(correlation_id)s) %(name)s - %(levelname)s - %(message)s",
                },
                "file": {
                    "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "format": "%(asctime)s %(levelname)s %(correlation_id)s %(name)s %(lineno)d %(funcName)s %(message)s",
                },
            },
            "handlers": {
                "rich_console": {
                    "class": "rich.logging.RichHandler",
                    "level": "DEBUG",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "json_console": {
                    "()": RichJsonHandler,
                    "level": "DEBUG",
                    "formatter": "file",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "rotating_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "file",
                    "filename": "socialAPI.log",
                    "maxBytes": 1024 * 1024,
                    "backupCount": 2,
                    "filters": ["correlation_id", "email_obfuscation"],
                },
                "logtail": {
                    "class": "logtail_handler.LogtailHandler",
                    "level": "DEBUG",
                    "token": "Mk8wZjtTNqcT4dgsewDPkHAK",
                    "formatter": "console",
                    "filters": ["correlation_id", "email_obfuscation"],
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": [
                        "rich_console",
                        "json_console",
                        "rotating_file",
                        "logtail",
                    ],
                    "level": "INFO",
                },
                "socialAPI": {
                    "handlers": [
                        "rich_console",
                        "json_console",
                        "rotating_file",
                        "logtail",
                    ],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "databases": {
                    "handlers": ["rich_console"],
                    "level": "WARNING",
                },
                "aiosqlite": {
                    "handlers": ["rich_console"],
                    "level": "WARNING",
                },
            },
        }
    )
