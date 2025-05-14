"""
logging.py 

@author: Matteo V. Rocco
@institution: Politecnico di Milano

This module defines the Logger class, which is used for logging throughout the 
package. It supports multiple formats and custom configurations specific to 
the needs of the application.

The Logger class provides a simplified interface for creating and managing 
logs at various levels (INFO, DEBUG, WARNING, ERROR, CRITICAL). It includes a 
method to generate child loggers that inherit properties from a parent logger, 
ensuring consistent log behavior across different modules of the package.
"""

import logging
import time

from contextlib import contextmanager
from typing import Literal


class Logger:
    """
    A customizable logging class for creating and managing logs in the application.

    The Logger provides facilities for logging messages with different importance 
    levels, ranging from debug messages to critical system messages. It is 
    designed to be easy to configure and use within a package, supporting 
    structured logging practices.

    Attributes:
        log_format (str): The format of the log messages. Choices are 'minimal' 
            or 'standard'.
        str_format (str): The string representation of the log format.
        logger (logging.Logger): The underlying logger instance from Python's 
            logging module.

    Args:
        logger_name (str): The name of the logger, defaults to 'default_logger'.
        log_level (str): The threshold for the logger, defaults to 'INFO'.
        log_format (str): The format used for log messages, defaults to 'minimal'.
    """

    LEVELS = {
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }

    FORMATS = {
        'minimal': '%(levelname)s | %(message)s',
        'standard': '%(levelname)s | %(name)s | %(message)s',
        'detailed': '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    }

    COLORS = {
        # set warning to orange
        'WARNING': '\033[38;5;214m',  # Orange
        'ERROR': '\033[31m',  # Red
        'DEBUG': '\033[32m',  # Green
        'RESET': '\033[0m',  # Reset to default
    }

    def __init__(
            self,
            logger_name: str = 'default_logger',
            log_level: Literal['INFO', 'DEBUG', 'WARNING', 'ERROR'] = 'INFO',
            log_format: Literal[
                'minimal', 'standard', 'detailed'] = 'standard',
    ) -> None:

        self.log_format = log_format
        self.str_format = self.FORMATS[log_format]
        self.logger = logging.getLogger(logger_name)

        if isinstance(log_level, str):
            level = self.LEVELS.get(log_level.upper(), logging.INFO)
        else:
            level = log_level

        self.logger.setLevel(level)

        if not self.logger.handlers:
            self.logger.setLevel(log_level)
            formatter = logging.Formatter(self.str_format)
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(log_level)
            stream_handler.setFormatter(self.get_colors(formatter))
            self.logger.addHandler(stream_handler)

    def get_colors(self, formatter):
        """
        Wraps the formatter to apply colors based on log level.
        """
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                color = Logger.COLORS.get(record.levelname, '')
                reset = Logger.COLORS['RESET']
                formatted = super().format(record)
                return f"{color}{formatted}{reset}"

        return ColoredFormatter(formatter._fmt)

    def get_child(self, name: str) -> 'Logger':
        """
        Creates and returns a child Logger with a specified name, inheriting 
        properties from this Logger instance.

        Args:
            name (str): The name identifier for the child logger, typically 
                __name__ from the module where the logger is used.

        Returns:
            Logger: A new Logger instance configured as a child of this one.
        """
        child_logger = self.logger.getChild(name.split('.')[-1])

        new_logger = Logger(
            logger_name=child_logger.name,
            log_level=child_logger.level,
            log_format=self.log_format,
        )

        new_logger.logger.propagate = False
        return new_logger

    def log(self, message: str, level: str = logging.INFO) -> None:
        """Basic log message. 

        Args:
            message (str): message to be displayed.
            level (str, optional): level of the log message. Defaults 
                to logging.INFO.
        """
        self.logger.log(msg=message, level=level)

    def info(self, message: str):
        """INFO log message."""
        self.logger.log(msg=message, level=logging.INFO)

    def debug(self, message: str):
        """DEBUG log message."""
        self.logger.log(msg=message, level=logging.DEBUG)

    def warning(self, message: str):
        """WARNING log message."""
        self.logger.log(msg=message, level=logging.WARNING)

    def error(self, message: str):
        """ERROR log message."""
        self.logger.log(msg=message, level=logging.ERROR)

    @contextmanager
    def log_timing(
            self,
            message: str,
            level: str = 'info',
            log_format: str = None,
            success: bool = True,
    ):
        """
        Context manager to time the execution of a code block and log the duration.

        Args:
            message (str): The message that will be logged at the start of the task.
            level (str): The log level for the messages (e.g., 'info', 'debug', etc.)
        """
        log_level = self.LEVELS.get(level.upper(), logging.INFO)
        log_function = getattr(
            self.logger,
            logging.getLevelName(log_level).lower()
        )

        log_function(message)
        status = {'success': success}

        if log_format:
            original_formatter = self.logger.handlers[0].formatter
            formatter = logging.Formatter(log_format)
            self.logger.handlers[0].setFormatter(formatter)
        else:
            original_formatter = None

        start_time = time.time()

        try:
            yield status
        except Exception:
            status['success'] = False
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            duration_str = \
                f"{int(duration // 60)}m {int(duration % 60)}s" \
                if duration > 60 else f"{duration:.2f} seconds"

            if status['success']:
                log_function(f"{message} DONE ({duration_str})")
            else:
                log_function(f"{message} FAILED ({duration_str})")

            if log_format:
                self.logger.handlers[0].setFormatter(original_formatter)


if __name__ == '__main__':
    logger = Logger(log_level='INFO', log_format='minimal')

    try:
        with logger.log_timing("Outer block"):
            with logger.log_timing("Inner block"):
                raise RuntimeError("Simulated failure")

    except RuntimeError as e:
        logger.error(f"Caught exception: {e}")
