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
        [
            "2",
            "Savings",
            "New Macbook",
            "1245.34",
            "Apple",
            "10/09/2020 19:01:21",
        ],
        [
            "3",
            "Checking",
            "DND Dice",
            "12.98",
            "Etsy",
            "05/04/2023 23:44:29",
        ],
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

    EXPECTED_STATEMENTS_TAB_VALUES: list[list[str]] = [
        ["1", "02/14/2019", "Checking", "3235.45", "True"],
        ["2", "07/08/2020", "Checking", "664.45", "True"],
        ["3", "07/20/2023", "Checking", "3825.01", "False"],
        ["4", "12/21/2018", "Savings", "517.01", "True"],
        ["5", "08/25/2019", "Savings", "320.93", "True"],
        ["6", "04/22/2021", "Savings", "500.33", "False"],
    ]

    EXPECTED_ACCOUNTS_TAB_VALUES: list[list[str]] = [
        ["1", "Checking", "2", "3", "7"],
        ["2", "Savings", "3", "1", "5"],
    ]

    EXPECTED_MERCHANT_TAB_VALUES: list[list[str]] = [
        ["1", "Penn Station", "False", "Dating, Eating Out", "pennstation"],
        ["2", "Outback Steak House", "False", "Eating Out", "outbackhouse"],
        ["3", "Amazon", "True", "No Tags", "amazon"],
        ["4", "Apple", "False", "Personal", "None"],
        ["5", "Port City Java", "False", "Coffee", "None"],
        ["6", "BJS", "False", "Groceries", "bjsrewards"],
        ["7", "Dollar General", "False", "No Tags", "dollar_general"],
        ["8", "Bambu Labs", "True", "Personal", "bambu"],
        ["9", "Etsy", "True", "Personal", "etsy"],
    ]

    EXPECTED_LOCATION_TAB_VALUES: list[list[str]] = [
        [
            "1",
            "Falls of Neuse",
            "Penn Station",
            "35.86837825457926",
            "-78.62150981593383",
        ],
        [
            "2",
            "Capital",
            "Outback Steak House",
            "35.85665622223983",
            "-78.58032796673776",
        ],
        [
            "3",
            "Crabtree Mall",
            "Apple",
            "35.8408590921226",
            "-78.68011850195218",
        ],
        [
            "4",
            "EB2",
            "Port City Java",
            "35.77184197261896",
            "-78.67356047898443",
        ],
        [
            "5",
            "Park Shops",
            "Port City Java",
            "35.78546665319359",
            "-78.66708463594044",
        ],
        [
            "6",
            "Talley",
            "Port City Java",
            "35.78392567533286",
            "-78.67092696947988",
        ],
        [
            "7",
            "Walnut",
            "BJS",
            "35.753166119681715",
            "-78.74569648479638",
        ],
        [
            "8",
            "Falls River",
            "Dollar General",
            "35.906477682429525",
            "-78.59029227485301",
        ],
    ]

    EXPECTED_TAGS_TAB_VALUES: list[list[str]] = [
        ["1", "Groceries", "False", "groc"],
        ["2", "Gas", "False", "gas"],
        ["3", "Anarack", "True", "None"],
        ["4", "University", "False", "uni"],
        ["5", "Dating", "False", "date"],
        ["6", "Third Party Transaction", "False", "paid for by parents"],
        ["7", "Eating Out", "False", "eatout"],
        ["8", "Winter Park Trip", "True", "None"],
        ["9", "The Maze Trip", "True", "None"],
        ["10", "Personal", "False", "personal"],
        ["11", "Coffee", "False", "coffee"],
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

        self.assertEqual([], app.transaction_tab.row_id_list)
        self.assertEqual([], app.statement_tab.row_id_list)
        self.assertEqual([], app.account_tab.row_id_list)
        self.assertEqual([], app.merchant_tab.row_id_list)
        self.assertEqual([], app.location_tab.row_id_list)
        self.assertEqual([], app.tag_tab.row_id_list)

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

        self.assertEqual([], app.transaction_tab.row_id_list)
        self.assertEqual([], app.statement_tab.row_id_list)
        self.assertEqual([], app.account_tab.row_id_list)
        self.assertEqual([], app.merchant_tab.row_id_list)
        self.assertEqual([], app.location_tab.row_id_list)
        self.assertEqual([], app.tag_tab.row_id_list)

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
        self.assertEqual([], app.transaction_tab.row_id_list)
        self.assertEqual([], app.statement_tab.row_id_list)
        self.assertEqual([], app.account_tab.row_id_list)
        self.assertEqual([], app.merchant_tab.row_id_list)
        self.assertEqual([], app.location_tab.row_id_list)
        self.assertEqual([], app.tag_tab.row_id_list)

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

        # Check that each tab has the correct values
        self.assertEqual(list(range(1, 7)), app.transaction_tab.row_id_list)
        self.assertEqual(
            TestMainWindow.EXPECTED_TRANSACTION_TAB_VALUES, app.transaction_tab.values
        )

        self.assertEqual(list(range(1, 7)), app.statement_tab.row_id_list)
        self.assertEqual(
            TestMainWindow.EXPECTED_STATEMENTS_TAB_VALUES, app.statement_tab.values
        )

        self.assertEqual(list(range(1, 3)), app.account_tab.row_id_list)
        self.assertEqual(
            TestMainWindow.EXPECTED_ACCOUNTS_TAB_VALUES, app.account_tab.values
        )

        self.assertEqual(list(range(1, 10)), app.merchant_tab.row_id_list)
        self.assertEqual(
            TestMainWindow.EXPECTED_MERCHANT_TAB_VALUES, app.merchant_tab.values
        )

        self.assertEqual(list(range(1, 9)), app.location_tab.row_id_list)
        self.assertEqual(
            TestMainWindow.EXPECTED_LOCATION_TAB_VALUES, app.location_tab.values
        )

        self.assertEqual(list(range(1, 12)), app.tag_tab.row_id_list)
        self.assertEqual(TestMainWindow.EXPECTED_TAGS_TAB_VALUES, app.tag_tab.values)

        database.close()
        os.remove(test_database_path)
        app.window.close()
