import re

from src.jarvis.audio.feedback import (
    FeedbackPlayer,
    FeedbackSound,
)
from src.jarvis.audio.interrupt_listener import (
    InterruptListener,
)
from src.jarvis.core.assistant import Assistant
from src.jarvis.wakeword import (
    WakeWordManager,
    WakeWordSession,
)


EXIT_COMMANDS = {
    "esci",
    "exit",
    "quit",
    "chiudi",
    "chiudi jarvis",
    "spegni",
    "spegni jarvis",
    "termina",
    "termina jarvis",
}


WAKE_WORD_DISABLE_COMMANDS = {
    "disattiva wake word",
    "spegni wake word",
    "disabilita wake word",
}


WAKE_WORD_ENABLE_COMMANDS = {
    "attiva wake word",
    "accendi wake word",
    "abilita wake word",
}


WAKE_WORD_STATUS_COMMANDS = {
    "stato wake word",
    "wake word attiva",
    "wake word attivo",
    "informazioni wake word",
}


SESSION_CLOSE_COMMANDS = {
    "basta",
    "grazie jarvis",
    "puoi dormire",
    "torna in attesa",
    "fine conversazione",
}


SENSITIVITY_PATTERN = re.compile(
    (
        r"^(?:sensibilità|sensibilita)\s+"
        r"wake\s+word\s+"
        r"([0-9]*\.?[0-9]+)$"
    ),
    flags=re.IGNORECASE,
)


def normalize_command(
    command: str,
) -> str:
    return (
        command
        .strip()
        .lower()
        .replace("’", "'")
        .rstrip(".,!?")
    )


def main() -> None:

    jarvis = Assistant()

    wake_word = WakeWordManager()

    wake_session = WakeWordSession(
        timeout_seconds=8.0
    )

    feedback = FeedbackPlayer()

    interrupt_listener = None

    jarvis.start()

    try:
        interrupt_listener = InterruptListener(
            logger=jarvis.services.logger,
            cancel_callback=(
                jarvis.conversation
                .cancel_current_response
            ),
        )

        interrupt_listener.start()

        while True:

            if wake_word.enabled:

                if not wake_session.is_active:

                    print(
                        "\nJ.A.R.V.I.S. in attesa "
                        "della Wake Word..."
                    )

                    detected = (
                        wake_word
                        .wait_for_wake_word()
                    )

                    if not detected:
                        feedback.play(
                            FeedbackSound.ERROR
                        )

                        continue

                    feedback.play(
                        FeedbackSound.WAKE
                    )

                    wake_session.activate()

                    feedback.play(
                        FeedbackSound.LISTENING
                    )

                    jarvis.conversation.reply(
                        "Ti ascolto."
                    )

                remaining = (
                    wake_session
                    .remaining_seconds()
                )

                if remaining <= 0:

                    feedback.play(
                        FeedbackSound.TIMEOUT
                    )

                    wake_session.close()

                    feedback.play(
                        FeedbackSound.STANDBY
                    )

                    continue

                command = (
                    jarvis.conversation.listen(
                        timeout_seconds=remaining
                    )
                )

            else:

                wake_session.close()

                command = input(
                    "\nWake Word disattivata.\n"
                    "Scrivi un comando:\n"
                    "Tu: "
                )

            normalized_command = (
                normalize_command(
                    command
                )
            )

            if not normalized_command:

                if wake_word.enabled:

                    feedback.play(
                        FeedbackSound.TIMEOUT
                    )

                    wake_session.close()

                    print(
                        "\nTimeout raggiunto. "
                        "Ritorno in standby."
                    )

                    feedback.play(
                        FeedbackSound.STANDBY
                    )

                continue

            if normalized_command in EXIT_COMMANDS:

                feedback.play(
                    FeedbackSound.SUCCESS
                )

                break

            if (
                normalized_command
                in SESSION_CLOSE_COMMANDS
            ):

                wake_session.close()

                feedback.play(
                    FeedbackSound.STANDBY
                )

                jarvis.conversation.reply(
                    "Va bene."
                )

                continue

            if (
                normalized_command
                in WAKE_WORD_DISABLE_COMMANDS
            ):

                wake_word.disable()

                wake_session.close()

                feedback.play(
                    FeedbackSound.SUCCESS
                )

                jarvis.conversation.reply(
                    "Wake Word disattivata."
                )

                continue

            if (
                normalized_command
                in WAKE_WORD_ENABLE_COMMANDS
            ):

                wake_word.enable()

                wake_session.close()

                feedback.play(
                    FeedbackSound.SUCCESS
                )

                jarvis.conversation.reply(
                    "Wake Word attivata."
                )

                continue

            if (
                normalized_command
                in WAKE_WORD_STATUS_COMMANDS
            ):

                status = (
                    "attiva"
                    if wake_word.enabled
                    else "disattivata"
                )

                config = (
                    wake_word.detector.config
                )

                response = (
                    f"Wake Word: "
                    f"{config.model_name}\n"
                    f"Stato: {status}\n"
                    f"Sensibilità: "
                    f"{wake_word.sensitivity:.2f}\n"
                    f"Ultimo punteggio: "
                    f"{wake_word.last_score:.3f}"
                )

                feedback.play(
                    FeedbackSound.SUCCESS
                )

                jarvis.conversation.reply(
                    response
                )

                if wake_word.enabled:
                    wake_session.refresh()

                continue

            sensitivity_match = (
                SENSITIVITY_PATTERN.fullmatch(
                    normalized_command
                )
            )

            if sensitivity_match is not None:

                value = float(
                    sensitivity_match.group(1)
                )

                try:
                    new_value = (
                        wake_word.set_sensitivity(
                            value
                        )
                    )

                except ValueError:

                    feedback.play(
                        FeedbackSound.ERROR
                    )

                    jarvis.conversation.reply(
                        "La sensibilità deve essere "
                        "compresa tra zero e uno."
                    )

                    continue

                feedback.play(
                    FeedbackSound.SUCCESS
                )

                jarvis.conversation.reply(
                    "Sensibilità Wake Word "
                    "impostata su "
                    f"{new_value:.2f}."
                )

                if wake_word.enabled:
                    wake_session.refresh()

                continue

            feedback.play(
                FeedbackSound.SUCCESS
            )

            jarvis.process_command(
                normalized_command
            )

            if wake_word.enabled:
                wake_session.refresh()

    except KeyboardInterrupt:

        jarvis.conversation.cancel_current_response()

        feedback.play(
            FeedbackSound.STANDBY
        )

        print(
            "\nInterruzione richiesta "
            "dall'utente."
        )

    except Exception as error:

        feedback.play(
            FeedbackSound.ERROR
        )

        raise error

    finally:

        jarvis.conversation.cancel_current_response()

        if interrupt_listener is not None:
            interrupt_listener.stop()

        wake_session.close()

        wake_word.reset()

        jarvis.shutdown()


if __name__ == "__main__":
    main()