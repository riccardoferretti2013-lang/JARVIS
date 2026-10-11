import re


class PronunciationEngine:
    """
    Corregge la pronuncia di termini tecnici e nomi propri
    prima che il testo venga inviato al motore TTS.

    Il testo visualizzato all'utente non viene modificato.
    """

    def __init__(self) -> None:
        self._replacements: dict[str, str] = {
            "J.A.R.V.I.S.": "Jarvis",
            "JARVIS": "Jarvis",
            "Python": "Paiton",
            "GitHub": "Ghit Hab",
            "Visual Studio Code": "Visual Studio Coud",
            "VS Code": "Visual Studio Coud",
            "Windows": "Uindous",
            "OpenAI": "Open A I",
            "Ollama": "Ol lama",
            "Qwen": "Quen",
            "SQL": "esse qu elle",
            "API": "a pi i",
            "AI": "a i",
            "CPU": "ci pi u",
            "GPU": "gi pi u",
            "RAM": "ram",
            "SSD": "esse esse di",
            "USB": "u esse bi",
            "HTML": "acca ti emme elle",
            "CSS": "ci esse esse",
            "JSON": "geison",
            "False": "falso",
            "True": "vero",
            "None": "nan",
            "Boolean": "bulian",
            "bool": "bul",
            "string": "stringa",
            "integer": "intero",
            "float": "flot",
        }

        self._compiled_patterns = self._build_patterns()

    def process(self, text: str) -> str:
        """
        Restituisce il testo adattato alla pronuncia vocale.
        """

        if not text:
            return ""

        processed_text = text

        for pattern, replacement in self._compiled_patterns:
            processed_text = pattern.sub(
                replacement,
                processed_text,
            )

        return processed_text.strip()

    def add_replacement(
        self,
        term: str,
        pronunciation: str,
    ) -> None:
        """
        Aggiunge o aggiorna una regola di pronuncia.
        """

        clean_term = term.strip()
        clean_pronunciation = pronunciation.strip()

        if not clean_term:
            raise ValueError(
                "Il termine originale non può essere vuoto."
            )

        if not clean_pronunciation:
            raise ValueError(
                "La pronuncia non può essere vuota."
            )

        self._replacements[clean_term] = clean_pronunciation
        self._compiled_patterns = self._build_patterns()

    def remove_replacement(self, term: str) -> None:
        """
        Rimuove una regola di pronuncia.
        """

        clean_term = term.strip()

        if clean_term in self._replacements:
            del self._replacements[clean_term]
            self._compiled_patterns = self._build_patterns()

    def get_replacements(self) -> dict[str, str]:
        """
        Restituisce una copia del dizionario delle pronunce.
        """

        return dict(self._replacements)

    def _build_patterns(
        self,
    ) -> list[tuple[re.Pattern[str], str]]:
        """
        Prepara le espressioni regolari utilizzate
        per sostituire i termini.
        """

        patterns: list[tuple[re.Pattern[str], str]] = []

        sorted_replacements = sorted(
            self._replacements.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for term, pronunciation in sorted_replacements:
            escaped_term = re.escape(term)

            pattern = re.compile(
                rf"(?<!\w){escaped_term}(?!\w)",
                flags=re.IGNORECASE,
            )

            patterns.append(
                (
                    pattern,
                    pronunciation,
                )
            )

        return patterns