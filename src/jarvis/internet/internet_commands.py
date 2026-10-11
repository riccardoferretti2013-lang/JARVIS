import re


class InternetCommands:

    _PATTERNS = [
        re.compile(
            r"^cerca su internet\s+(.+)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^cerca sul web\s+(.+)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^cerca online\s+(.+)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^fai una ricerca su\s+(.+)$",
            re.IGNORECASE,
        ),
        re.compile(
            r"^cerca informazioni su\s+(.+)$",
            re.IGNORECASE,
        ),
    ]

    def extract_query(
        self,
        command: str,
    ) -> str | None:

        clean_command = (
            command.strip()
        )

        for pattern in self._PATTERNS:

            match = (
                pattern.match(
                    clean_command
                )
            )

            if match is None:
                continue

            query = (
                match.group(1)
                .strip()
            )

            if query:
                return query

        return None