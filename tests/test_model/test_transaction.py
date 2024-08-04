"""
Tests the Transaction class.
"""

# mypy: ignore-errors
from datetime import datetime

from src.model import date_format
from src.model.amount import Amount
from src.model.tag import Tag
from src.model.transaction import Transaction
from tests.test_model.sample_1_test_case import (
    Sample1TestCase,
    EXPECTED_TRANSACTIONS,
    EXPECTED_STATEMENTS,
    EXPECTED_ACCOUNTS,
    EXPECTED_MERCHANTS,
    EXPECTED_AMOUNTS,
    EXPECTED_TAGS,
)


class TestTransaction(Sample1TestCase):
    """
    Tests the Transaction class.
    """

    def test_from_id(self):
        """
        Tests Transaction.from_id(sqlid: int).

        Prerequisite: test_get_all()
        """

        # Test valid Transactions
        expected_transactions: list[Transaction] = Transaction.get_all()

        for expected_transaction in expected_transactions:
            self.assertEqual(
                expected_transaction, Transaction.from_id(expected_transaction.sqlid)
            )

        # Test invalid Transaction
        with self.assertRaises(ValueError) as msg:
            Transaction.from_id(-1)
        self.assertEqual("No transaction with id = -1.", str(msg.exception))

        with self.assertRaises(ValueError) as msg:
            Transaction.from_id(20)
        self.assertEqual("No transaction with id = 20.", str(msg.exception))

    def test_sync(self):
        """
        Tests Transaction.sync().

        Prerequisite: test_get_all() and test_from_id()
        """

        expected_transactions: list[Transaction] = EXPECTED_TRANSACTIONS.copy()
        expected_transactions.append(
            Transaction(
                8,
                "Fancy date with Sara",
                2,
                False,
                "2021-12-10 21:43:08",
                None,
                None,
                35.85667580264126,
                -78.58033709794717,
                1,
                None,
            )
        )

        # Test create new Transaction
        transaction: Transaction = Transaction(
            None,
            "Fancy date with Sara",
            2,
            False,
            "2021-12-10 21:43:08",
            None,
            None,
            35.85667580264126,
            -78.58033709794717,
            1,
            None,
        )
        transaction.sync()

        self.assertSqlListEqual(expected_transactions, Transaction.get_all())
        self.assertEqual(8, transaction.sqlid)

        # Update existing Transaction
        expected_transactions[2] = Transaction(
            3,
            "DND Dice Box",
            7,
            True,
            datetime.strptime("2022-02-03 18:45:17", date_format),
            2,
            "CHANGEDIMG.png",
            35.90644784758162,
            -78.59026491389089,
            2,
            None,
        )

        transaction = Transaction.from_id(3)
        transaction.description = "DND Dice Box"
        transaction.merchant_id = 7
        transaction.reconciled = True
        transaction.date = datetime.strptime("2022-02-03 18:45:17", date_format)
        transaction.statement_id = 2
        transaction.receipt_file_name = "CHANGEDIMG.png"
        transaction.lat = 35.90644784758162
        transaction.long = -78.59026491389089
        transaction.account_id = 2

        transaction.sync()

        self.assertSqlListEqual(expected_transactions, Transaction.get_all())
        self.assertEqual(3, transaction.sqlid)

        # Test with "" fields
        transaction = Transaction.from_id(3)
        transaction.description = ""
        transaction.sync()

        self.assertIsNone(Transaction.from_id(3).description)

        transaction = Transaction.from_id(2)
        transaction.receipt_file_name = ""
        transaction.sync()

        self.assertIsNone(Transaction.from_id(2).receipt_file_name)

    def test_syncable(self):
        """
        Tests Transaction.syncable() and Transaction.sync()

        Prerequisite: test_get_all() and test_sync()
        """
        trans: Transaction = Transaction(
            None,
            "Fancy date with Sara",
            2,
            None,
            "2021-12-10 21:43:08",
            None,
            None,
            35.85667580264126,
            -78.58033709794717,
            None,
            None,
        )

        # Try to sync without required fields
        self.assertEqual(
            ["reconciled cannot be None.", "account_id cannot be None."],
            trans.syncable(),
        )

        with self.assertRaises(RuntimeError) as msg:
            trans.sync()
        self.assertEqual("reconciled cannot be None.", str(msg.exception))
        self.assertSqlListEqual(EXPECTED_TRANSACTIONS, Transaction.get_all())

        # Try to sync with required fields
        trans = Transaction(reconciled=True, account_id=1)

        self.assertIsNone(trans.syncable())

        trans.sync()
        self.assertSqlListEqual(EXPECTED_TRANSACTIONS + [trans], Transaction.get_all())

    def test_get_all(self):
        """
        Test Transaction.get_all().

        Prerequisite: None
        """

        self.assertSqlListEqual(EXPECTED_TRANSACTIONS, Transaction.get_all())

    def test_merchant(self):
        """
        Tests Transaction.merchant().

        Prerequisite: test_from_id()
        """

        self.assertEqual(EXPECTED_MERCHANTS[4 - 1], Transaction.from_id(2).merchant())

        self.assertEqual(EXPECTED_MERCHANTS[9 - 1], Transaction.from_id(3).merchant())

        self.assertEqual(
            None,
            Transaction.from_id(6).merchant(),
        )

        # Test with new Transaction
        self.assertEqual(None, Transaction().merchant())

    def test_statement(self):
        """
        Tests Transaction.statement().

        Prerequisite: test_from_id()
        """

        self.assertEqual(
            EXPECTED_STATEMENTS[5 - 1],
            Transaction.from_id(2).statement(),
        )

        self.assertEqual(
            EXPECTED_STATEMENTS[1 - 1],
            Transaction.from_id(4).statement(),
        )

        self.assertEqual(
            None,
            Transaction.from_id(5).statement(),
        )

        # Test with new Transaction
        self.assertEqual(None, Transaction().statement())

    def test_account(self):
        """
        Tests Transaction.account().

        Prerequisite: test_from_id()
        """

        self.assertEqual(EXPECTED_ACCOUNTS[1 - 1], Transaction.from_id(1).account())
        self.assertEqual(EXPECTED_ACCOUNTS[2 - 1], Transaction.from_id(5).account())

        # Test with new Transaction
        self.assertEqual(None, Transaction().account())

    def test_transfer_trans(self):
        """
        Tests Transaction.transfer_trans().

        Prerequisite: test_from_id()
        """

        self.assertEqual(
            EXPECTED_TRANSACTIONS[6 - 1],
            Transaction.from_id(5).transfer_trans(),
        )

        self.assertEqual(
            EXPECTED_TRANSACTIONS[5 - 1],
            Transaction.from_id(6).transfer_trans(),
        )

        self.assertIsNone(Transaction.from_id(3).transfer_trans())

        # Test with new Transaction
        self.assertIsNone(Transaction().transfer_trans())

    def test_total_amount(self):
        """
        Tests Transaction.total_amount().

        Prerequisite: test_from_id()
        """

        self.assertEqual(34.82 + 12.63, Transaction.from_id(4).total_amount())

        self.assertEqual(1245.34, Transaction.from_id(2).total_amount())

        # Test with new Transaction
        self.assertEqual(0, Transaction().total_amount())

    def test_amounts(self):
        """
        Tests Transaction.account()

        Prerequisite: test_from_id()
        """

        expected_amounts: list[Amount] = [
            EXPECTED_AMOUNTS[4 - 1],
            EXPECTED_AMOUNTS[5 - 1],
        ]

        self.assertSqlListEqual(expected_amounts, Transaction.from_id(4).amounts())

        expected_amounts = [EXPECTED_AMOUNTS[2 - 1]]

        self.assertEqual(expected_amounts, Transaction.from_id(2).amounts())

        # Test with new Transaction
        self.assertEqual([], Transaction().amounts())

    def test_split_amount(self):
        """
        Tests Transaction.split_amount(existing_amount_id: int, new_amount: float, description: str
        = "")

        Prerequisite: test_from_id() and test_total_amount() and test_amounts()
        """

        # Split valid amounts
        expected_amounts: list[Amount] = [
            Amount(2, 1245.34 - 16.43, 2, None),
            Amount(8, 16.43, 2, "Laptop case"),
        ]

        Transaction.from_id(2).split_amount(2, 16.43, "Laptop case")

        self.assertSqlListEqual(expected_amounts, Transaction.from_id(2).amounts())

        self.assertEqual(1245.34, Transaction.from_id(2).total_amount())

        # Split invalid amounts
        with self.assertRaises(ValueError) as msg:
            # Trying to split 12.98 into 13 and something
            Transaction.from_id(3).split_amount(3, 13, "illegal split")
        self.assertEqual(
            "Cannot split $13 from existing amount $12.98.", str(msg.exception)
        )

        with self.assertRaises(ValueError) as msg:
            Transaction.from_id(6).split_amount(3, 2.41, "illegal split")
        self.assertEqual(
            "This transaction does not have an amount with id = 3.", str(msg.exception)
        )

    def test_combine_amounts(self):
        """
        Tests Transaction.combine_amount(first_amount_id: int, second_amount_id: int,
        new_description: Optional[str] = None)

        Prerequisite: test_from_id() and test_total_amount() and test_amounts()
        """

        # Test valid amount
        expected_amounts: list[Amount] = [
            Amount(4, 34.82 + 12.63, 4, "A single purchase")
        ]

        Transaction.from_id(4).combine_amount(4, 5, "A single purchase")

        self.assertSqlListEqual(expected_amounts, Transaction.from_id(4).amounts())

        # Test invalid amount
        with self.assertRaises(ValueError) as msg:
            Transaction.from_id(6).combine_amount(7, 2)
        self.assertEqual(
            "Transaction with id = 6 has no amount with id = 2.", str(msg.exception)
        )

        with self.assertRaises(ValueError) as msg:
            Transaction.from_id(6).combine_amount(2, 7)
        self.assertEqual(
            "Transaction with id = 6 has no amount with id = 2.", str(msg.exception)
        )

    def test_tags(self):
        """
        Test Transaction.tags()

        Prerequisites: test_from_id()
        """

        # Test with transaction 1
        expected_tags: list[Tag] = [
            EXPECTED_TAGS[5 - 1],
            EXPECTED_TAGS[7 - 1],
        ]

        self.assertSqlListEqual(expected_tags, Transaction.from_id(1).tags())

        # Test with transaction 3
        expected_tags = [EXPECTED_TAGS[10 - 1]]

        self.assertSqlListEqual(expected_tags, Transaction.from_id(3).tags())

        # Test with transaction 2
        expected_tags = [
            EXPECTED_TAGS[4 - 1],
            EXPECTED_TAGS[10 - 1],
        ]

        self.assertSqlListEqual(expected_tags, Transaction.from_id(2).tags())

        # Test with new Transaction
        self.assertEqual([], Transaction().tags())
