"""
Contains the Sample1TestCase class which is a base class for all unit tests relating to
sample_database_1.db.
"""

# mypy: ignore-errors
import os
import shutil
from datetime import datetime
from unittest import TestCase

from src.model import database
from src.model import date_format
from src.model.account import Account
from src.model.amount import Amount
from src.model.location import Location
from src.model.merchant import Merchant
from src.model.sql_object import SqlObject
from src.model.statement import Statement
from src.model.tag import Tag
from src.model.transaction import Transaction
from tests.test_model import sample_database_1_path, test_database_path

EXPECTED_TRANSACTIONS: list[Transaction] = [
    Transaction(
        1,
        "Date with Sara",
        1,
        False,
        datetime.strptime("2020-08-27 21:14:40", date_format),
        None,
        "IMAGE4.jpeg",
        35.868317424041166,
        -78.62154243252625,
        1,
        None,
    ),
    Transaction(
        2,
        "New Macbook",
        4,
        True,
        datetime.strptime("2020-10-09 19:01:21", date_format),
        5,
        "IMAGE8932.png",
        35.840809717971595,
        -78.68013948171635,
        2,
        None,
    ),
    Transaction(
        3,
        "DND Dice",
        9,
        True,
        datetime.strptime("2023-05-04 23:44:29", date_format),
        1,
        "IMAGE22.png",
        None,
        None,
        1,
        None,
    ),
    Transaction(
        4,
        "Things from Amazon",
        3,
        True,
        datetime.strptime("2020-09-28 19:26:10", date_format),
        1,
        None,
        None,
        None,
        1,
        None,
    ),
    Transaction(
        5,
        "Transfer From Savings",
        None,
        False,
        datetime.strptime("2021-02-15 02:32:18", date_format),
        None,
        None,
        None,
        None,
        2,
        6,
    ),
    Transaction(
        6,
        "Transfer Into Checking",
        None,
        False,
        datetime.strptime("2021-02-15 02:33:05", date_format),
        None,
        None,
        None,
        None,
        1,
        5,
    ),
]

EXPECTED_STATEMENTS: list[Statement] = [
    Statement(
        1,
        datetime.strptime("2019-02-14 00:00:00", date_format),
        "BOA.csv",
        1,
        3235.45,
        True,
    ),
    Statement(
        2,
        datetime.strptime("2020-07-08 00:00:00", date_format),
        "BOA1.csv",
        1,
        66.45,
        True,
    ),
    Statement(
        3,
        datetime.strptime("2023-07-20 00:00:00", date_format),
        "NEWBOA.csv",
        1,
        3825.01,
        False,
    ),
    Statement(4, "2018-12-21 00:00:00", "DISCOVER.csv", 2, 517.01, True),
    Statement(5, "2019-08-25 00:00:00", None, 2, 320.93, True),
    Statement(6, "2021-04-22 00:00:00", "NEWDISCOVER.csv", 2, 500.33, False),
]

EXPECTED_ACCOUNTS: list[Account] = [
    Account(1, "Checking", 2, 3, 7),
    Account(2, "Savings", 3, 1, 5),
]

EXPECTED_MERCHANTS: list[Merchant] = [
    Merchant(1, "Penn Station", False, "pennstation"),
    Merchant(2, "Outback Steak House", False, "outbackhouse"),
    Merchant(3, "Amazon", True, "amazon"),
    Merchant(4, "Apple", False, None),
    Merchant(5, "Port City Java", False, None),
    Merchant(6, "BJS", False, "bjsrewards"),
    Merchant(7, "Dollar General", False, "dollar_general"),
    Merchant(8, "Bambu Labs", True, "bambu"),
    Merchant(9, "Etsy", True, "etsy"),
]

EXPECTED_LOCATIONS: list[Location] = [
    Location(1, "Falls of Neuse", 1, 35.86837825457926, -78.62150981593383),
    Location(2, "Capital", 2, 35.85665622223983, -78.58032796673776),
    Location(3, "Crabtree Mall", 4, 35.8408590921226, -78.68011850195218),
    Location(4, "EB2", 5, 35.77184197261896, -78.67356047898443),
    Location(5, "Park Shops", 5, 35.78546665319359, -78.66708463594044),
    Location(6, "Talley", 5, 35.78392567533286, -78.67092696947988),
    Location(7, "Walnut", 6, 35.753166119681715, -78.74569648479638),
    Location(8, "Falls River", 7, 35.906477682429525, -78.59029227485301),
]

EXPECTED_TAGS: list[Tag] = [
    Tag(1, "Groceries", False, "groc"),
    Tag(2, "Gas", False, "gas"),
    Tag(3, "Anarack", True, None),
    Tag(4, "University", False, "uni"),
    Tag(5, "Dating", False, "date"),
    Tag(6, "Third Party Transaction", False, "paid for by parents"),
    Tag(7, "Eating Out", False, "eatout"),
    Tag(8, "Winter Park Trip", True, None),
    Tag(9, "The Maze Trip", True, None),
    Tag(10, "Personal", False, "personal"),
    Tag(11, "Coffee", False, "coffee"),
]

EXPECTED_AMOUNTS: list[Amount] = [
    Amount(1, 20.54, 1, None),
    Amount(2, 1245.34, 2, None),
    Amount(3, 12.98, 3, None),
    Amount(4, 34.82, 4, "PC Parts"),
    Amount(5, 12.63, 4, "Textbook"),
    Amount(6, -100, 5, None),
    Amount(7, 100, 6, None),
]


class Sample1TestCase(TestCase):
    """
    Base class for all unit tests relating to sample_database_1.db
    """

    def setUp(self):
        """
        Copy sample database file and connect to it.
        """
        shutil.copyfile(sample_database_1_path, test_database_path)
        database.connect(test_database_path)

    def tearDown(self):
        """
        Close database and delete test file.
        """
        database.close()
        os.remove(test_database_path)

    # pylint: disable=invalid-name
    def assertSqlEqual(self, expected: SqlObject, actual: SqlObject) -> None:
        """
        Asserts that two SqlObjects are equal and their IDs match.

        :param expected: Expected SqlObject
        :param actual: Actual SqlObjet
        :return: True if the two SqlObjects are equal and their IDs are equal, false if otherwise
        """
        self.assertEqual(expected.sqlid, actual.sqlid)
        self.assertEqual(expected, actual)

    # pylint: disable=invalid-name
    def assertSqlListEqual(
        self,
        expected_list: list[SqlObject],
        actual_list: list[SqlObject],
        strict_order: bool = True,
    ) -> None:
        """
        Asserts that two lists of SqlObjects are equal and their IDs match.
        To use non strict_order each SqlObject must have a sqlid set.

        :param expected_list: Expected list of SqlObject
        :param actual_list: Actual list of SqlObject
        :param strict_order: True if the order of the lists must be the same, false if they can
        be different
        """
        self.assertEqual(len(expected_list), len(actual_list))

        # Ensure order
        if strict_order:
            for expected, actual in zip(expected_list, actual_list):
                self.assertSqlEqual(expected, actual)

        # Sort objects by their sqlid then call this function with strict_order=True
        else:
            sorted_expected_list: list[SqlObject] = expected_list.copy()
            sorted_actual_list: list[SqlObject] = actual_list.copy()

            sorted_expected_list.sort(key=lambda x: x.sqlid)  # type: ignore
            sorted_actual_list.sort(key=lambda x: x.sqlid)  # type: ignore

            self.assertSqlListEqual(
                sorted_expected_list, sorted_actual_list, strict_order=True
            )
