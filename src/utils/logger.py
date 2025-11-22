"""
Logging utilities for ingestion pipeline
"""


class IngestionLogger:
    """
    Simple logger for ingestion processes

    Provides consistent formatting for console output
    """

    def __init__(self, prefix=""):
        self.prefix = prefix

    def info(self, message):
        """Log informational message"""
        print(f"{self.prefix}{message}")

    def success(self, message):
        """Log success message"""
        print(f"{self.prefix}✅ {message}")

    def warning(self, message):
        """Log warning message"""
        print(f"{self.prefix}⚠️ {message}")

    def error(self, message):
        """Log error message"""
        print(f"{self.prefix}❌ {message}")

    def progress(self, current, total, message=""):
        """Log progress update"""
        print(f"{self.prefix}[{current}/{total}] {message}")

    def separator(self, char="-", length=50):
        """Print separator line"""
        print(char * length)
