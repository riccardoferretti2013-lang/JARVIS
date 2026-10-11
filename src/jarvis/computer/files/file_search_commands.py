from pathlib import Path

from .file_search_controller import (
    FileSearchController,
)


class FileSearchCommands:
    """
    Gestisce:
    - ricerca file
    - apertura cartelle
    - copia file/cartelle
    - spostamento file/cartelle
    - eliminazione file/cartelle
    - compressione ZIP
    """

    def __init__(
        self,
        controller: FileSearchController | None = None,
    ) -> None:
        self._controller = (
            controller
            or FileSearchController()
        )

        self._delete_pending: (
            Path | None
        ) = None

    def process(
        self,
        command: str,
    ) -> str | None:

        clean_command = (
            command
            .strip()
        )

        if not clean_command:
            return None

        lower_command = (
            clean_command.lower()
        )

        confirmation_result = (
            self._process_delete_confirmation(
                lower_command
            )
        )

        if confirmation_result is not None:
            return confirmation_result

        compress_result = (
            self._process_compress_command(
                clean_command,
                lower_command,
            )
        )

        if compress_result is not None:
            return compress_result

        delete_result = (
            self._process_delete_command(
                clean_command,
                lower_command,
            )
        )

        if delete_result is not None:
            return delete_result

        move_result = (
            self._process_move_command(
                clean_command,
                lower_command,
            )
        )

        if move_result is not None:
            return move_result

        copy_result = (
            self._process_copy_command(
                clean_command,
                lower_command,
            )
        )

        if copy_result is not None:
            return copy_result

        folder_result = (
            self._process_folder_command(
                clean_command,
                lower_command,
            )
        )

        if folder_result is not None:
            return folder_result

        file_prefixes = (
            "cerca file ",
            "cerca il file ",
            "trova file ",
            "trova il file ",
            "cerca documento ",
            "trova documento ",
        )

        for prefix in file_prefixes:
            if lower_command.startswith(
                prefix
            ):
                query = clean_command[
                    len(prefix):
                ].strip()

                return self._search(
                    query
                )

        return None

    def _process_compress_command(
        self,
        command: str,
        lower_command: str,
    ) -> str | None:

        prefixes = (
            (
                "comprimi il file ",
                "file",
            ),
            (
                "comprimi file ",
                "file",
            ),
            (
                "comprimi la cartella ",
                "folder",
            ),
            (
                "comprimi cartella ",
                "folder",
            ),
            (
                "crea zip del file ",
                "file",
            ),
            (
                "crea zip della cartella ",
                "folder",
            ),
        )

        item_type = None
        item_name = None

        for prefix, detected_type in prefixes:
            if lower_command.startswith(
                prefix
            ):
                item_type = detected_type

                item_name = command[
                    len(prefix):
                ].strip()

                break

        if (
            item_type is None
            or item_name is None
        ):
            return None

        if not item_name:
            return (
                "Non hai indicato cosa comprimere."
            )

        source = self._resolve_source(
            item_type,
            item_name,
        )

        if source is None:
            return (
                "Non ho trovato un elemento "
                "univoco chiamato "
                f'"{item_name}".'
            )

        zip_path = (
            self._controller.compress_item(
                source
            )
        )

        if zip_path is None:
            return (
                "Non sono riuscito a comprimere "
                f"{source.name}."
            )

        return (
            f"Ho compresso {source.name} "
            f"nel file {zip_path.name}."
        )

    def _process_delete_confirmation(
        self,
        command: str,
    ) -> str | None:

        confirm_commands = {
            "conferma",
            "confermo",
            "conferma eliminazione",
            "si elimina",
            "sì elimina",
        }

        cancel_commands = {
            "annulla",
            "annulla eliminazione",
            "non eliminare",
        }

        if self._delete_pending is None:
            return None

        if command in cancel_commands:
            name = (
                self._delete_pending.name
            )

            self._delete_pending = None

            return (
                "Eliminazione annullata. "
                f"{name} non è stato eliminato."
            )

        if command not in confirm_commands:
            return None

        path = self._delete_pending

        self._delete_pending = None

        if not path.exists():
            return (
                "L'elemento non esiste più."
            )

        deleted = (
            self._controller.delete_item(
                path
            )
        )

        if not deleted:
            return (
                "Non sono riuscito a eliminare "
                f"{path.name}."
            )

        return (
            f"Ho eliminato {path.name}."
        )

    def _process_delete_command(
        self,
        command: str,
        lower_command: str,
    ) -> str | None:

        prefixes = (
            (
                "elimina il file ",
                "file",
            ),
            (
                "elimina file ",
                "file",
            ),
            (
                "cancella il file ",
                "file",
            ),
            (
                "cancella file ",
                "file",
            ),
            (
                "elimina la cartella ",
                "folder",
            ),
            (
                "elimina cartella ",
                "folder",
            ),
            (
                "cancella la cartella ",
                "folder",
            ),
            (
                "cancella cartella ",
                "folder",
            ),
        )

        item_type = None
        item_name = None

        for prefix, detected_type in prefixes:
            if lower_command.startswith(
                prefix
            ):
                item_type = detected_type

                item_name = command[
                    len(prefix):
                ].strip()

                break

        if (
            item_type is None
            or item_name is None
        ):
            return None

        if not item_name:
            return (
                "Non hai indicato cosa eliminare."
            )

        source = self._resolve_source(
            item_type,
            item_name,
        )

        if source is None:
            return (
                "Non ho trovato un elemento "
                "univoco chiamato "
                f'"{item_name}".'
            )

        if self._controller.is_protected(
            source
        ):
            return (
                "Non posso eliminare "
                f"{source.name} perché è "
                "una cartella protetta."
            )

        self._delete_pending = source

        item_description = (
            "il file"
            if source.is_file()
            else "la cartella"
        )

        return (
            f"Stai per eliminare definitivamente "
            f"{item_description} {source.name}. "
            "Di' conferma per continuare "
            "oppure annulla."
        )

    def _process_move_command(
        self,
        command: str,
        lower_command: str,
    ) -> str | None:

        prefixes = (
            (
                "sposta il file ",
                "file",
            ),
            (
                "sposta file ",
                "file",
            ),
            (
                "sposta la cartella ",
                "folder",
            ),
            (
                "sposta cartella ",
                "folder",
            ),
        )

        item_type = None
        remainder = None

        for prefix, detected_type in prefixes:
            if lower_command.startswith(
                prefix
            ):
                item_type = detected_type

                remainder = command[
                    len(prefix):
                ].strip()

                break

        if (
            item_type is None
            or remainder is None
        ):
            return None

        lower_remainder = (
            remainder.lower()
        )

        separator = " in "

        if separator not in lower_remainder:
            return (
                "Indica anche la cartella "
                "di destinazione."
            )

        separator_index = (
            lower_remainder.rfind(
                separator
            )
        )

        item_name = remainder[
            :separator_index
        ].strip()

        destination_name = remainder[
            separator_index
            + len(separator):
        ].strip()

        if not item_name:
            return (
                "Non hai indicato cosa spostare."
            )

        if not destination_name:
            return (
                "Non hai indicato dove spostare "
                "l'elemento."
            )

        source = self._resolve_source(
            item_type,
            item_name,
        )

        if source is None:
            return (
                "Non ho trovato un elemento "
                "univoco chiamato "
                f'"{item_name}".'
            )

        destination = (
            self._resolve_destination(
                destination_name
            )
        )

        if destination is None:
            return (
                "Non ho trovato una cartella "
                "di destinazione univoca chiamata "
                f'"{destination_name}".'
            )

        moved_path = (
            self._controller.move_item(
                source,
                destination,
            )
        )

        if moved_path is None:
            return (
                "Non sono riuscito a spostare "
                f"{source.name}."
            )

        return (
            f"Ho spostato {source.name} "
            f"nella cartella {destination.name}."
        )

    def _process_copy_command(
        self,
        command: str,
        lower_command: str,
    ) -> str | None:

        prefixes = (
            (
                "copia il file ",
                "file",
            ),
            (
                "copia file ",
                "file",
            ),
            (
                "copia la cartella ",
                "folder",
            ),
            (
                "copia cartella ",
                "folder",
            ),
        )

        item_type = None
        remainder = None

        for prefix, detected_type in prefixes:
            if lower_command.startswith(
                prefix
            ):
                item_type = detected_type

                remainder = command[
                    len(prefix):
                ].strip()

                break

        if (
            item_type is None
            or remainder is None
        ):
            return None

        lower_remainder = (
            remainder.lower()
        )

        separator = " in "

        if separator not in lower_remainder:
            return (
                "Indica anche la cartella "
                "di destinazione."
            )

        separator_index = (
            lower_remainder.rfind(
                separator
            )
        )

        item_name = remainder[
            :separator_index
        ].strip()

        destination_name = remainder[
            separator_index
            + len(separator):
        ].strip()

        if not item_name:
            return (
                "Non hai indicato cosa copiare."
            )

        if not destination_name:
            return (
                "Non hai indicato dove copiare "
                "l'elemento."
            )

        source = self._resolve_source(
            item_type,
            item_name,
        )

        if source is None:
            return (
                "Non ho trovato un elemento "
                "univoco chiamato "
                f'"{item_name}".'
            )

        destination = (
            self._resolve_destination(
                destination_name
            )
        )

        if destination is None:
            return (
                "Non ho trovato una cartella "
                "di destinazione univoca chiamata "
                f'"{destination_name}".'
            )

        copied_path = (
            self._controller.copy_item(
                source,
                destination,
            )
        )

        if copied_path is None:
            return (
                "Non sono riuscito a copiare "
                f"{source.name}."
            )

        return (
            f"Ho copiato {source.name} "
            f"nella cartella {destination.name}."
        )

    def _resolve_source(
        self,
        item_type: str,
        item_name: str,
    ) -> Path | None:

        if item_type == "file":
            results = (
                self._find_file_for_action(
                    item_name
                )
            )

        else:
            results = (
                self._controller.find_folder(
                    item_name,
                    max_results=10,
                )
            )

        if not results:
            return None

        return self._select_unique_match(
            results,
            item_name,
        )

    def _resolve_destination(
        self,
        destination_name: str,
    ) -> Path | None:

        results = (
            self._controller.find_folder(
                destination_name,
                max_results=10,
            )
        )

        if not results:
            return None

        return self._select_unique_match(
            results,
            destination_name,
        )

    def _find_file_for_action(
        self,
        file_name: str,
    ) -> list[Path]:

        exact_results = (
            self._controller.find_exact(
                file_name
            )
        )

        if exact_results:
            return exact_results

        return self._controller.search(
            query=file_name,
            max_results=10,
        )

    @staticmethod
    def _select_unique_match(
        results: list[Path],
        requested_name: str,
    ) -> Path | None:

        if len(results) == 1:
            return results[0]

        exact = [
            path
            for path in results
            if (
                path.name.lower()
                == requested_name.lower()
            )
        ]

        if len(exact) == 1:
            return exact[0]

        return None

    def _process_folder_command(
        self,
        command: str,
        lower_command: str,
    ) -> str | None:

        direct_folders = {
            "apri desktop": "desktop",
            "apri scrivania": "scrivania",
            "apri documenti": "documenti",
            "apri downloads": "downloads",
            "apri download": "download",
            "apri la cartella download": "download",
            "apri la cartella downloads": "downloads",
            "apri la cartella documenti": "documenti",
            "apri la cartella desktop": "desktop",
        }

        if lower_command in direct_folders:
            return self._open_folder(
                direct_folders[
                    lower_command
                ]
            )

        prefixes = (
            "apri cartella ",
            "apri la cartella ",
            "apri directory ",
            "apri la directory ",
        )

        for prefix in prefixes:
            if lower_command.startswith(
                prefix
            ):
                folder_name = command[
                    len(prefix):
                ].strip()

                return self._open_folder(
                    folder_name
                )

        return None

    def _open_folder(
        self,
        folder_name: str,
    ) -> str:

        if not folder_name:
            return (
                "Non hai indicato quale "
                "cartella aprire."
            )

        results = (
            self._controller.find_folder(
                folder_name,
                max_results=10,
            )
        )

        if not results:
            return (
                "Non ho trovato la cartella "
                f'"{folder_name}".'
            )

        folder = (
            self._select_unique_match(
                results,
                folder_name,
            )
        )

        if folder is None:
            return self._format_folder_results(
                results
            )

        opened = (
            self._controller.open_folder(
                folder
            )
        )

        if opened:
            return (
                "Ho aperto la cartella "
                f"{folder.name}."
            )

        return (
            "Non sono riuscito ad aprire "
            f"la cartella {folder.name}."
        )

    def _search(
        self,
        query: str,
    ) -> str:

        if not query:
            return (
                "Non hai indicato quale "
                "file cercare."
            )

        results = self._controller.search(
            query=query,
            max_results=10,
        )

        if not results:
            return (
                "Non ho trovato file "
                f'corrispondenti a "{query}".'
            )

        if len(results) == 1:
            return (
                "Ho trovato il file: "
                f"{results[0]}"
            )

        return self._format_results(
            results
        )

    @staticmethod
    def _format_results(
        results: list[Path],
    ) -> str:

        formatted_results = "\n".join(
            f"{index}. {path}"
            for index, path in enumerate(
                results,
                start=1,
            )
        )

        return (
            f"Ho trovato {len(results)} file:\n"
            f"{formatted_results}"
        )

    @staticmethod
    def _format_folder_results(
        results: list[Path],
    ) -> str:

        formatted_results = "\n".join(
            f"{index}. {path}"
            for index, path in enumerate(
                results,
                start=1,
            )
        )

        return (
            "Ho trovato più cartelle "
            "con questo nome:\n"
            f"{formatted_results}"
        )