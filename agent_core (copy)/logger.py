# agent_core/logger.py
"""
Système de logging
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


class Logger:
    """Gestionnaire de logging"""

    def __init__(self, name: str = "agent", level: str = "INFO", log_file: Optional[str] = None):
        self.name = name
        self.level = getattr(logging, level.upper())
        self.log_file = log_file
        self._setup_logger()

    def _setup_logger(self):
        """Configure le logger"""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)
        self.logger.propagate = False

        if self.logger.handlers:
            return

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

        # Handler console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Handler fichier
        if self.log_file:
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_file,
                maxBytes=10 * 1024 * 1024,
                backupCount=3,
                encoding='utf-8'
            )
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        return self.logger


def setup_logger(name: str = "agent", level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    return Logger(name, level, log_file).get_logger()