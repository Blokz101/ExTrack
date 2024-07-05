"""
Tests the UserSettings class.
"""

# mypy: ignore-errors
import json
import os
from pathlib import Path
from unittest import TestCase

from src.model import user_settings
from tests.test_model import test_settings_file_path


class TestUserSettings(TestCase):
    """
    Tests the UserSettings class.
    """

    def tearDown(self):
        """
        Runs after each test, deletes the settings file if it exists.
        """
        if test_settings_file_path.exists():
            os.remove(test_settings_file_path)

    def test_create_new_settings(self):
        """
        Test creating a new file with no settings.
        """
        self.assertFalse(test_settings_file_path.exists())

        user_settings.load_settings(test_settings_file_path)

        self.assertTrue(test_settings_file_path.exists())
        self.assertEqual(user_settings.settings, {"database_path": ""})

    def test_load_settings(self):
        """
        Tests UserSettings.load_settings()
        """
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": "test.db"}, file)
        user_settings.load_settings(test_settings_file_path)

        self.assertEqual({"database_path": "test.db"}, user_settings.settings)

    def test_database_path(self):
        """
        Tests UserSettings.database_path()
        """
        # Test without a database_path
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            file.write("{}")
        user_settings.load_settings(test_settings_file_path)

        with self.assertRaises(RuntimeError) as msg:
            user_settings.database_path()
        self.assertEqual(
            "database_path must exist in the settings file.", str(msg.exception)
        )

        # Test with an empty database_path
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": ""}, file)
        user_settings.load_settings(test_settings_file_path)

        with self.assertRaises(RuntimeError) as msg:
            user_settings.database_path()
        self.assertEqual(
            "database_path must have a value in the settings file.", str(msg.exception)
        )

        # Test with a database_path
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": "test.db"}, file)
        user_settings.load_settings(test_settings_file_path)

        self.assertEqual(Path("test.db"), user_settings.database_path())
