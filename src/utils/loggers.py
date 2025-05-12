"""LoggerFactory: A reusable logger setup utility with timestamped file output."""


from datetime import datetime
import logging
import os


class LoggerFactory:
    """Create and configure a logger with file and console output."""

    def __init__(self, logger_name: str, log_dir: str, log_file_base: str):
        """Initialize the logger factory.

        Args:
            logger_name (str): Unique name for the logger.
            log_dir (str): Directory where the log file will be stored.
            log_file_base (str): Base name of the log file (without timestamp).
        """
        self.logger_name = logger_name
        self.log_dir = log_dir
        self.log_file_base = log_file_base
        self.logger = logging.getLogger(self.logger_name)

    def get_logger(self) -> logging.Logger:
        """Set up and return a logger instance.

        Returns:
            logging.Logger: Configured logger instance.
        """
        if self.logger.handlers:
            return self.logger

        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        os.makedirs(self.log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{self.log_file_base}_{timestamp}.log"
        file_path = os.path.join(self.log_dir, log_filename)

        file_handler = logging.FileHandler(file_path, mode="w")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        return self.logger