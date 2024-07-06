"""
Tests the MainWindow class.
"""

import json

# mypy: ignore-errors
import os
import shutil
from queue import Queue
from unittest import TestCase

from src import view, model
from src.model import database
from src.model.user_settings import UserSettings
from src.view.main_window import MainWindow
from tests.test_model import (
    test_database_path,
    test_settings_file_path,
    sample_database_1_path,
)


class TestMainWindow(TestCase):
    """Tests the MainWindow class."""

    def setUp(self):
        """
        Runs before each test, deletes the test database if it exists.
        """
        if test_database_path.exists():
            os.remove(test_database_path)
        if test_settings_file_path.exists():
            os.remove(test_settings_file_path)

        view.testing_mode = True
        model.app_settings = UserSettings(test_settings_file_path)
        view.notification_message_queue = Queue()

    def tearDown(self):
        """
        Runs after each test, deletes the test database if it exists.
        """
        if test_database_path.exists():
            os.remove(test_database_path)
        if test_settings_file_path.exists():
            os.remove(test_settings_file_path)

    def test_window_construction_no_settings_no_database(self):
        """
        Tests the construction of the main window with no settings file or database file.
        """
        app: MainWindow = MainWindow()
        _, _ = app.window.read(timeout=0)

        self.assertTrue(view.notification_message_queue.empty())
        self.assertEqual([], app.row_id_list)
        self.assertTrue(test_settings_file_path.exists())

        app.window.close()

    def test_window_construction_with_invalid_settings_no_database_1(self):
        """
        Tests the construction of the main window with a settings file that has no database path.
        """
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({}, file)

        app: MainWindow = MainWindow()
        _, _ = app.window.read(timeout=0)

        self.assertEqual(1, view.notification_message_queue.qsize())
        self.assertEqual(
            "database_path must have a value in settings.json.",
            view.notification_message_queue.get(),
        )
        self.assertEqual([], app.row_id_list)

        app.window.close()

    def test_window_construction_with_invalid_settings_no_database_2(self):
        """
        Tests the construction of the main window with a settings file that has database_path
        that does not exist in the file system.
        """
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": str(test_database_path.absolute())}, file)

        app: MainWindow = MainWindow()
        _, _ = app.window.read(timeout=0)

        self.assertEqual(1, view.notification_message_queue.qsize())
        self.assertEqual(
            f"Database file at path '{str(test_database_path.absolute())}' does not exist.",
            view.notification_message_queue.get(),
        )
        self.assertEqual([], app.row_id_list)

        app.window.close()

    def test_window_construction_with_settings_with_database(self):
        """
        Tests the construction of the main window with a settings file that has a valid database
        path.
        """
        shutil.copyfile(sample_database_1_path, test_database_path)

        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"database_path": str(test_database_path.absolute())}, file)

        app: MainWindow = MainWindow()
        _, _ = app.window.read(timeout=0)

        self.assertTrue(view.notification_message_queue.empty())
        self.assertEqual([1, 2, 3, 4, 5, 6], app.row_id_list)

        database.close()
        os.remove(test_database_path)
        app.window.close()
