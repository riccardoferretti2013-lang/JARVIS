from ..audio.audio_engine import AudioEngine
from ..config.configuration import Configuration
from ..config.settings_manager import SettingsManager
from ..core.router import CommandRouter

from .base_service import BaseService
from .logger_service import LoggerService


class ServiceManager:

    def __init__(self):
        self.config = Configuration()

        self.settings = SettingsManager()
        self.settings.load()

        self.logger = LoggerService()

        self.audio = AudioEngine(
            settings=self.settings,
            logger=self.logger
        )

        self.router = CommandRouter()

        self._services: list[BaseService] = []

        self.register(self.logger)
        self.register(self.audio)

    def register(self, service: BaseService) -> None:
        if service in self._services:
            return

        self._services.append(service)

    def initialize(self) -> None:
        for service in self._services:
            try:
                if not service.initialized:
                    service.initialize()

                    if service is not self.logger:
                        self.logger.info(
                            f"Servizio inizializzato: {service.name}"
                        )

            except Exception as error:
                if self.logger.initialized:
                    self.logger.error(
                        f"Errore inizializzazione servizio "
                        f"{service.name}: {error}"
                    )

                raise

    def shutdown(self) -> None:
        for service in reversed(self._services):
            try:
                if service.initialized:
                    if service is not self.logger:
                        self.logger.info(
                            f"Arresto servizio: {service.name}"
                        )

                    service.shutdown()

            except Exception as error:
                if self.logger.initialized:
                    self.logger.error(
                        f"Errore arresto servizio "
                        f"{service.name}: {error}"
                    )

    def get_status(self) -> dict[str, str]:
        return {
            service.name: service.status()
            for service in self._services
        }