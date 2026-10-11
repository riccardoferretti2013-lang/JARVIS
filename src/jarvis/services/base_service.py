from abc import ABC


class BaseService(ABC):
    def __init__(self, name: str):
        self._name = name
        self._initialized = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def initialized(self) -> bool:
        return self._initialized

    def initialize(self):
        self._initialized = True

    def shutdown(self):
        self._initialized = False

    def status(self) -> str:
        return "Online" if self._initialized else "Offline"