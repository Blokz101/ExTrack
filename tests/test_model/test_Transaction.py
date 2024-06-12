from datetime import datetime

from src.model.Tag import Tag
from src.model.Account import Account
from src.model.Amount import Amount
from src.model.Merchant import Merchant
from src.model.Statement import Statement
from src.model.Transaction import Transaction
from tests.test_model.Sample1TestCase import Sample1TestCase

from src.model import date_format


class TestTransaction(Sample1TestCase):
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

    expected_amounts: list[Amount] = [
        Amount(1, 20.54, 1, None),
        Amount(2, 1245.34, 2, None),
        Amount(3, 12.98, 3, None),
        Amount(4, 34.82, 4, "PC Parts"),
        Amount(5, 12.63, 4, "Textbook"),
        Amount(6, -100, 5, None),
        Amount(7, 100, 6, None),
    ]

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

        expected_transactions: list[Transaction] = (
            TestTransaction.expected_transactions.copy()
        )
        expected_transactions.append(
            Transaction(
                7,
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

        # Update existing Transaction
        expected_transactions[2] = Transaction(
            3,
            "DND Dice Box",
            7,
            True,
            datetime.strptime("2022-02-03 18:45:17", date_format),
            2,
            None,
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
        transaction.lat = 35.90644784758162
        transaction.long = -78.59026491389089
        transaction.account_id = 2

        transaction.sync()

        self.assertSqlListEqual(expected_transactions, Transaction.get_all())

    def test_get_all(self):
        """
        Test Transaction.get_all().

        Prerequisite: None
        """

        self.assertSqlListEqual(
            TestTransaction.expected_transactions, Transaction.get_all()
        )

    def test_merchant(self):
        """
        Tests Transaction.merchant().

        Prerequisite: test_from_id()
        """

        self.assertEqual(
            Merchant(4, "Apple", False, None), Transaction.from_id(2).merchant()
        )

        self.assertEqual(
            Merchant(9, "Etsy", True, None), Transaction.from_id(3).merchant()
        )

        self.assertEqual(
            None,
            Transaction.from_id(6).merchant(),
        )

    def test_statement(self):
        """
        Tests Transaction.statement().

        Prerequisite: test_from_id()
        """

        self.assertEqual(
            Statement(5, "2019-08-25 12:58:05", None, 2),
            Transaction.from_id(2).statement(),
        )

        self.assertEqual(
            Statement(
                1, datetime.strptime("2019-02-14 17:48:20", date_format), None, 1
            ),
            Transaction.from_id(4).statement(),
        )

        self.assertEqual(
            None,
            Transaction.from_id(5).statement(),
        )

    def test_account(self):
        """
        Tests Transaction.account().

        Prerequisite: test_from_id()
        """

        self.assertEqual(
            Account(1, "Checking", 2, 3, 7), Transaction.from_id(1).account()
        )

        self.assertEqual(
            Account(2, "Savings", 3, 1, 5), Transaction.from_id(5).account()
        )

    def test_transfer_trans(self):
        """
        Tests Transaction.transfer_trans().

        Prerequisite: test_from_id()
        """

        self.assertEqual(
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
            Transaction.from_id(5).transfer_trans(),
        )

        self.assertEqual(
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
            Transaction.from_id(6).transfer_trans(),
        )

        self.assertEqual(
            None,
            Transaction.from_id(3).transfer_trans(),
        )

    def test_total_amount(self):
        """
        Tests Transaction.total_amount().

        Prerequisite: test_from_id()
        """

        self.assertEqual(34.82 + 12.63, Transaction.from_id(4).total_amount())

        self.assertEqual(1245.34, Transaction.from_id(2).total_amount())

    def test_amounts(self):
        """
        Tests Transaction.account()

        Prerequisite: test_from_id()
        """

        expected_amounts: list[Amount] = [
            Amount(4, 34.82, 4, "PC Parts"),
            Amount(5, 12.63, 4, "Textbook"),
        ]

        self.assertSqlListEqual(expected_amounts, Transaction.from_id(4).amounts())

        expected_amounts = [Amount(2, 1245.34, 2, None)]

        self.assertEqual(expected_amounts, Transaction.from_id(2).amounts())

    def test_split_amount(self):
        """
        Tests Transaction.split_amount(existing_amount_id: int, new_amount: float, description: str = "")

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
            f"This transaction does not have an amount with id = 3.", str(msg.exception)
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
            Tag(5, "Dating", False),
            Tag(7, "Eating Out", False),
        ]

        self.assertSqlListEqual(expected_tags, Transaction.from_id(1).tags())

        # Test with transaction 3
        expected_tags = [
            Tag(10, "Personal", False),
        ]

        self.assertSqlListEqual(expected_tags, Transaction.from_id(3).tags())

        # Test with transaction 2
        expected_tags = [
            Tag(4, "University", False),
            Tag(10, "Personal", False),
        ]

        self.assertSqlListEqual(expected_tags, Transaction.from_id(2).tags())
