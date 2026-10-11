from openai import OpenAI

from config.settings import Settings


class JarvisOpenAIClient:
    """Gestisce il collegamento tra J.A.R.V.I.S. e OpenAI."""

    def __init__(self) -> None:
        if not Settings.OPENAI_API_KEY:
            raise ValueError(
                "Chiave OpenAI non trovata nel file .env."
            )

        self.client = OpenAI(
            api_key=Settings.OPENAI_API_KEY
        )

    def ask(self, message: str) -> str:
        """Invia un messaggio al modello e restituisce la risposta."""

        if not message.strip():
            return "Non hai scritto nessun messaggio."

        response = self.client.responses.create(
            model=Settings.OPENAI_MODEL,
            instructions=(
                "Sei J.A.R.V.I.S., un assistente personale intelligente. "
                "Rispondi sempre in italiano in modo chiaro e naturale."
            ),
            input=message,
        )

        return response.output_text