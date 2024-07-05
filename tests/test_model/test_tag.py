"""
Tests the Tag class.
"""

# mypy: ignore-errors
from datetime import datetime

from src.model import date_format
from src.model.amount import Amount
from src.model.merchant import Merchant
from src.model.tag import Tag
from src.model.transaction import Transaction
from tests.test_model.sample_1_test_case import Sample1TestCase


class TagTestCase(Sample1TestCase):
    """
    Tests the Tag class.
    """

    expected_tags: list[Tag] = [
        Tag(1, "Groceries", False),
        Tag(2, "Gas", False),
        Tag(3, "Anarack", True),
        Tag(4, "University", False),
        Tag(5, "Dating", False),
        Tag(6, "Third Party Transaction", False),
        Tag(7, "Eating Out", False),
        Tag(8, "Winter Park Trip", True),
        Tag(9, "The Maze Trip", True),
        Tag(10, "Personal", False),
        Tag(11, "Coffee", False),
    ]

    def test_from_id(self):
        """
        Tests Tag.from_id(sqlid: int)

        Prerequisite: test_get_all()
        """
        self.assertSqlListEqual(TagTestCase.expected_tags, Tag.get_all())

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

        expected_tags: list[Tag] = TagTestCase.expected_tags.copy()
        expected_tags.append(Tag(12, "Other", False))

        # Test create new Tag
        tag: Tag = Tag(None, "Other", False)
        tag.sync()

        self.assertSqlListEqual(expected_tags, Tag.get_all())
        self.assertEqual(12, tag.sqlid)

        # Update existing Merchant
        expected_tags[5] = Tag(6, "Christmas Gifts", True)

        tag = Tag.from_id(6)
        tag.name = "Christmas Gifts"
        tag.occasional = True

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
        tag: Tag = Tag(None, None, None)

        # Try to sync without required fields
        self.assertEqual(
            ["name cannot be None.", "occasional cannot be None."], tag.syncable()
        )

        with self.assertRaises(RuntimeError) as msg:
            tag.sync()
        self.assertEqual("name cannot be None.", str(msg.exception))
        self.assertSqlListEqual(TagTestCase.expected_tags, Tag.get_all())

        # Try to sync with required fields
        tag = Tag(name="Gaming", occasional=False)

        self.assertIsNone(tag.syncable())

        tag.sync()
        self.assertSqlListEqual(TagTestCase.expected_tags + [tag], Tag.get_all())

    def test_get_all(self):
        """
        Tests Tag.get_all()

        Prerequisite: None
        """

        actual_tags: list[Tag] = Tag.get_all()

        self.assertEqual(len(TagTestCase.expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(TagTestCase.expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

    def test_default_merchants(self):
        """
        Tests Tag.default_merchants()

        Prerequisite: test_from_id
        """

        # Test with Personal
        expected_merchants: list[Merchant] = [
            Merchant(4, "Apple", False, None),
            Merchant(8, "Bambu Labs", True, None),
            Merchant(9, "Etsy", True, None),
        ]

        actual_merchants: list[Merchant] = Tag.from_id(10).default_merchants()

        self.assertEqual(len(expected_merchants), len(actual_merchants))
        for expected_merchant, actual_merchant in zip(
            expected_merchants, actual_merchants
        ):
            self.assertEqual(expected_merchant.sqlid, actual_merchant.sqlid)
            self.assertEqual(expected_merchant, actual_merchant)

        # Test with Eating Out
        expected_merchants = [
            Merchant(1, "Penn Station", False, None),
            Merchant(2, "Outback Steak House", False, None),
        ]

        actual_merchants = Tag.from_id(7).default_merchants()

        self.assertEqual(len(expected_merchants), len(actual_merchants))
        for expected_merchant, actual_merchant in zip(
            expected_merchants, actual_merchants
        ):
            self.assertEqual(expected_merchant.sqlid, actual_merchant.sqlid)
            self.assertEqual(expected_merchant, actual_merchant)

        # Test with Coffee
        expected_merchants = [
            Merchant(5, "Port City Java", False, None),
        ]

        actual_merchants = Tag.from_id(11).default_merchants()

        self.assertEqual(len(expected_merchants), len(actual_merchants))
        for expected_merchant, actual_merchant in zip(
            expected_merchants, actual_merchants
        ):
            self.assertEqual(expected_merchant.sqlid, actual_merchant.sqlid)
            self.assertEqual(expected_merchant, actual_merchant)

        # Test with new Tag
        self.assertEqual([], Tag().default_merchants())

    def test_amounts(self):
        """
        Tests Tag.amounts()

        Prerequisite: test_from_id()
        """

        # Test with Anarack
        expected_amounts: list[Amount] = [Amount(4, 34.82, 4, "PC Parts")]

        actual_amounts: list[Amount] = Tag.from_id(3).amounts()
        self.assertSqlListEqual(expected_amounts, actual_amounts)

        # Test with Personal
        expected_amounts: list[Amount] = [
            Amount(2, 1245.34, 2, None),
            Amount(3, 12.98, 3, None),
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
        ]

        self.assertSqlListEqual(expected_transactions, Tag.from_id(10).transactions())

        # Test with tag 4
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
        ]

        self.assertSqlListEqual(expected_transactions, Tag.from_id(4).transactions())

        # Test with tag 5
        expected_transactions = [
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
        ]

        self.assertSqlListEqual(expected_transactions, Tag.from_id(5).transactions())

        # Test with new tag
        self.assertEqual([], Tag().transactions())
