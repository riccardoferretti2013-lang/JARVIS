from ai.ollama_provider import OllamaProvider


def main():
    provider = OllamaProvider()

    print("=" * 50)
    print("J.A.R.V.I.S. - Ollama Test")
    print("=" * 50)

    while True:

        domanda = input("\nTu: ")

        if domanda.lower() == "esci":
            break

        risposta = provider.ask(domanda)

        print(f"\nJ.A.R.V.I.S.: {risposta}")


if __name__ == "__main__":
    main()