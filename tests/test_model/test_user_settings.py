"""
Tests the UserSettings class.
"""

# mypy: ignore-errors
import json
import os
from pathlib import Path
from unittest import TestCase

from src import model
from src.model.user_settings import UserSettings
from tests.test_model import test_database_path, test_settings_file_path


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
        model.app_settings = UserSettings(test_settings_file_path)

    def tearDown(self):
        """
        Runs after each test, deletes the settings file if it exists.
        """
        if test_settings_file_path.exists():
            os.remove(test_settings_file_path)
        if test_database_path.exists():
            os.remove(test_database_path)

    def test_create_new_settings(self):
        """
        Test creating a new file with no settings.
        """
        self.assertFalse(test_settings_file_path.exists())

        model.app_settings.load_settings()

        self.assertTrue(test_settings_file_path.exists())
        self.assertIsNotNone(model.app_settings.settings_file_path)
        self.assertEqual(
            model.app_settings.settings,
            {
                "database_path": "",
                "receipts_folder": "~/Documents/ExTrackReceipts",
                "location_scan_radius": "0.2",
            },
        )

    def test_load_settings_without_file(self):
        """
        Tests UserSettings.load_settings() when a settings file does not exist.
        """
        self.assertFalse(test_settings_file_path.exists())
        self.assertIsNone(model.app_settings.settings)

        model.app_settings.load_settings()

        self.assertIsNotNone(model.app_settings.settings)
        self.assertTrue(test_settings_file_path.exists())

    def test_load_settings_with_file(self):
        """
        Tests User.settings.load_settings() when a settings file exists
        """
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": ""}, file)

        self.assertTrue(test_settings_file_path.exists())
        self.assertIsNone(model.app_settings.settings)

        model.app_settings.load_settings()

        self.assertTrue(test_settings_file_path.exists())
        self.assertIsNotNone(model.app_settings.settings)

    def test_database_path(self):
        """
        Tests UserSettings.database_path()
        """
        actual_database_path: Path

        # Test without a settings file
        self.assertFalse(test_settings_file_path.exists())

        actual_database_path = model.app_settings.database_path()

        self.assertTrue(test_settings_file_path.exists())
        self.assertIsNone(actual_database_path)

        # Test without a settings file which lacks a database_path
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            file.write("{}")
        model.app_settings.load_settings()

        self.assertTrue(test_settings_file_path.exists())

        with self.assertRaises(RuntimeError) as msg:
            model.app_settings.database_path()
        self.assertEqual(
            "database_path must have a value in settings.json.", str(msg.exception)
        )

        # Test with a valid settings file and empty database path
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": ""}, file)
        model.app_settings.load_settings()

        actual_database_path = model.app_settings.database_path()

        self.assertIsNone(actual_database_path)

        # Test with valid settings file and database path
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": str(test_database_path.absolute())}, file)
        model.app_settings.load_settings()

        self.assertEqual(
            test_database_path,
            model.app_settings.database_path(),
        )

    def test_set_database_path(self):
        """
        Tests UserSettings.set_database_path()
        """
        # pylint: disable=consider-using-with
        open(test_database_path, "w", encoding="utf-8").close()

        # Test without a settings file
        self.assertFalse(test_settings_file_path.exists())
        with self.assertRaises(RuntimeError) as msg:
            model.app_settings.set_database_path(test_database_path)
        self.assertEqual("Settings file has not been loaded.", str(msg.exception))

        # Test with a settings file
        model.app_settings.load_settings()
        self.assertEqual(None, model.app_settings.database_path())
        model.app_settings.set_database_path(test_database_path)
        model.app_settings.load_settings()
        self.assertEqual(test_database_path, model.app_settings.database_path())

        # Test setting to None again
        model.app_settings.set_database_path(None)
        model.app_settings.load_settings()
        self.assertIsNone(model.app_settings.database_path())
