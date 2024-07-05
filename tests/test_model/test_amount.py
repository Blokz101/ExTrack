"""
Test the Amount class.
"""

# mypy: ignore-errors
from datetime import datetime

from src.model import date_format, database
from src.model.amount import Amount
from src.model.tag import Tag
from src.model.transaction import Transaction
from tests.test_model.sample_1_test_case import Sample1TestCase


class TestAmount(Sample1TestCase):
    """
    Tests the Amount class.
    """

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
        Tests Amount.from_id(sqlid: int)

        Prerequisite: test_get_all()
        """

        # Test valid amounts
        expected_amounts: list[Amount] = Amount.get_all()

        for expected_amount in expected_amounts:
            self.assertEqual(expected_amount, Amount.from_id(expected_amount.sqlid))

        # Test invalid amount
        with self.assertRaises(ValueError) as msg:
            Amount.from_id(-1)
        self.assertEqual("No amount with id = -1.", str(msg.exception))

        with self.assertRaises(ValueError) as msg:
            Amount.from_id(8)
        self.assertEqual("No amount with id = 8.", str(msg.exception))

    def test_sync(self):
        """
        Tests Amount.sync()

        Prerequisite: test_get_all() and test_from_id()
        """

        expected_amounts: list[Amount] = TestAmount.expected_amounts.copy()
        expected_amounts.append(Amount(8, 65.48, 4, "Box Fan"))

        # Test create new Amount
        amount: Amount = Amount(None, 65.48, 4, "Box Fan")
        amount.sync()

        self.assertSqlListEqual(expected_amounts, Amount.get_all())
        self.assertEqual(8, amount.sqlid)

        # Update existing Amount
        expected_amounts[3] = Amount(4, 2.45, 3, "Gum separate from rest of purchase.")

        amount = Amount.from_id(4)
        amount.amount = 2.45
        amount.transaction_id = 3
        amount.description = "Gum separate from rest of purchase."

        amount.sync()

        self.assertSqlListEqual(expected_amounts, Amount.get_all())
        self.assertEqual(4, amount.sqlid)

        # Test with "" text fields
        amount = Amount.from_id(4)
        amount.description = ""
        amount.sync()

        self.assertIsNone(Amount.from_id(4).description)

    def test_syncable(self):
        """
        Test Amount.syncable() and Amount.sync()

        Prerequisite: test_get_all() and test_sync()
        """
        amount: Amount = Amount(None, None, None, "Box Fan")

        # Try to sync without required fields
        self.assertEqual(
            ["amount cannot be None.", "transaction_id cannot be None."],
            amount.syncable(),
        )

        with self.assertRaises(RuntimeError) as msg:
            amount.sync()
        self.assertEqual("amount cannot be None.", str(msg.exception))
        self.assertSqlListEqual(TestAmount.expected_amounts, Amount.get_all())

        # Try to sync with the required fields
        amount = Amount(amount=57.34, transaction_id=3)

        self.assertIsNone(amount.syncable())

        amount.sync()
        self.assertSqlListEqual(
            TestAmount.expected_amounts + [amount], Amount.get_all()
        )

    def test_get_all(self):
        """
        Test Amount.get_all()

        Prerequisite: None
        """

        self.assertSqlListEqual(TestAmount.expected_amounts, Amount.get_all())

    def test_transaction(self):
        """
        Tests Amount.Transactions()

        Prerequisite: test_from_id()
        """

        # Test with amount 2
        self.assertSqlEqual(
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
            Amount.from_id(2).transaction(),
        )

        # Test with amount 4 and 5
        self.assertSqlEqual(
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
            Amount.from_id(4).transaction(),
        )

        self.assertSqlEqual(
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
            Amount.from_id(5).transaction(),
        )

        # Test with new Amount
        self.assertEqual(None, Amount().transaction())

    def test_delete(self):
        """
        Tests Amount.delete()

        Prerequisite: test_from_id() and test_get_all()
        """

        # Test with valid amounts
        expected_amounts: list[Amount] = TestAmount.expected_amounts.copy()
        expected_amounts.pop(3)

        Amount.from_id(4).delete()

        self.assertSqlListEqual(expected_amounts, Amount.get_all())

        # Ensure that the amount_tag branches have been deleted
        _, cur = database.get_connection()
        cur.execute("SELECT 1 FROM amount_tags WHERE amount_id = 4")
        self.assertEqual([], cur.fetchall())

        # Test with invalid amount
        with self.assertRaises(RuntimeError) as msg:
            Amount.from_id(2).delete()
        self.assertEqual(
            "Cannot delete amount with id = 2 because transaction with id = 2 would be left "
            "without an amount.",
            str(msg.exception),
        )

    def test_tags(self):
        """
        Tests Amount.tags()

        Prerequisite: test_from_id()
        """

        # Test with amount 1
        expected_tags: list[Tag] = [
            Tag(5, "Dating", False),
            Tag(7, "Eating Out", False),
        ]

        actual_tags: list[Tag] = Amount.from_id(1).tags()

        self.assertEqual(len(expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

        # Test with amount 2
        expected_tags: list[Tag] = [
            Tag(4, "University", False),
            Tag(10, "Personal", False),
        ]

        actual_tags: list[Tag] = Amount.from_id(2).tags()

        self.assertEqual(len(expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

        # Test with amount 4
        expected_tags: list[Tag] = [
            Tag(3, "Anarack", True),
        ]

        actual_tags: list[Tag] = Amount.from_id(4).tags()

        self.assertEqual(len(expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

        # Test with new amount
        self.assertEqual([], Amount().tags())

    def test_set_tags(self):
        """
        Tests Amount.set_tags()
        """
        amount: Amount
        expected_tags: list[Tag]

        # Test with 34.82
        amount = Amount.from_id(1)
        expected_tags = [Tag.from_id(10), Tag.from_id(4)]
        amount.set_tags(list(tag.sqlid for tag in expected_tags))

        self.assertSqlListEqual(expected_tags, amount.from_id(1).tags())

        # Test with 34.82 and adding tags
        amount = Amount.from_id(4)
        expected_tags = [Tag.from_id(3), Tag.from_id(7)]
        amount.set_tags(list(tag.sqlid for tag in expected_tags))

        self.assertSqlListEqual(expected_tags, amount.from_id(4).tags())

        # Test with 1245.34 and removing tags
        amount = Amount.from_id(2)
        expected_tags = []
        amount.set_tags(list(tag.sqlid for tag in expected_tags))

        self.assertSqlListEqual(expected_tags, amount.from_id(2).tags())

        # Test with a new amount
        with self.assertRaises(RuntimeError) as msg:
            Amount().set_tags([0, 3])
        self.assertEqual(
            "Cannot set tags of an amount that does not exist in the database.",
            str(msg.exception),
        )
