from ai.openai_client import JarvisOpenAIClient


def main() -> None:
    try:
        ai_client = JarvisOpenAIClient()

        print("Connessione a OpenAI in corso...")

        risposta = ai_client.ask(
            "Ciao, presentati brevemente come J.A.R.V.I.S."
        )

        print("\nRisposta ricevuta:")
        print(risposta)

    except Exception as error:
        print("\nSi è verificato un errore:")
        print(error)


if __name__ == "__main__":
    main()