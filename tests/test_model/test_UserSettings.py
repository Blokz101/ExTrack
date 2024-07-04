import json
import os
from pathlib import Path
from unittest import TestCase
from src.model.UserSettings import UserSettings
from src.model import settings_file_path, user_settings


class TestUserSettings(TestCase):

    def tearDown(self):
        """
        Runs after each test, deletes the settings file if it exists.
        """
        if settings_file_path.exists():
            os.remove(settings_file_path)

    def test_create_new_settings(self):
        """
        Test creating a new file with no settings.
        """
        if settings_file_path.exists():
            os.remove(settings_file_path)

        user_settings.load_settings()

        self.assertTrue(settings_file_path.exists())
        self.assertEqual(user_settings.settings, {"database_path": ""})

    def test_load_settings(self):
        """
        Tests UserSettings.load_settings()
        """
        with open(settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": "test.db"}, file)

        user_settings.load_settings()
        self.assertEqual({"database_path": "test.db"}, user_settings.settings)

    def test_database_path(self):
        """
        Tests UserSettings.database_path()
        """
        # Test without a database_path
        with open(settings_file_path, "w", encoding="utf-8") as file:
            file.write("{}")
        user_settings.load_settings()
        with self.assertRaises(RuntimeError) as msg:
            user_settings.database_path()
        self.assertEqual(
            "database_path must exist in the settings file.", str(msg.exception)
        )

        # Test with an empty database_path
        with open(settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": ""}, file)
        user_settings.load_settings()
        with self.assertRaises(RuntimeError) as msg:
            user_settings.database_path()
        self.assertEqual(
            "database_path must have a value in the settings file.", str(msg.exception)
        )

        # Test with a database_path
        with open(settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": "test.db"}, file)
        user_settings.load_settings()
        self.assertEqual(Path("test.db"), user_settings.database_path())
