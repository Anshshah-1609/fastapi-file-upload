"""Centralized logging configuration module."""

from __future__ import annotations

import inspect
import logging
import sys

# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    DEBUG = "\033[0m"  # White
    INFO = "\033[32m"   # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"  # Red
    CRITICAL = "\033[35m"  # Magenta
    RESET = "\033[0m"   # Reset
    BOLD = "\033[1m"    # Bold


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels."""

    def __init__(self, *args, use_colors: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors for the entire line."""
        # Collect extra fields (excluding standard LogRecord attributes)
        standard_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
            'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname',
            'process', 'processName', 'relativeCreated', 'thread', 'threadName',
            'exc_info', 'exc_text', 'stack_info', 'taskName'
        }
        
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                extra_fields[key] = value
        
        # Format the base message first
        formatted = super().format(record)
        
        # Append extra fields if they exist
        if extra_fields:
            extra_str = " | ".join(f"{k}={v}" for k, v in extra_fields.items())
            formatted = f"{formatted} | {extra_str}"
        
        if self.use_colors:
            # Wrap the entire formatted message with color based on log level
            if record.levelno == logging.DEBUG:
                formatted = f"{Colors.DEBUG}{formatted}{Colors.RESET}"
            elif record.levelno == logging.INFO:
                formatted = f"{Colors.INFO}{formatted}{Colors.RESET}"
            elif record.levelno == logging.WARNING:
                formatted = f"{Colors.WARNING}{formatted}{Colors.RESET}"
            elif record.levelno == logging.ERROR:
                formatted = f"{Colors.ERROR}{formatted}{Colors.RESET}"
            elif record.levelno == logging.CRITICAL:
                formatted = f"{Colors.BOLD}{Colors.CRITICAL}{formatted}{Colors.RESET}"

        return formatted


# Configure logging once when this module is imported
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    ColoredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[handler],
)


def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger instance for the given module name.

    Args:
        name: The name of the module. If None, uses the caller's module name.

    Returns:
        A configured Logger instance.
    """
    if name is None:
        # Get the caller's module name
        frame = inspect.currentframe()
        if frame and frame.f_back:
            caller_frame = frame.f_back
            name = caller_frame.f_globals.get("__name__", "app")
        else:
            name = "app"

    return logging.getLogger(name)
