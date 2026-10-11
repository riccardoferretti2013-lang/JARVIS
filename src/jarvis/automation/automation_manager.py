from ..computer import ApplicationCommands
from .routine import Routine
from .routines import WorkRoutine


class AutomationManager:
    """
    Gestisce le routine automatiche
    di J.A.R.V.I.S.
    """

    def __init__(
        self,
        application_commands: (
            ApplicationCommands
            | None
        ) = None,
    ) -> None:

        self._application_commands = (
            application_commands
            or ApplicationCommands()
        )

        self._routines: list[
            Routine
        ] = [
            WorkRoutine(
                application_commands=(
                    self._application_commands
                )
            ),
        ]

    def process(
        self,
        command: str,
    ) -> str | None:

        clean_command = (
            command
            .strip()
            .lower()
        )

        if not clean_command:
            return None

        for routine in self._routines:

            if not routine.matches(
                clean_command
            ):
                continue

            return routine.execute()

        return None

    def get_routines(
        self,
    ) -> tuple[Routine, ...]:

        return tuple(
            self._routines
        )