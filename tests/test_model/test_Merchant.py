from datetime import datetime

from src.model import date_format
from src.model.Transaction import Transaction
from src.model.Location import Location
from src.model.Tag import Tag
from src.model.Merchant import Merchant
from tests.test_model.Sample1TestCase import Sample1TestCase


class TestMerchant(Sample1TestCase):

    expected_merchants: list[Merchant] = [
        Merchant(1, "Penn Station", False, None),
        Merchant(2, "Outback Steak House", False, None),
        Merchant(3, "Amazon", True, None),
        Merchant(4, "Apple", False, None),
        Merchant(5, "Port City Java", False, None),
        Merchant(6, "BJS", False, None),
        Merchant(7, "Dollar General", False, None),
        Merchant(8, "Bambu Labs", True, None),
        Merchant(9, "Etsy", True, None),
    ]

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
            Merchant.from_id(10)
        self.assertEqual("No merchant with id = 10.", str(msg.exception))

    def test_sync(self):
        """
        Tests Merchant.sync().

        Prerequisite: test_get_all() and test_from_id()
        """

        expected_merchants: list[Merchant] = TestMerchant.expected_merchants.copy()
        expected_merchants.append(Merchant(10, "Wolf Pack Outfitters", False, None))

        # Test create new Merchant
        merchant: Merchant = Merchant(None, "Wolf Pack Outfitters", False, None)
        merchant.sync()

        self.assertSqlListEqual(expected_merchants, Merchant.get_all())
        self.assertEqual(10, merchant.sqlid)

        # Update existing Merchant
        expected_merchants[3] = Merchant(4, "Apple Online Store", True, "Apple")

        merchant = Merchant.from_id(4)
        merchant.name = "Apple Online Store"
        merchant.online = True
        merchant.rule = "Apple"

        merchant.sync()

        self.assertSqlListEqual(expected_merchants, Merchant.get_all())

    def test_syncable(self):
        """
        Tests Merchant.syncable() and Merchant.sync()

        Prerequisite: test_get_all() and test_sync()
        """
        merchant: Merchant = Merchant(None, None, None, None)

        # Try to sync without required fields
        self.assertEqual(
            ["name cannot be None.", "online cannot be None."], merchant.syncable()
        )

        with self.assertRaises(RuntimeError) as msg:
            merchant.sync()
        self.assertEqual("name cannot be None.", str(msg.exception))
        self.assertSqlListEqual(TestMerchant.expected_merchants, Merchant.get_all())

        # Try to sync with required fields
        merchant = Merchant(name="Smash Burger", online=False)

        self.assertIsNone(merchant.syncable())

        merchant.sync()
        self.assertSqlListEqual(
            TestMerchant.expected_merchants + [merchant], Merchant.get_all()
        )

    def test_get_all(self):
        """
        Test Merchant.get_all().

        Prerequisite: None
        """

        actual_merchants: list[Merchant] = Merchant.get_all()

        self.assertEqual(len(TestMerchant.expected_merchants), len(actual_merchants))
        for expected_merchant, actual_merchant in zip(
            TestMerchant.expected_merchants, actual_merchants
        ):
            self.assertEqual(expected_merchant.sqlid, actual_merchant.sqlid)
            self.assertEqual(expected_merchant, actual_merchant)

    def test_transactions(self):
        """
        Tests Merchant.transactions()

        Prerequisite: test_from_id()
        """

        expected_transactions: list[Transaction] = [
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
            Location(4, "EB2", 5, 35.77184197261896, -78.67356047898443),
            Location(5, "Park Shops", 5, 35.78546665319359, -78.66708463594044),
            Location(6, "Talley", 5, 35.78392567533286, -78.67092696947988),
        ]

        actual_locations: list[Location] = Merchant.from_id(5).locations()

        self.assertEqual(len(expected_locations), len(actual_locations))
        for expected_location, actual_location in zip(
            expected_locations, actual_locations
        ):
            self.assertEqual(expected_location.sqlid, actual_location.sqlid)
            self.assertEqual(expected_location, actual_location)

        # Test with new merchant
        self.assertEqual([], Merchant().locations())

    def test_default_tags(self):
        """
        Tests Tag.default_tags()

        Prerequisite: test_from_id()
        """

        # Test with Penn Station
        expected_tags: list[Tag] = [
            Tag(5, "Dating", False),
            Tag(7, "Eating Out", False),
        ]

        actual_tags: list[Tag] = Merchant.from_id(1).default_tags()

        self.assertEqual(len(expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

        # Test with BJS
        expected_tags = [Tag(1, "Groceries", False)]

        actual_tags = Merchant.from_id(6).default_tags()

        self.assertEqual(len(expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

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
