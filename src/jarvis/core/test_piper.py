from pathlib import Path
import wave
import winsound

from piper import PiperVoice


MODEL = Path(
    "assets/voices/it_IT-riccardo-x_low.onnx"
)

OUTPUT = Path("test_piper.wav")


def main() -> None:
    print("Caricamento modello...")

    voice = PiperVoice.load(str(MODEL))

    print("Generazione audio...")

    with wave.open(str(OUTPUT), "wb") as wav_file:
        voice.synthesize_wav(
            (
                "Ciao Riccardo. "
                "Io sono Jarvis. "
                "Finalmente abbiamo una voce tutta nuova."
            ),
            wav_file,
        )

    print("Riproduzione audio...")

    winsound.PlaySound(
        str(OUTPUT),
        winsound.SND_FILENAME,
    )

    print("Test completato!")


if __name__ == "__main__":
    main()