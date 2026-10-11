from .wake_word_detector import WakeWordDetector


def main() -> None:
    detector = WakeWordDetector()

    print("In ascolto...")
    print("Pronuncia: Hey Jarvis")

    detected = detector.listen_once()

    if detected:
        print("Wake Word rilevata!")


if __name__ == "__main__":
    main()