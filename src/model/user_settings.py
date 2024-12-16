"""
Contains the UserSettings class which provides utility for getting user settings from the
settings file.
"""

import json
from pathlib import Path
from typing import Optional, Any


class UserSettings:
    """Gets user settings from the settings file or returns the default if no setting is found."""

    DEFAULT_SETTINGS: dict[str, any] = {
        "database_path": "",
        "receipts_folder": "~/Documents/ExTrackReceipts",
        "location_scan_radius": 0.2,
        "default_account": "",
    }
    """Default settings for the application."""

    def __init__(self, settings_file_path: Path) -> None:
        self.settings: Optional[dict[str, str]] = None
        """Settings for the application."""

        self.settings_file_path: Path = settings_file_path
        """Path to the settings file."""

    def load_settings(self) -> None:
        """
        Load settings from the settings file.
        """
        # If the settings file path does not exist, dump the default settings to the file
        if not self.settings_file_path.exists():  # type: ignore
            self._set_settings(self.DEFAULT_SETTINGS)

        # Load the settings from the settings file
        with open(self.settings_file_path, "r", encoding="utf-8") as file:  # type: ignore
            self.settings = json.load(file)

    def _set_settings(self, new_settings: Optional[dict[str, str]] = None) -> None:
        """
        Dump the settings to the settings file.

        :param new_settings: New settings to dump, if left blank, the current settings will be
        dumped.
        """
        with open(self.settings_file_path, "w", encoding="utf-8") as file:
            json.dump(new_settings if new_settings is not None else self.settings, file)

    def _get_setting(
        self,
        key: str,
        require_existence: bool = False,
        require_value: bool = False,
        default: Optional[str] = None,
    ) -> Optional[str]:
        """
        Get a setting from the settings file.

        :param key: Key to get from the settings file
        :param require_existence: True if an error should be thrown if key is missing
         false if default should be returned instead
        :param require_value: True if an error should be thrown if the value is empty
        :param default: Default value to return if the key is missing
        :return: Value of the key in the settings file
        """
        if self.settings is None:
            self.load_settings()

        # Try to get the value from the settings file
        value: str
        try:
            value = self.settings[key]  # type: ignore
        except KeyError as error:
            # If the KEY does not exist in the settings file and existence is required,
            # throw an error
            if require_existence or require_value:
                raise RuntimeError(
                    f"{key} must have a value in settings.json."
                ) from error

            # If the KEY does not exist in the settings file and existence is not required,
            # return the default
            return default

        # If VALUE does not exist in the settings file and a value is required, throw an error
        if value == "":
            if require_value:
                raise RuntimeError(f"{key} must have a value in the settings file.")
            return None

        return value

    def database_path(self) -> Optional[Path]:
        """
        Gets the path to the database file from the settings.

        :return: Path to database file
        """
        database_path: Any = self._get_setting("database_path", require_existence=True)
        return None if database_path is None else Path(str(database_path))

    def receipts_folder(self) -> Path:
        """
        Gets the path to the receipts folder from the settings.

        :return: Path to receipts folder
        """
        receipts_folder: Any = self._get_setting(
            "receipts_folder", require_existence=True
        )
        return Path(receipts_folder)

    def location_scan_radius(self) -> float:
        """
        Gets the location scan radius from the settings.

        :return: Radius in miles to scan for a merchant location match.
        """
        location: Any = self._get_setting(
            "location_scan_radius",
            default=UserSettings.DEFAULT_SETTINGS["location_scan_radius"],
        )
        try:
            return float(location)
        except ValueError:
            return UserSettings.DEFAULT_SETTINGS["location_scan_radius"]

    def default_account(self) -> Optional[str]:
        """
        Gets the default account from the settings if it exists.

        :return: Raw account name string from the settings file if it exists.
        """
        return self._get_setting("default_account", default=None)

    def set_database_path(self, new_path: Optional[Path]) -> None:
        """
        Sets the database path.

        :param new_path: New path to the database file
        """
        if self.settings is None:
            raise RuntimeError("Settings file has not been loaded.")

        self.settings["database_path"] = "" if new_path is None else str(new_path)
        self._set_settings()
