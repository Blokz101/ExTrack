"""
Tests the Account class.
"""

import json
import os

from model import UserSettings

# mypy: ignore-errors

from src import model
from src.model.account import Account
from src.model.statement import Statement
from src.model.transaction import Transaction
from tests.test_model import test_settings_file_path, test_database_path
from tests.test_model.sample_1_test_case import (
    Sample1TestCase,
    EXPECTED_ACCOUNTS,
    EXPECTED_TRANSACTIONS,
    EXPECTED_STATEMENTS,
)


class TestAccount(Sample1TestCase):
    """
    Tests the Account class.
    """

    def test_from_id(self) -> None:
        """
        Tests Account.from_id(sqlid: int)

        Prerequisite: test_get_all()
        """

        # Test valid accounts
        expected_accounts: list[Account] = Account.get_all()

        for expected_account in expected_accounts:
            self.assertEqual(expected_account, Account.from_id(expected_account.sqlid))

        # Test invalid accounts
        with self.assertRaises(ValueError) as msg:
            Account.from_id(-1)
        self.assertEqual("No account with id = -1.", str(msg.exception))

        with self.assertRaises(ValueError) as msg:
            Account.from_id(3)
        self.assertEqual("No account with id = 3.", str(msg.exception))

    def test_sync(self) -> None:
        """
        Tests Account.sync()

        Prerequisite: test_get_all() and test_from_id()
        """

        expected_accounts: list[Account] = EXPECTED_ACCOUNTS.copy()
        expected_accounts.append(Account(3, "BJS Card", 1, 2, 6))

        # Test create new Account
        account: Account = Account(None, "BJS Card", 1, 2, 6)
        account.sync()

        actual_accounts: list[Account] = Account.get_all()
        self.assertEqual(len(expected_accounts), len(actual_accounts))

        self.assertSqlListEqual(expected_accounts, actual_accounts)
        self.assertEqual(3, account.sqlid)

        # Update existing Account
        expected_accounts[1] = Account(2, "College Funds", 5, 3, 4)

        account = Account.from_id(2)
        account.name = "College Funds"
        account.amount_idx = 5
        account.description_idx = 3
        account.date_idx = 4

        account.sync()

        self.assertSqlListEqual(expected_accounts, Account.get_all())
        self.assertEqual(2, account.sqlid)

        # Sync with "" text fields
        account = Account.from_id(2)
        account.name = ""
        with self.assertRaises(RuntimeError):
            account.sync()

    def test_syncable(self) -> None:
        """
        Tests Account.syncable() and Account.sync()

        Prerequisites: test_get_all() and test_sync()
        """
        account: Account = Account(None, None, 1, 2, 6)

        # Try to sync without required fields
        self.assertEqual(["name cannot be None."], account.syncable())

        with self.assertRaises(RuntimeError) as msg:
            account.sync()
        self.assertEqual("name cannot be None.", str(msg.exception))
        self.assertSqlListEqual(EXPECTED_ACCOUNTS, Account.get_all())

        # Try to sync with required fields
        account = Account(name="University")

        self.assertIsNone(account.syncable())

        account.sync()
        self.assertSqlListEqual(EXPECTED_ACCOUNTS + [account], Account.get_all())

    def test_get_all(self) -> None:
        """
        Test Account.get_all()

        Prerequisite: None
        """

        actual_accounts: list[Account] = Account.get_all()

        self.assertSqlListEqual(EXPECTED_ACCOUNTS, actual_accounts)

    def test_transactions(self) -> None:
        """
        Tests Account.transactions()

        Prerequisite: test_from_id()
        """

        expected_transactions: list[Transaction] = [
            EXPECTED_TRANSACTIONS[1 - 1],
            EXPECTED_TRANSACTIONS[3 - 1],
            EXPECTED_TRANSACTIONS[4 - 1],
            EXPECTED_TRANSACTIONS[6 - 1],
            EXPECTED_TRANSACTIONS[7 - 1],
        ]
        self.assertSqlListEqual(
            expected_transactions, Account.from_id(1).transactions()
        )

        expected_transactions = [
            EXPECTED_TRANSACTIONS[2 - 1],
            EXPECTED_TRANSACTIONS[5 - 1],
        ]
        self.assertSqlListEqual(
            expected_transactions, Account.from_id(2).transactions()
        )

        # Test with new Account
        self.assertEqual([], Account().transactions())

    def test_statements(self) -> None:
        """
        Tests Account.statements()

        Prerequisite: test_from_id()
        """

        expected_statements_1: list[Statement] = [
            EXPECTED_STATEMENTS[1 - 1],
            EXPECTED_STATEMENTS[2 - 1],
            EXPECTED_STATEMENTS[3 - 1],
        ]

        expected_statements_2: list[Statement] = [
            EXPECTED_STATEMENTS[4 - 1],
            EXPECTED_STATEMENTS[5 - 1],
            EXPECTED_STATEMENTS[6 - 1],
        ]

        self.assertSqlListEqual(expected_statements_1, Account.from_id(1).statements())

        self.assertSqlListEqual(expected_statements_2, Account.from_id(2).statements())

        # Test with new Account
        self.assertEqual([], Account().statements())

    def test_default_account(self):
        """
        Tests Account.default_account()
        """
        # Setup
        if test_settings_file_path.exists():
            os.remove(test_settings_file_path)
        model.app_settings = UserSettings(test_settings_file_path)

        # Main Test
        self.assertFalse(test_settings_file_path.exists())

        # Test with a settings file that lacks location_scan_radius
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            file.write("{}")
        model.app_settings.load_settings()

        self.assertTrue(test_settings_file_path.exists())
        self.assertIsNone(model.app_settings.default_account())

        # Test with a settings file and valid default_account
        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"default_account": "Checking"}, file)
        model.app_settings.load_settings()

        self.assertSqlEqual(Account.from_id(1), Account.default_account())

        with open(test_settings_file_path, "w", encoding="utf-8") as file:
            json.dump({"default_account": "Savings"}, file)
        model.app_settings.load_settings()

        self.assertSqlEqual(Account.from_id(2), Account.default_account())

        # Teardown
        if test_settings_file_path.exists():
            os.remove(test_settings_file_path)
