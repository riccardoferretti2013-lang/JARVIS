import json
from pathlib import Path
from typing import Any


class SettingsManager:
    """
    Gestisce le impostazioni persistenti di J.A.R.V.I.S.
    """

    def __init__(
        self,
        config_file: str | Path | None = None,
    ) -> None:
        if config_file is None:
            project_root = (
                Path(__file__)
                .resolve()
                .parents[3]
            )

            config_file = (
                project_root
                / "config"
                / "config.json"
            )

        self.config_file = Path(
            config_file
        )

        self.settings: dict[str, Any] = {}

    def load(
        self,
    ) -> None:
        if not self.config_file.exists():
            raise FileNotFoundError(
                "File di configurazione non trovato: "
                f"{self.config_file.resolve()}"
            )

        try:
            with self.config_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                loaded_settings = json.load(
                    file
                )

        except json.JSONDecodeError as error:
            raise ValueError(
                "Il file di configurazione contiene "
                "JSON non valido: "
                f"{self.config_file.resolve()}"
            ) from error

        if not isinstance(
            loaded_settings,
            dict,
        ):
            raise ValueError(
                "Il contenuto di config.json "
                "deve essere un oggetto JSON."
            )

        self.settings = loaded_settings

    def save(
        self,
    ) -> None:
        """
        Salva tutte le impostazioni su config.json.
        """

        self.config_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.config_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.settings,
                file,
                indent=4,
                ensure_ascii=False,
            )

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.settings.get(
            key,
            default,
        )

    def set(
        self,
        key: str,
        value: Any,
        save: bool = True,
    ) -> None:
        """
        Imposta un valore.

        Se save=True, salva subito il file.
        """

        clean_key = key.strip()

        if not clean_key:
            raise ValueError(
                "La chiave non può essere vuota."
            )

        self.settings[
            clean_key
        ] = value

        if save:
            self.save()

    def remove(
        self,
        key: str,
        save: bool = True,
    ) -> bool:
        """
        Rimuove un'impostazione.
        """

        if key not in self.settings:
            return False

        del self.settings[key]

        if save:
            self.save()

        return True

    def contains(
        self,
        key: str,
    ) -> bool:
        return key in self.settings

    def get_all(
        self,
    ) -> dict[str, Any]:
        return self.settings.copy()