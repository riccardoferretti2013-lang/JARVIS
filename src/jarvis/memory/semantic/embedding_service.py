from ollama import Client, ResponseError


class EmbeddingService:
    """
    Genera embeddings tramite Ollama.
    """

    def __init__(
        self,
        model: str = "embeddinggemma",
        host: str = "http://localhost:11434",
    ) -> None:
        self._model = model
        self._client = Client(
            host=host
        )

    @property
    def model_name(self) -> str:
        return self._model

    def is_available(self) -> bool:
        try:
            self._client.list()
            return True

        except Exception:
            return False

    def embed(
        self,
        text: str,
    ) -> list[float]:
        clean_text = text.strip()

        if not clean_text:
            return []

        try:
            response = self._client.embed(
                model=self._model,
                input=clean_text,
            )

            if not response.embeddings:
                return []

            return [
                float(value)
                for value in response.embeddings[0]
            ]

        except ResponseError as error:
            raise RuntimeError(
                f"Errore embeddings Ollama: {error.error}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                "Errore durante la generazione "
                f"dell'embedding: {error}"
            ) from error