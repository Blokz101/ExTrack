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

    def setUp(self):
        """
        Runs before each test, resets the user_settings variable.
        """
        if test_settings_file_path.exists():
            os.remove(test_settings_file_path)
        user_settings.settings = None
        user_settings.settings_file_path = None

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
        self.assertIsNone(user_settings.settings_file_path)

        user_settings.load_settings(test_settings_file_path)

        self.assertTrue(test_settings_file_path.exists())
        self.assertIsNotNone(user_settings.settings_file_path)
        self.assertEqual(user_settings.settings, {"database_path": ""})

    def test_load_settings(self):
        """
        Tests UserSettings.load_settings()
        """
        # Test without having loaded a file previously without a file
        self.assertIsNone(user_settings.settings)
        self.assertIsNone(user_settings.settings_file_path)

        with self.assertRaises(RuntimeError) as msg:
            user_settings.load_settings()
        self.assertEqual("Settings file path has not been set.", str(msg.exception))

        # Test having loaded a file previously
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": "test.db"}, file)
        user_settings.load_settings(test_settings_file_path)

        self.assertEqual({"database_path": "test.db"}, user_settings.settings)

    def test_database_path(self):
        """
        Tests UserSettings.database_path()
        """
        # Test without a settings file
        self.assertFalse(test_settings_file_path.exists())
        user_settings.load_settings(test_settings_file_path)
        self.assertIsNone(user_settings.database_path())

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

        self.assertIsNone(user_settings.database_path())

        # Test with a database_path
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": "test.db"}, file)
        user_settings.load_settings(test_settings_file_path)

        self.assertEqual(Path("test.db"), user_settings.database_path())

    def test_set_database_path(self):
        """
        Tests UserSettings.set_database_path()
        """
        # Test without a settings file
        self.assertFalse(test_settings_file_path.exists())
        with self.assertRaises(RuntimeError) as msg:
            user_settings.set_database_path(Path("test.db"))
        self.assertEqual("Settings file has not been loaded.", str(msg.exception))

        # Test with a settings file
        user_settings.load_settings(test_settings_file_path)
        self.assertEqual(None, user_settings.database_path())
        user_settings.set_database_path(Path("test.db"))
        user_settings.load_settings()
        self.assertEqual(Path("test.db"), user_settings.database_path())

        # Test setting to None again
        user_settings.set_database_path(None)
        user_settings.load_settings()
        self.assertIsNone(user_settings.database_path())
