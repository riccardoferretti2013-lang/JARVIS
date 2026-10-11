import logging
from pathlib import Path

from .base_service import BaseService


class LoggerService(BaseService):
    def __init__(self):
        super().__init__("Logger")

        self.logger = logging.getLogger("JARVIS")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

    def initialize(self):
        if self.initialized:
            return

        log_folder = Path("logs")
        log_folder.mkdir(exist_ok=True)

        log_file = log_folder / "jarvis.log"

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s"
        )

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        self.logger.handlers.clear()
        self.logger.addHandler(file_handler)

        super().initialize()

        self.info("Logger inizializzato.")

    def shutdown(self):
        if not self.initialized:
            return

        self.info("Logger arrestato.")

        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

        super().shutdown()

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)