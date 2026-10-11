import os
import shutil
import zipfile
from pathlib import Path


class FileSearchController:
    """
    Gestisce:
    - ricerca file
    - ricerca cartelle
    - apertura cartelle
    - copia
    - spostamento
    - eliminazione
    - compressione ZIP
    """

    def __init__(
        self,
        search_roots: list[str | Path] | None = None,
    ) -> None:
        if search_roots is None:
            home = Path.home()

            search_roots = [
                home / "Desktop",
                home / "Documents",
                home / "Downloads",
                home,
            ]

        self._search_roots = [
            Path(path)
            for path in search_roots
        ]

        self._project_root = (
            Path(__file__)
            .resolve()
            .parents[4]
        )

    @property
    def search_roots(
        self,
    ) -> list[Path]:
        return list(
            self._search_roots
        )

    def search(
        self,
        query: str,
        max_results: int = 20,
    ) -> list[Path]:
        clean_query = (
            query
            .strip()
            .lower()
        )

        if not clean_query:
            return []

        results: list[Path] = []
        seen: set[Path] = set()

        for root in self._search_roots:
            if not root.exists():
                continue

            try:
                for path in root.rglob("*"):
                    if len(results) >= max_results:
                        return results

                    if not path.is_file():
                        continue

                    if clean_query not in path.name.lower():
                        continue

                    resolved = path.resolve()

                    if resolved in seen:
                        continue

                    seen.add(
                        resolved
                    )

                    results.append(
                        path
                    )

            except (
                PermissionError,
                OSError,
            ):
                continue

        return results

    def find_exact(
        self,
        filename: str,
    ) -> list[Path]:
        clean_filename = (
            filename
            .strip()
            .lower()
        )

        if not clean_filename:
            return []

        results: list[Path] = []
        seen: set[Path] = set()

        for root in self._search_roots:
            if not root.exists():
                continue

            try:
                for path in root.rglob("*"):
                    if not path.is_file():
                        continue

                    if (
                        path.name.lower()
                        != clean_filename
                    ):
                        continue

                    resolved = path.resolve()

                    if resolved in seen:
                        continue

                    seen.add(
                        resolved
                    )

                    results.append(
                        path
                    )

            except (
                PermissionError,
                OSError,
            ):
                continue

        return results

    def find_folder(
        self,
        folder_name: str,
        max_results: int = 10,
    ) -> list[Path]:
        clean_name = (
            folder_name
            .strip()
            .lower()
        )

        if not clean_name:
            return []

        special_folder = (
            self._get_special_folder(
                clean_name
            )
        )

        if special_folder is not None:
            return [
                special_folder
            ]

        results: list[Path] = []
        seen: set[Path] = set()

        for root in self._search_roots:
            if not root.exists():
                continue

            try:
                if (
                    root.is_dir()
                    and clean_name
                    in root.name.lower()
                ):
                    resolved = (
                        root.resolve()
                    )

                    if resolved not in seen:
                        seen.add(
                            resolved
                        )

                        results.append(
                            root
                        )

                for path in root.rglob("*"):
                    if (
                        len(results)
                        >= max_results
                    ):
                        return results

                    if not path.is_dir():
                        continue

                    if (
                        clean_name
                        not in path.name.lower()
                    ):
                        continue

                    resolved = (
                        path.resolve()
                    )

                    if resolved in seen:
                        continue

                    seen.add(
                        resolved
                    )

                    results.append(
                        path
                    )

            except (
                PermissionError,
                OSError,
            ):
                continue

        return results

    def open_folder(
        self,
        folder: str | Path,
    ) -> bool:
        path = Path(
            folder
        )

        if (
            not path.exists()
            or not path.is_dir()
        ):
            return False

        try:
            os.startfile(
                str(path)
            )

            return True

        except OSError:
            return False

    def copy_item(
        self,
        source: str | Path,
        destination_folder: str | Path,
    ) -> Path | None:
        source_path = Path(
            source
        )

        destination_path = Path(
            destination_folder
        )

        if not source_path.exists():
            return None

        if (
            not destination_path.exists()
            or not destination_path.is_dir()
        ):
            return None

        target = (
            destination_path
            / source_path.name
        )

        target = (
            self._get_available_copy_name(
                target
            )
        )

        try:
            if source_path.is_file():
                shutil.copy2(
                    source_path,
                    target,
                )

            elif source_path.is_dir():
                shutil.copytree(
                    source_path,
                    target,
                )

            else:
                return None

            return target

        except (
            PermissionError,
            OSError,
            shutil.Error,
        ):
            return None

    def move_item(
        self,
        source: str | Path,
        destination_folder: str | Path,
    ) -> Path | None:
        source_path = Path(
            source
        )

        destination_path = Path(
            destination_folder
        )

        if not source_path.exists():
            return None

        if (
            not destination_path.exists()
            or not destination_path.is_dir()
        ):
            return None

        target = (
            destination_path
            / source_path.name
        )

        target = (
            self._get_available_copy_name(
                target
            )
        )

        try:
            result = shutil.move(
                str(source_path),
                str(target),
            )

            return Path(
                result
            )

        except (
            PermissionError,
            OSError,
            shutil.Error,
        ):
            return None

    def delete_item(
        self,
        item: str | Path,
    ) -> bool:
        path = Path(
            item
        )

        if not path.exists():
            return False

        if self.is_protected(
            path
        ):
            return False

        try:
            if path.is_file():
                path.unlink()

            elif path.is_dir():
                shutil.rmtree(
                    path
                )

            else:
                return False

            return True

        except (
            PermissionError,
            OSError,
            shutil.Error,
        ):
            return False

    def compress_item(
        self,
        item: str | Path,
    ) -> Path | None:
        """
        Comprime un file o una cartella
        in formato ZIP.

        Lo ZIP viene creato nella stessa
        cartella dell'elemento originale.
        """

        source = Path(
            item
        )

        if not source.exists():
            return None

        if source.is_file():
            zip_name = (
                source.parent
                / f"{source.stem}.zip"
            )

        elif source.is_dir():
            zip_name = (
                source.parent
                / f"{source.name}.zip"
            )

        else:
            return None

        zip_name = (
            self._get_available_zip_name(
                zip_name
            )
        )

        try:
            with zipfile.ZipFile(
                zip_name,
                mode="w",
                compression=zipfile.ZIP_DEFLATED,
            ) as archive:

                if source.is_file():
                    archive.write(
                        source,
                        arcname=source.name,
                    )

                else:
                    for path in source.rglob("*"):
                        if not path.is_file():
                            continue

                        relative_path = (
                            path.relative_to(
                                source.parent
                            )
                        )

                        archive.write(
                            path,
                            arcname=relative_path,
                        )

            return zip_name

        except (
            PermissionError,
            OSError,
            zipfile.BadZipFile,
        ):
            try:
                if zip_name.exists():
                    zip_name.unlink()

            except OSError:
                pass

            return None

    def is_protected(
        self,
        item: str | Path,
    ) -> bool:
        try:
            path = Path(
                item
            ).resolve()

        except OSError:
            return True

        protected_paths = {
            Path.home().resolve(),
            self._project_root.resolve(),
        }

        for root in self._search_roots:
            try:
                protected_paths.add(
                    root.resolve()
                )

            except OSError:
                continue

        return path in protected_paths

    @staticmethod
    def _get_available_copy_name(
        target: Path,
    ) -> Path:
        if not target.exists():
            return target

        parent = target.parent

        if target.is_file():
            stem = target.stem
            suffix = target.suffix

        else:
            stem = target.name
            suffix = ""

        candidate = (
            parent
            / f"{stem} - copia{suffix}"
        )

        counter = 2

        while candidate.exists():
            candidate = (
                parent
                / (
                    f"{stem} - copia "
                    f"{counter}{suffix}"
                )
            )

            counter += 1

        return candidate

    @staticmethod
    def _get_available_zip_name(
        target: Path,
    ) -> Path:
        """
        Evita di sovrascrivere ZIP esistenti.
        """

        if not target.exists():
            return target

        parent = target.parent
        stem = target.stem

        candidate = (
            parent
            / f"{stem} - copia.zip"
        )

        counter = 2

        while candidate.exists():
            candidate = (
                parent
                / (
                    f"{stem} - copia "
                    f"{counter}.zip"
                )
            )

            counter += 1

        return candidate

    @staticmethod
    def _get_special_folder(
        folder_name: str,
    ) -> Path | None:
        home = Path.home()

        aliases = {
            "desktop": (
                home / "Desktop"
            ),
            "scrivania": (
                home / "Desktop"
            ),
            "documenti": (
                home / "Documents"
            ),
            "documents": (
                home / "Documents"
            ),
            "download": (
                home / "Downloads"
            ),
            "downloads": (
                home / "Downloads"
            ),
            "home": home,
            "utente": home,
            "profilo utente": home,
        }

        path = aliases.get(
            folder_name
        )

        if (
            path is not None
            and path.exists()
        ):
            return path

        return None