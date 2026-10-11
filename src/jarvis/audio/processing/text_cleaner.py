import re


class SpeechTextCleaner:
    """
    Prepara le risposte testuali dell'AI per la sintesi vocale.

    Rimuove o trasforma gli elementi che il motore TTS
    non dovrebbe pronunciare, come Markdown, URL e simboli.
    """

    _CODE_BLOCK_PATTERN = re.compile(
        r"```.*?```",
        flags=re.DOTALL,
    )

    _MARKDOWN_LINK_PATTERN = re.compile(
        r"\[([^\]]+)\]\([^)]+\)"
    )

    _URL_PATTERN = re.compile(
        r"https?://\S+|www\.\S+",
        flags=re.IGNORECASE,
    )

    _MARKDOWN_SYMBOLS_PATTERN = re.compile(
        r"[*_~#>`]+"
    )

    _MULTIPLE_SPACES_PATTERN = re.compile(
        r"[ \t]+"
    )

    _MULTIPLE_NEWLINES_PATTERN = re.compile(
        r"\n{3,}"
    )

    def clean(self, text: str) -> str:
        """
        Restituisce una versione del testo adatta alla voce.
        """

        if not text:
            return ""

        cleaned_text = text.strip()

        cleaned_text = self._remove_code_blocks(
            cleaned_text
        )

        cleaned_text = self._replace_markdown_links(
            cleaned_text
        )

        cleaned_text = self._remove_urls(
            cleaned_text
        )

        cleaned_text = self._clean_inline_code(
            cleaned_text
        )

        cleaned_text = self._remove_markdown_symbols(
            cleaned_text
        )

        cleaned_text = self._normalize_lists(
            cleaned_text
        )

        cleaned_text = self._normalize_whitespace(
            cleaned_text
        )

        return cleaned_text.strip()

    def _remove_code_blocks(self, text: str) -> str:
        """
        Evita che il TTS legga interi blocchi di codice.
        """

        return self._CODE_BLOCK_PATTERN.sub(
            " Ho omesso il blocco di codice dalla lettura. ",
            text,
        )

    def _replace_markdown_links(self, text: str) -> str:
        """
        Mantiene il testo visibile dei collegamenti Markdown.
        """

        return self._MARKDOWN_LINK_PATTERN.sub(
            r"\1",
            text,
        )

    def _remove_urls(self, text: str) -> str:
        """
        Rimuove gli indirizzi web dalla lettura vocale.
        """

        return self._URL_PATTERN.sub(
            " collegamento web ",
            text,
        )

    @staticmethod
    def _clean_inline_code(text: str) -> str:
        """
        Mantiene il contenuto del codice inline,
        eliminando i caratteri backtick.
        """

        return re.sub(
            r"`([^`]+)`",
            r"\1",
            text,
        )

    def _remove_markdown_symbols(self, text: str) -> str:
        """
        Elimina i principali simboli Markdown.
        """

        return self._MARKDOWN_SYMBOLS_PATTERN.sub(
            "",
            text,
        )

    @staticmethod
    def _normalize_lists(text: str) -> str:
        """
        Trasforma i punti elenco in frasi più leggibili.
        """

        lines = []

        for line in text.splitlines():
            normalized_line = re.sub(
                r"^\s*[-+•]\s+",
                "",
                line,
            )

            normalized_line = re.sub(
                r"^\s*\d+[.)]\s+",
                "",
                normalized_line,
            )

            lines.append(normalized_line)

        return "\n".join(lines)

    def _normalize_whitespace(self, text: str) -> str:
        """
        Elimina spazi e righe vuote eccessive.
        """

        text = self._MULTIPLE_SPACES_PATTERN.sub(
            " ",
            text,
        )

        text = self._MULTIPLE_NEWLINES_PATTERN.sub(
            "\n\n",
            text,
        )

        return text