import os
import shutil
from unittest import TestCase

from model import database
from model.Location import Location
from test_model import sample_database_1, test_database


class TestLocation(TestCase):

    expected_locations: list[Location] = [
        Location(1, "Falls of Neuse", 1, 35.86837825457926, -78.62150981593383),
        Location(2, "Capital", 2, 35.85665622223983, -78.58032796673776),
        Location(3, "Crabtree Mall", 4, 35.8408590921226, -78.68011850195218),
        Location(4, "EB2", 5, 35.77184197261896, -78.67356047898443),
        Location(5, "Park Shops", 5, 35.78546665319359, -78.66708463594044),
        Location(6, "Talley", 5, 35.78392567533286, -78.67092696947988),
        Location(7, "Walnut", 6, 35.753166119681715, -78.74569648479638),
        Location(8, "Falls River", 7, 35.906477682429525, -78.59029227485301),
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
            Location.from_id(9)
        self.assertEqual("No location with id = 9.", str(msg.exception))

    def test_sync(self):
        """
        Tests Location.sync()

        Prerequisite: test_get_all() and from_id(sqlid: int)
        """

        expected_locations: list[Location] = TestLocation.expected_locations.copy()
        expected_locations.append(
            Location(9, "Nelson Hall", 5, 35.78828200046954, -78.67396105203677)
        )

        # Test create new Location
        location: Location = Location(
            None, "Nelson Hall", 5, 35.78828200046954, -78.67396105203677
        )
        location.sync()

        actual_locations: list[Location] = Location.get_all()
        self.assertEqual(len(expected_locations), len(actual_locations))
        for expected_location, actual_location in zip(
            expected_locations, actual_locations
        ):
            self.assertEqual(expected_location.sqlid, actual_location.sqlid)
            self.assertEqual(expected_location, actual_location)

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

        actual_locations: list[Location] = Location.get_all()
        self.assertEqual(len(expected_locations), len(actual_locations))
        for expected_location, actual_location in zip(
            expected_locations, actual_locations
        ):
            self.assertEqual(expected_location.sqlid, actual_location.sqlid)
            self.assertEqual(expected_location, actual_location)

    def test_get_all(self):
        """
        Test Merchant.get_all().

        Prerequisite: None
        """

        actual_locations: list[Location] = Location.get_all()

        self.assertEqual(len(TestLocation.expected_locations), len(actual_locations))
        for expected_location, actual_location in zip(
            TestLocation.expected_locations, actual_locations
        ):
            self.assertEqual(expected_location.sqlid, actual_location.sqlid)
            self.assertEqual(expected_location, actual_location)
