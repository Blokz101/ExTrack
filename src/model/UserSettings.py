from typing import Optional, cast
import json
from pathlib import Path


class UserSettings:
    """Gets user settings from the settings file or returns the default if no setting is found."""

    DEFAULT_SETTINGS: dict[str, str] = {"database_path": ""}
    """Default settings for the application."""

    def __init__(self, settings_file_path: Path) -> None:
        self.settings_file_path: Path = settings_file_path
        """Path to the settings file."""

        self.settings: Optional[dict[str, str]] = None
        """Settings for the application."""

        self.load_settings()

    def load_settings(self) -> None:
        """
        Load settings from the settings file.
        """
        if not self.settings_file_path.exists():
            with open(self.settings_file_path, "w", encoding="utf-8") as file:
                json.dump(UserSettings.DEFAULT_SETTINGS, file)

        with open(self.settings_file_path, "r", encoding="utf-8") as file:
            self.settings = json.load(file)

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
        :param require_existence: True if an error should be thrown if key is missing,
         false if default should be returned instead
        :param require_value: True if an error should be thrown if the value is empty
        :param default: Default value to return if the key is missing
        :return: Value of the key in the settings file
        """
        if self.settings is None:
            self.load_settings()
            if self.settings is None:
                raise RuntimeError("Settings file could not be loaded.")

        # Try to get the value from the settings file
        value: str
        try:
            value = self.settings[key]
        except KeyError as error:
            # If the KEY does not exist in the settings file and existence is required,
            # throw an error
            if require_existence or require_value:
                raise RuntimeError(f"{key} must exist in the settings file.") from error

            # If the KEY does not exist in the settings file and existence is not required,
            # return the default
            return default

        # If VALUE does not exist in the settings file and a value is required, throw an error
        if require_value and value == "":
            raise RuntimeError(f"{key} must have a value in the settings file.")

        return value

    def database_path(self) -> Path:
        """
        Gets the path to the database file from the settings.

        :return: Path to database file
        """
        return Path(
            cast(
                str,
                self._get_setting(
                    "database_path", require_existence=True, require_value=True
                ),
            )
        )
