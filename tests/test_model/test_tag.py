"""
Tests the Tag class.
"""

# mypy: ignore-errors

from src.model.amount import Amount
from src.model.merchant import Merchant
from src.model.tag import Tag
from src.model.transaction import Transaction
from tests.test_model.sample_1_test_case import (
    Sample1TestCase,
    EXPECTED_TAGS,
    EXPECTED_MERCHANTS,
    EXPECTED_AMOUNTS,
    EXPECTED_TRANSACTIONS,
)


class TagTestCase(Sample1TestCase):
    """
    Tests the Tag class.
    """

    def test_from_id(self):
        """
        Tests Tag.from_id(sqlid: int)

        Prerequisite: test_get_all()
        """
        self.assertSqlListEqual(EXPECTED_TAGS, Tag.get_all())

        # Test invalid tags
        with self.assertRaises(ValueError) as msg:
            Tag.from_id(-1)
        self.assertEqual("No tag with id = -1.", str(msg.exception))

        with self.assertRaises(ValueError) as msg:
            Tag.from_id(12)
        self.assertEqual("No tag with id = 12.", str(msg.exception))

    def test_sync(self):
        """
        Tests Tag.sync()

        Prerequisite: test_get_all() and test_from_id()
        """
        # Test create new Tag
        expected_tags: list[Tag] = EXPECTED_TAGS.copy()
        expected_tags.append(Tag(12, "Other", False, "other"))

        tag: Tag = Tag(None, "Other", False, "other")
        tag.sync()

        self.assertSqlListEqual(expected_tags, Tag.get_all())
        self.assertEqual(12, tag.sqlid)

        # Update existing Merchant
        expected_tags[5] = Tag(6, "Christmas Gifts", True, None)

        tag = Tag.from_id(6)
        tag.name = "Christmas Gifts"
        tag.occasional = True
        tag.rule = None

        tag.sync()

        self.assertSqlListEqual(expected_tags, Tag.get_all())
        self.assertEqual(6, tag.sqlid)

        # Test with "" text fields
        tag = Tag.from_id(2)
        tag.name = ""

        with self.assertRaises(RuntimeError):
            tag.sync()

    def test_syncable(self):
        """
        Tests Tag.syncable() and Tag.sync()

        Prerequisite: test_get_all() and test_sync()
        """
        tag: Tag = Tag(None, None, None, "other")

        # Try to sync without required fields
        self.assertEqual(
            ["name cannot be None.", "occasional cannot be None."], tag.syncable()
        )

        with self.assertRaises(RuntimeError) as msg:
            tag.sync()
        self.assertEqual("name cannot be None.", str(msg.exception))
        self.assertSqlListEqual(EXPECTED_TAGS, Tag.get_all())

        # Try to sync with required fields
        tag = Tag(name="Gaming", occasional=False)

        self.assertIsNone(tag.syncable())

        tag.sync()
        self.assertSqlListEqual(EXPECTED_TAGS + [tag], Tag.get_all())

    def test_get_all(self):
        """
        Tests Tag.get_all()

        Prerequisite: None
        """

        actual_tags: list[Tag] = Tag.get_all()

        self.assertSqlListEqual(EXPECTED_TAGS, actual_tags)

    def test_default_merchants(self):
        """
        Tests Tag.default_merchants()

        Prerequisite: test_from_id
        """

        # Test with Personal
        expected_merchants: list[Merchant] = [
            EXPECTED_MERCHANTS[4 - 1],
            EXPECTED_MERCHANTS[8 - 1],
            EXPECTED_MERCHANTS[9 - 1],
        ]
        actual_merchants: list[Merchant] = Tag.from_id(10).default_merchants()

        self.assertSqlListEqual(expected_merchants, actual_merchants)

        # Test with Eating Out
        expected_merchants = [
            EXPECTED_MERCHANTS[1 - 1],
            EXPECTED_MERCHANTS[2 - 1],
        ]
        actual_merchants = Tag.from_id(7).default_merchants()

        self.assertSqlListEqual(expected_merchants, actual_merchants)

        # Test with Coffee
        expected_merchants = [EXPECTED_MERCHANTS[5 - 1]]
        actual_merchants = Tag.from_id(11).default_merchants()

        self.assertSqlListEqual(expected_merchants, actual_merchants)

        # Test with new Tag
        self.assertEqual([], Tag().default_merchants())

    def test_amounts(self):
        """
        Tests Tag.amounts()

        Prerequisite: test_from_id()
        """

        # Test with Anarack
        expected_amounts: list[Amount] = [EXPECTED_AMOUNTS[4 - 1]]

        actual_amounts: list[Amount] = Tag.from_id(3).amounts()
        self.assertSqlListEqual(expected_amounts, actual_amounts)

        # Test with Personal
        expected_amounts: list[Amount] = [
            EXPECTED_AMOUNTS[2 - 1],
            EXPECTED_AMOUNTS[3 - 1],
        ]

        actual_amounts: list[Amount] = Tag.from_id(10).amounts()
        self.assertSqlListEqual(expected_amounts, actual_amounts)

        # Tset with new tag
        self.assertEqual([], Tag().amounts())

    def test_transactions(self):
        """
        Tests Tag.transactions()

        Prerequisites: test_from_id
        """

        # Test with tag 10
        expected_transactions: list[Transaction] = [
            EXPECTED_TRANSACTIONS[2 - 1],
            EXPECTED_TRANSACTIONS[3 - 1],
        ]

        self.assertSqlListEqual(expected_transactions, Tag.from_id(10).transactions())

        # Test with tag 4
        expected_transactions = [
            EXPECTED_TRANSACTIONS[2 - 1],
            EXPECTED_TRANSACTIONS[4 - 1],
        ]

        self.assertSqlListEqual(expected_transactions, Tag.from_id(4).transactions())

        # Test with tag 5
        expected_transactions = [EXPECTED_TRANSACTIONS[1 - 1]]

        self.assertSqlListEqual(expected_transactions, Tag.from_id(5).transactions())

        # Test with new tag
        self.assertEqual([], Tag().transactions())
