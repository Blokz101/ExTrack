"""
Tests the Merchant class.
"""

# mypy: ignore-errors

from src.model.location import Location
from src.model.merchant import Merchant
from src.model.tag import Tag
from src.model.transaction import Transaction
from tests.test_model.sample_1_test_case import (
    Sample1TestCase,
    EXPECTED_MERCHANTS,
    EXPECTED_TRANSACTIONS,
    EXPECTED_LOCATIONS,
    EXPECTED_TAGS,
)


class TestMerchant(Sample1TestCase):
    """
    Tests the Merchant class.
    """

    def test_from_id(self):
        """
        Tests Merchant.from_id(sqlid: int)

        Prerequisite: test_get_all()
        """

        # Test valid merchants
        expected_merchants: list[Merchant] = Merchant.get_all()

        for expected_merchant in expected_merchants:
            self.assertEqual(
                expected_merchant, Merchant.from_id(expected_merchant.sqlid)
            )

        # Test invalid merchant
        with self.assertRaises(ValueError) as msg:
            Merchant.from_id(-1)
        self.assertEqual("No merchant with id = -1.", str(msg.exception))

        with self.assertRaises(ValueError) as msg:
            Merchant.from_id(28)
        self.assertEqual("No merchant with id = 28.", str(msg.exception))

    def test_sync(self):
        """
        Tests Merchant.sync().

        Prerequisite: test_get_all() and test_from_id()
        """
        # Test create new Merchant
        expected_merchants: list[Merchant] = EXPECTED_MERCHANTS.copy()
        expected_merchants.append(
            Merchant(28, "Wolf Pack Outfitters", False, "wolfPACK")
        )

        merchant: Merchant = Merchant(None, "Wolf Pack Outfitters", False, "wolfPACK")
        merchant.sync()

        self.assertSqlListEqual(expected_merchants, Merchant.get_all())
        self.assertEqual(28, merchant.sqlid)

        # Update existing Merchant
        expected_merchants[3] = Merchant(4, "Apple Online Store", True, "Apple")

        merchant = Merchant.from_id(4)
        merchant.name = "Apple Online Store"
        merchant.online = True
        merchant.rule = "Apple"

        merchant.sync()

        self.assertSqlListEqual(expected_merchants, Merchant.get_all())
        self.assertEqual(4, merchant.sqlid)

        # Test with "" text fields
        merchant = Merchant.from_id(6)
        merchant.name = ""
        with self.assertRaises(RuntimeError):
            merchant.sync()

        merchant = Merchant.from_id(3)
        merchant.rule = ""
        merchant.sync()

        self.assertIsNone(Merchant.from_id(3).rule)

    def test_syncable(self):
        """
        Tests Merchant.syncable() and Merchant.sync()

        Prerequisite: test_get_all() and test_sync()
        """
        merchant: Merchant = Merchant(None, None, None, "new")

        # Try to sync without required fields
        self.assertEqual(
            ["name cannot be None.", "online cannot be None."], merchant.syncable()
        )

        with self.assertRaises(RuntimeError) as msg:
            merchant.sync()
        self.assertEqual("name cannot be None.", str(msg.exception))
        self.assertSqlListEqual(EXPECTED_MERCHANTS, Merchant.get_all())

        # Try to sync with required fields
        merchant = Merchant(name="Smash Burger", online=False)

        self.assertIsNone(merchant.syncable())

        merchant.sync()
        self.assertSqlListEqual(EXPECTED_MERCHANTS + [merchant], Merchant.get_all())

    def test_get_all(self):
        """
        Test Merchant.get_all().

        Prerequisite: None
        """

        actual_merchants: list[Merchant] = Merchant.get_all()

        self.assertSqlListEqual(EXPECTED_MERCHANTS, actual_merchants)

    def test_transactions(self):
        """
        Tests Merchant.transactions()

        Prerequisite: test_from_id()
        """

        expected_transactions: list[Transaction] = [EXPECTED_TRANSACTIONS[4 - 1]]

        self.assertSqlListEqual(
            expected_transactions, Merchant.from_id(3).transactions()
        )

        # Test with new merchant
        self.assertEqual([], Merchant().transactions())

    def test_locations(self):
        """
        Tests Merchant.locations().

        Prerequisite: test_from_id()
        """

        expected_locations: list[Location] = [
            EXPECTED_LOCATIONS[4 - 1],
            EXPECTED_LOCATIONS[5 - 1],
            EXPECTED_LOCATIONS[6 - 1],
        ]

        actual_locations: list[Location] = Merchant.from_id(5).locations()

        self.assertSqlListEqual(expected_locations, actual_locations)

        # Test with new merchant
        self.assertEqual([], Merchant().locations())

    def test_default_tags(self):
        """
        Tests Tag.default_tags()

        Prerequisite: test_from_id()
        """

        # Test with Penn Station
        expected_tags: list[Tag] = [
            EXPECTED_TAGS[5 - 1],
            EXPECTED_TAGS[7 - 1],
        ]
        actual_tags: list[Tag] = Merchant.from_id(1).default_tags()

        self.assertSqlListEqual(expected_tags, actual_tags)

        # Test with BJS
        expected_tags = [Tag(1, "Groceries", False, "groc")]
        actual_tags = Merchant.from_id(6).default_tags()

        self.assertSqlListEqual(expected_tags, actual_tags)

        # Test with new merchant
        self.assertEqual([], Merchant().default_tags())

    def test_add_remove_default_tags(self):
        """
        Tests Tag.add_default_tags() and Tag.remove_default_tags()

        Prerequisite: test_get_all() and test_from_id()
        """

        expected_tags: list[Tag]

        # Test with penn station
        penn_station: Merchant = Merchant.from_id(1)

        expected_tags = [Tag.from_id(5), Tag.from_id(7)]
        self.assertSqlListEqual(expected_tags, penn_station.default_tags())

        # Remove valid tags
        penn_station.remove_default_tag(5)
        penn_station.remove_default_tag(7)

        expected_tags = []
        self.assertSqlListEqual(expected_tags, penn_station.default_tags())

        # Remove invalid tags
        with self.assertRaises(KeyError) as msg:
            penn_station.remove_default_tag(5)
        self.assertEqual(
            "Merchant 'Penn Station' does not have a default tag 'Dating'.",
            str(msg.exception)[1:-1],
        )

        with self.assertRaises(KeyError) as msg:
            penn_station.remove_default_tag(1)
        self.assertEqual(
            "Merchant 'Penn Station' does not have a default tag 'Groceries'.",
            str(msg.exception)[1:-1],
        )

        # Add valid tags
        penn_station.add_default_tag(Tag.from_id(5))
        penn_station.add_default_tag(Tag.from_id(7))

        expected_tags = [Tag.from_id(5), Tag.from_id(7)]
        self.assertSqlListEqual(expected_tags, penn_station.default_tags())

        # Add duplicate tags
        with self.assertRaises(ValueError) as msg:
            penn_station.add_default_tag(Tag.from_id(5))
        self.assertEqual(
            "Cannot add duplicate default tag 'Dating'.", str(msg.exception)
        )

        with self.assertRaises(ValueError) as msg:
            penn_station.add_default_tag(Tag.from_id(7))
        self.assertEqual(
            "Cannot add duplicate default tag 'Eating Out'.", str(msg.exception)
        )

    def test_set_default_tags(self):
        """
        Tests Merchant.set_default_tags(tag_id_list: list[int])

        Prerequisites: test_default_tags and test_from_id and test_Tag.from_id
        """
        merchant: Merchant
        expected_tags: list[Tag]

        # Test with Penn Station and adding and removing tags
        merchant = Merchant.from_id(1)
        expected_tags = [Tag.from_id(1), Tag.from_id(10), Tag.from_id(7)]
        merchant.set_default_tags(list(tag.sqlid for tag in expected_tags))

        self.assertSqlListEqual(
            expected_tags, merchant.from_id(1).default_tags(), strict_order=False
        )

        # Test with BJS and adding tags
        merchant = Merchant.from_id(6)
        expected_tags = [Tag.from_id(1), Tag.from_id(5), Tag.from_id(10)]
        merchant.set_default_tags(list(tag.sqlid for tag in expected_tags))

        self.assertSqlListEqual(
            expected_tags, merchant.from_id(6).default_tags(), strict_order=False
        )

        # Test with Apple and removing tags
        merchant = Merchant.from_id(4)
        expected_tags = []
        merchant.set_default_tags(list(tag.sqlid for tag in expected_tags))

        self.assertSqlListEqual(
            expected_tags, merchant.from_id(4).default_tags(), strict_order=False
        )

        # Test with new Merchant
        with self.assertRaises(RuntimeError) as msg:
            Merchant().set_default_tags([3, 5])
        self.assertEqual(
            "Cannot set default tags of a merchant that does not exist in the database.",
            str(msg.exception),
        )
