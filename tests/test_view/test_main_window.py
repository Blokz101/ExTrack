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

    EXPECTED_TRANSACTION_TAB_VALUES: list[list[str]] = [
        [
            "1",
            "Checking",
            "Date with Sara",
            "20.54",
            "Penn Station",
            "08/27/2020 21:14:40",
        ],
        ["2", "Savings", "New Macbook", "1245.34", "Apple", "10/09/2020 19:01:21"],
        ["3", "Checking", "DND Dice", "12.98", "Etsy", "05/04/2023 23:44:29"],
        [
            "4",
            "Checking",
            "Things from Amazon",
            "47.45",
            "Amazon",
            "09/28/2020 19:26:10",
        ],
        [
            "5",
            "Savings",
            "Transfer From Savings",
            "-100.0",
            "None",
            "02/15/2021 02:32:18",
        ],
        [
            "6",
            "Checking",
            "Transfer Into Checking",
            "100.0",
            "None",
            "02/15/2021 02:33:05",
        ],
    ]

    EXPECTED_MERCHANT_TAB_VALUES: list[list[str]] = [
        ["1", "Penn Station", "False", "pennstation"],
        ["2", "Outback Steak House", "False", "outbackhouse"],
        ["3", "Amazon", "True", "amazon"],
        ["4", "Apple", "False", "None"],
        ["5", "Port City Java", "False", "None"],
        ["6", "BJS", "False", "bjsrewards"],
        ["7", "Dollar General", "False", "dollar_general"],
        ["8", "Bambu Labs", "True", "bambu"],
        ["9", "Etsy", "True", "etsy"],
    ]

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
        # TODO Add row id list verification for the rest of the tabs
        self.assertEqual([], app.transaction_tab.row_id_list)
        self.assertEqual([], app.merchant_tab.row_id_list)

        self.assertTrue(test_settings_file_path.exists())

        app.window.close()

        self.fail("Test not fully implemented, but has succeeded so far.")

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
        # TODO Add row id list verification for the rest of the tabs
        self.assertEqual([], app.transaction_tab.row_id_list)
        self.assertEqual([], app.merchant_tab.row_id_list)

        app.window.close()

        self.fail("Test not fully implemented, but has succeeded so far.")

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
        # TODO Add row id list verification for the rest of the tabs
        self.assertEqual([], app.transaction_tab.row_id_list)
        self.assertEqual([], app.merchant_tab.row_id_list)

        app.window.close()

        self.fail("Test not fully implemented, but has succeeded so far.")

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
        # TODO Add row id list verification for the rest of the tabs
        self.assertEqual(list(range(1, 7)), app.transaction_tab.row_id_list)
        self.assertEqual(
            TestMainWindow.EXPECTED_TRANSACTION_TAB_VALUES, app.transaction_tab.values
        )
        self.assertEqual(list(range(1, 10)), app.merchant_tab.row_id_list)
        self.assertEqual(
            TestMainWindow.EXPECTED_MERCHANT_TAB_VALUES, app.merchant_tab.values
        )

        database.close()
        os.remove(test_database_path)
        app.window.close()

        self.fail("Test not fully implemented, but has succeeded so far.")
