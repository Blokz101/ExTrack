import os
import shutil

from model.Location import Location
from tests.test_model import test_database, sample_database_1
from unittest import TestCase

from src.model import database
from src.model.Merchant import Merchant


class TestMerchant(TestCase):

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

        Prerequisite: test_get_all() and from_id(sqlid: int)
        """

        expected_merchants: list[Merchant] = TestMerchant.expected_merchants.copy()
        expected_merchants.append(Merchant(10, "Wolf Pack Outfitters", False, None))

        # Test create new Merchant
        merchant: Merchant = Merchant(None, "Wolf Pack Outfitters", False, None)
        merchant.sync()

        actual_merchants: list[Merchant] = Merchant.get_all()
        self.assertEqual(len(expected_merchants), len(actual_merchants))
        for expected_merchant, actual_merchant in zip(
            expected_merchants, actual_merchants
        ):
            self.assertEqual(expected_merchant.sqlid, actual_merchant.sqlid)
            self.assertEqual(expected_merchant, actual_merchant)

        # Update existing merchant
        expected_merchants[3] = Merchant(4, "Apple Online Store", True, "Apple")

        merchant = Merchant.from_id(4)
        merchant.name = "Apple Online Store"
        merchant.online = True
        merchant.rule = "Apple"

        merchant.sync()

        actual_merchants: list[Merchant] = Merchant.get_all()
        self.assertEqual(len(expected_merchants), len(actual_merchants))
        for expected_merchant, actual_merchant in zip(
            expected_merchants, actual_merchants
        ):
            self.assertEqual(expected_merchant.sqlid, actual_merchant.sqlid)
            self.assertEqual(expected_merchant, actual_merchant)

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

    # def test_transactions(self):
    #
    #     self.fail()
    #
    def test_locations(self):
        """
        Tests Merchant.locations().

        Prerequisite: test_from_id(sqlid: int) and TestLocation.test_get_all()
        """

        expected_locations: list[Location] = [
            Location(4, "EB2", 5, 35.77184197261896, -78.67356047898443),
            Location(5, "Park Shops", 5, 35.78546665319359, -78.66708463594044),
            Location(6, "Talley", 5, 35.78392567533286, -78.67092696947988),
        ]

        self.assertEqual(expected_locations, Merchant.from_id(5).locations())

    #
    # def test_default_tags(self):
    #
    #     self.fail()
