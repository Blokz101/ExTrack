from datetime import datetime

from src.model import date_format
from src.model.Transaction import Transaction
from src.model.Statement import Statement
from src.model.Account import Account
from tests.test_model.Sample1TestCase import Sample1TestCase


class TestAccount(Sample1TestCase):

    expected_accounts: list[Account] = [
        Account(1, "Checking", 2, 3, 7),
        Account(2, "Savings", 3, 1, 5),
    ]

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

        Prerequisite: test_get_all() and test_from_id()
        """

        expected_accounts: list[Account] = TestAccount.expected_accounts.copy()
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

        account: Account = Account.from_id(2)
        account.name = "College Funds"
        account.amount_idx = 5
        account.description_idx = 3
        account.date_idx = 4

        account.sync()

        self.assertSqlListEqual(expected_accounts, Account.get_all())

    def test_syncable(self):
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
        self.assertSqlListEqual(TestAccount.expected_accounts, Account.get_all())

        # Try to sync with required fields
        account = Account(name="University")

        self.assertIsNone(account.syncable())

        account.sync()
        self.assertSqlListEqual(
            TestAccount.expected_accounts + [account], Account.get_all()
        )

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

    def test_transactions(self):
        """
        Tests Account.transactions()

        Prerequisite: test_from_id()
        """

        expected_transactions: list[Transaction] = [
            Transaction(
                1,
                "Date with Sara",
                1,
                False,
                datetime.strptime("2020-08-27 21:14:40", date_format),
                None,
                None,
                35.868317424041166,
                -78.62154243252625,
                1,
                None,
            ),
            Transaction(
                3,
                "DND Dice",
                9,
                True,
                datetime.strptime("2023-05-04 23:44:29", date_format),
                1,
                None,
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
        self.assertSqlListEqual(
            expected_transactions, Account.from_id(1).transactions()
        )

        expected_transactions = [
            Transaction(
                2,
                "New Macbook",
                4,
                True,
                datetime.strptime("2020-10-09 19:01:21", date_format),
                5,
                None,
                35.840809717971595,
                -78.68013948171635,
                2,
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
        ]
        self.assertSqlListEqual(
            expected_transactions, Account.from_id(2).transactions()
        )

    def test_statements(self):
        """
        Tests Account.statements()

        Prerequisite: test_from_id()
        """

        expected_statements_1: list[Statement] = [
            Statement(1, "2019-02-14 17:48:20", None, 1),
            Statement(2, "2020-07-08 07:12:34", None, 1),
            Statement(3, "2023-07-20 05:46:37", None, 1),
        ]

        expected_statements_2: list[Statement] = [
            Statement(4, "2018-12-21 08:21:34", None, 2),
            Statement(5, "2019-08-25 12:58:05", None, 2),
            Statement(6, "2021-04-22 09:01:52", None, 2),
        ]

        self.assertEqual(expected_statements_1, Account.from_id(1).statements())

        self.assertEqual(expected_statements_2, Account.from_id(2).statements())
