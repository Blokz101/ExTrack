"""
Test the Amount class.
"""

# mypy: ignore-errors

from src.model import database
from src.model.amount import Amount
from src.model.tag import Tag
from tests.test_model.sample_1_test_case import (
    Sample1TestCase,
    EXPECTED_AMOUNTS,
    EXPECTED_TRANSACTIONS,
    EXPECTED_TAGS,
)


class TestAmount(Sample1TestCase):
    """
    Tests the Amount class.
    """

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

        expected_amounts: list[Amount] = EXPECTED_AMOUNTS.copy()
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
        self.assertSqlListEqual(EXPECTED_AMOUNTS, Amount.get_all())

        # Try to sync with the required fields
        amount = Amount(amount=57.34, transaction_id=3)

        self.assertIsNone(amount.syncable())

        amount.sync()
        self.assertSqlListEqual(EXPECTED_AMOUNTS + [amount], Amount.get_all())

    def test_get_all(self):
        """
        Test Amount.get_all()

        Prerequisite: None
        """

        self.assertSqlListEqual(EXPECTED_AMOUNTS, Amount.get_all())

    def test_transaction(self):
        """
        Tests Amount.Transactions()

        Prerequisite: test_from_id()
        """

        # Test with amount 2
        self.assertSqlEqual(
            EXPECTED_TRANSACTIONS[2 - 1], Amount.from_id(2).transaction()
        )

        # Test with amount 4 and 5
        self.assertSqlEqual(
            EXPECTED_TRANSACTIONS[4 - 1], Amount.from_id(4).transaction()
        )

        self.assertSqlEqual(
            EXPECTED_TRANSACTIONS[4 - 1], Amount.from_id(5).transaction()
        )

        # Test with new Amount
        self.assertEqual(None, Amount().transaction())

    def test_delete(self):
        """
        Tests Amount.delete()

        Prerequisite: test_from_id() and test_get_all()
        """

        # Test with valid amounts
        expected_amounts: list[Amount] = EXPECTED_AMOUNTS.copy()
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
        expected_tags: list[Tag] = [EXPECTED_TAGS[5 - 1], EXPECTED_TAGS[7 - 1]]
        actual_tags: list[Tag] = Amount.from_id(1).tags()

        self.assertSqlListEqual(expected_tags, actual_tags)

        # Test with amount 2
        expected_tags: list[Tag] = [EXPECTED_TAGS[4 - 1], EXPECTED_TAGS[10 - 1]]
        actual_tags: list[Tag] = Amount.from_id(2).tags()

        self.assertSqlListEqual(actual_tags, expected_tags)

        # Test with amount 4
        expected_tags: list[Tag] = [EXPECTED_TAGS[3 - 1]]
        actual_tags: list[Tag] = Amount.from_id(4).tags()

        self.assertSqlListEqual(expected_tags, actual_tags)

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
