"""
Tests the Location class.
"""

# mypy: ignore-errors
from src.model.location import Location
from tests.test_model.sample_1_test_case import (
    Sample1TestCase,
    EXPECTED_LOCATIONS,
    EXPECTED_MERCHANTS,
)


class TestLocation(Sample1TestCase):
    """
    Tests the Location class.
    """

    def test_from_id(self):
        """
        Tests Location.from_id(sqlid: int)

        Prerequisite: test_get_all()
        """

        # Test valid locations
        expected_locations: list[Location] = Location.get_all()

        for expected_location in expected_locations:
            self.assertEqual(
                expected_location, Location.from_id(expected_location.sqlid)
            )

        # Test invalid location
        with self.assertRaises(ValueError) as msg:
            Location.from_id(-1)
        self.assertEqual("No location with id = -1.", str(msg.exception))

        with self.assertRaises(ValueError) as msg:
            Location.from_id(29)
        self.assertEqual("No location with id = 29.", str(msg.exception))

    def test_sync(self):
        """
        Tests Location.sync()

        Prerequisite: test_get_all() and from_id(sqlid: int)
        """

        expected_locations: list[Location] = EXPECTED_LOCATIONS.copy()
        expected_locations.append(
            Location(29, "Nelson Hall", 5, 35.78828200046954, -78.67396105203677)
        )

        # Test create new Location
        location: Location = Location(
            None, "Nelson Hall", 5, 35.78828200046954, -78.67396105203677
        )
        location.sync()

        self.assertSqlListEqual(expected_locations, Location.get_all())
        self.assertEqual(29, location.sqlid)

        # Update existing location
        expected_locations[1] = Location(
            2, "Biomed Campus", 5, 35.797412141008884, -78.70439800618529
        )

        location = Location.from_id(2)
        location.description = "Biomed Campus"
        location.merchant_id = 5
        location.lat = 35.797412141008884
        location.long = -78.70439800618529

        location.sync()

        self.assertSqlListEqual(expected_locations, Location.get_all())
        self.assertEqual(2, location.sqlid)

        # Test with "" text fields
        location = Location.from_id(6)
        location.description = ""
        location.sync()

        self.assertIsNone(Location.from_id(6).description)

    def test_syncable(self):
        """
        Tests Location.syncable() and Location.sync()

        Prerequisites: test_get_all() and test_sync()
        """
        location: Location = Location(None, "Nelson Hall", None, None, None)

        # Try to sync without required fields
        self.assertEqual(
            [
                "merchant_id cannot be None.",
                "lat cannot be None.",
                "long cannot be None.",
            ],
            location.syncable(),
        )

        with self.assertRaises(RuntimeError) as msg:
            location.sync()
        self.assertEqual("merchant_id cannot be None.", str(msg.exception))
        self.assertSqlListEqual(EXPECTED_LOCATIONS, Location.get_all())

        # Try to sync with required fields
        location = Location(merchant_id=5, lat=10, long=-10)

        self.assertIsNone(location.syncable())

        location.sync()
        self.assertSqlListEqual(EXPECTED_LOCATIONS + [location], Location.get_all())

    def test_get_all(self):
        """
        Test Location.get_all().

        Prerequisite: None
        """

        actual_locations: list[Location] = Location.get_all()

        self.assertSqlListEqual(EXPECTED_LOCATIONS, actual_locations)

    def test_merchant(self):
        """
        Tests Location.merchant()

        Prerequisite: test_from_id()
        """

        self.assertEqual(EXPECTED_MERCHANTS[5 - 1], Location.from_id(5).merchant())

        self.assertEqual(EXPECTED_MERCHANTS[5 - 1], Location.from_id(4).merchant())

        self.assertEqual(EXPECTED_MERCHANTS[4 - 1], Location.from_id(3).merchant())

        # Test with new location
        self.assertEqual(None, Location().merchant())
