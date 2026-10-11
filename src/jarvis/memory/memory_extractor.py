import re
from collections.abc import Callable

from .memory import Memory, MemoryType


MemoryExtractorFunction = Callable[[str], Memory | None]


class MemoryExtractor:
    """
    Estrae automaticamente ricordi permanenti
    dai messaggi dell'utente.
    """

    def extract(
        self,
        text: str,
    ) -> list[Memory]:

        clean_text = text.strip()

        if not clean_text:
            return []

        extractors: list[MemoryExtractorFunction] = [
            self._extract_name,
            self._extract_preferred_name,
            self._extract_birth_date,
            self._extract_age,
            self._extract_city,
            self._extract_school,
            self._extract_job,
            self._extract_hobby,
            self._extract_pet,
            self._extract_goal,
            self._extract_favorite_language,
            self._extract_favorite_color,
            self._extract_operating_system,
            self._extract_project,
            self._extract_favorite_browser,
            self._extract_favorite_editor,
            self._extract_favorite_theme,
            self._extract_favorite_music,
        ]

        memories: list[Memory] = []

        for extractor in extractors:
            memory = extractor(
                clean_text
            )

            if memory is not None:
                memories.append(
                    memory
                )

        return memories

    @staticmethod
    def _create_memory(
        key: str,
        value: str,
        memory_type: MemoryType,
        importance: int,
    ) -> Memory:

        return Memory(
            key=key,
            value=value.strip(),
            memory_type=memory_type,
            importance=importance,
        )

    @staticmethod
    def _match(
        pattern: str,
        text: str,
    ) -> str | None:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match is None:
            return None

        return (
            match.group(1)
            .strip()
            .rstrip(".,!?")
        )

    def _extract_name(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:mi chiamo|"
                r"il mio nome è)\s+"
                r"([A-Za-zÀ-ÿ'-]+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="nome_utente",
            value=value.title(),
            memory_type=MemoryType.PROFILE,
            importance=10,
        )

    def _extract_preferred_name(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            r"\bchiamami\s+([A-Za-zÀ-ÿ0-9'_-]+)",
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="nome_preferito",
            value=value,
            memory_type=MemoryType.PREFERENCE,
            importance=10,
        )

    def _extract_birth_date(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:sono nato il|"
                r"sono nata il|"
                r"la mia data di nascita è)\s+"
                r"(.+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="data_nascita",
            value=value,
            memory_type=MemoryType.PROFILE,
            importance=9,
        )

    def _extract_age(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            r"\bho\s+(\d{1,3})\s+anni\b",
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="eta",
            value=value,
            memory_type=MemoryType.PROFILE,
            importance=8,
        )

    def _extract_city(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:abito a|"
                r"vivo a|"
                r"sono di)\s+"
                r"([A-Za-zÀ-ÿ' -]+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="citta",
            value=value.title(),
            memory_type=MemoryType.PROFILE,
            importance=8,
        )

    def _extract_school(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:frequento|"
                r"vado alla scuola|"
                r"studio alla scuola|"
                r"studio presso)\s+"
                r"(.+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="scuola",
            value=value,
            memory_type=MemoryType.PROFILE,
            importance=8,
        )

    def _extract_job(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:lavoro come|"
                r"la mia professione è|"
                r"faccio il|"
                r"faccio la)\s+"
                r"(.+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="professione",
            value=value,
            memory_type=MemoryType.PROFILE,
            importance=8,
        )

    def _extract_hobby(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:il mio hobby è|"
                r"come hobby pratico|"
                r"nel tempo libero mi piace)\s+"
                r"(.+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="hobby",
            value=value,
            memory_type=MemoryType.PREFERENCE,
            importance=6,
        )

    def _extract_pet(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:il mio animale domestico si chiama|"
                r"ho un cane di nome|"
                r"ho una cagna di nome|"
                r"ho un gatto di nome|"
                r"ho una gatta di nome|"
                r"ho un animale domestico di nome)\s+"
                r"([A-Za-zÀ-ÿ0-9'_-]+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="animale_domestico",
            value=value,
            memory_type=MemoryType.PROFILE,
            importance=6,
        )

    def _extract_goal(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:il mio obiettivo è|"
                r"il mio obiettivo principale è|"
                r"voglio diventare|"
                r"vorrei diventare)\s+"
                r"(.+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="obiettivo",
            value=value,
            memory_type=MemoryType.PROFILE,
            importance=10,
        )

    def _extract_favorite_language(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:il mio linguaggio preferito è|"
                r"preferisco programmare in)\s+"
                r"([A-Za-z0-9+#.-]+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="linguaggio_preferito",
            value=value,
            memory_type=MemoryType.PREFERENCE,
            importance=9,
        )

    def _extract_favorite_color(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:il mio colore preferito è|"
                r"preferisco il colore)\s+"
                r"([A-Za-zÀ-ÿ -]+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="colore_preferito",
            value=value.title(),
            memory_type=MemoryType.PREFERENCE,
            importance=8,
        )

    def _extract_operating_system(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:uso|utilizzo)\s+"
                r"(Windows|Linux|macOS|Mac OS)"
            ),
            text,
        )

        if value is None:
            return None

        normalized_value = value

        if value.lower() == "mac os":
            normalized_value = "macOS"

        return self._create_memory(
            key="sistema_operativo",
            value=normalized_value,
            memory_type=MemoryType.PROFILE,
            importance=7,
        )

    def _extract_project(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:sto lavorando al progetto|"
                r"sto lavorando sul progetto|"
                r"il mio progetto si chiama)\s+"
                r"(.+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="progetto_attuale",
            value=value,
            memory_type=MemoryType.PROJECT,
            importance=8,
        )

    def _extract_favorite_browser(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:il mio browser preferito è|"
                r"come browser preferisco)\s+"
                r"(.+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="browser_preferito",
            value=value,
            memory_type=MemoryType.PREFERENCE,
            importance=7,
        )

    def _extract_favorite_editor(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:il mio editor preferito è|"
                r"uso come editor|"
                r"come editor preferisco)\s+"
                r"(.+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="editor_preferito",
            value=value,
            memory_type=MemoryType.PREFERENCE,
            importance=8,
        )

    def _extract_favorite_theme(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:preferisco il tema|"
                r"il mio tema preferito è)\s+"
                r"(.+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="tema_preferito",
            value=value,
            memory_type=MemoryType.PREFERENCE,
            importance=6,
        )

    def _extract_favorite_music(
        self,
        text: str,
    ) -> Memory | None:

        value = self._match(
            (
                r"\b(?:la mia musica preferita è|"
                r"il mio genere musicale preferito è|"
                r"mi piace la musica)\s+"
                r"(.+)"
            ),
            text,
        )

        if value is None:
            return None

        return self._create_memory(
            key="musica_preferita",
            value=value,
            memory_type=MemoryType.PREFERENCE,
            importance=6,
        )