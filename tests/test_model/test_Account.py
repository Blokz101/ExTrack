import os
import shutil
from unittest import TestCase

from src.model import database
from src.model.Account import Account
from tests.test_model import test_database, sample_database_1


class TestAccount(TestCase):

    expected_accounts: list[Account] = [
        Account(1, "Checking", 2, 3, 7),
        Account(2, "Savings", 3, 1, 5),
    ]

    def setUp(self):
        """
        Copy sample database file and connect to it.
        """
        shutil.copyfile(sample_database_1, test_database)
        database.connect(test_database)

    def tearDown(self):
        """
        Close database and delete test file.
        """
        database.close()
        os.remove(test_database)

    def test_from_id(self):
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

    def test_sync(self):
        """
        Tests Account.sync()

        Prerequisite: test_get_all() and from_id(sqlid: int)
        """

        expected_accounts: list[Account] = TestAccount.expected_accounts
        expected_accounts.append(Account(3, "BJS Card", 1, 2, 6))

        # Test create new Account
        account: Account = Account(None, "BJS Card", 1, 2, 6)
        account.sync()

        actual_accounts: list[Account] = Account.get_all()
        self.assertEqual(len(expected_accounts), len(actual_accounts))
        for expected_account, actual_account in zip(expected_accounts, actual_accounts):
            self.assertEqual(expected_account.sqlid, actual_account.sqlid)
            self.assertEqual(expected_account, actual_account)

        # Update existing Account
        expected_accounts[1] = Account(2, "College Funds", 5, 3, 4)

        account: Account = Account.from_id(2)
        account.name = "College Funds"
        account.amount_idx = 5
        account.description_idx = 3
        account.date_idx = 4

        account.sync()

        actual_accounts: list[Account] = Account.get_all()
        self.assertEqual(len(TestAccount.expected_accounts), len(actual_accounts))
        for expected_account, actual_account in zip(expected_accounts, actual_accounts):
            self.assertEqual(expected_account.sqlid, actual_account.sqlid)
            self.assertEqual(expected_account, actual_account)

    def test_get_all(self):
        """
        Test Account.get_all()

        Prerequisite: None
        """

        actual_accounts: list[Account] = Account.get_all()

        self.assertEqual(len(TestAccount.expected_accounts), len(actual_accounts))
        for expected_account, actual_account in zip(
            TestAccount.expected_accounts, actual_accounts
        ):
            self.assertEqual(expected_account.sqlid, actual_account.sqlid)
            self.assertEqual(expected_account, actual_account)
