"""
Tests for the LocationPopup class.
"""

# mypy: ignore-errors
from PySimpleGUI import Window
from ddt import ddt, data
from typing import cast

from src.model.location import Location
from src.model.merchant import Merchant
from src.view.location_popup import LocationPopup
from tests.test_model.sample_1_test_case import Sample1TestCase
from src.view.data_popup import DataPopup
from src.view.searchable_combo import SearchableCombo


@ddt
class TestLocationPopup(Sample1TestCase):
    """
    Testes for the LocationPopup class.
    """

    def test_construction_for_new_location(self):
        """
        Tests the constructor for a new location.
        """
        popup: LocationPopup = LocationPopup(None)
        popup_window: Window = popup.window
        _, _ = popup_window.read(timeout=0)

        # Validate basic fields and inputs
        self.assertEqual("", popup_window[LocationPopup.DESCRIPTION_INPUT_KEY].get())
        self.assertIsNone(
            cast(
                SearchableCombo, popup_window[LocationPopup.MERCHANT_COMBO_KEY]
            ).selected_value
        )
        self.assertEqual(
            "None, None", popup_window[LocationPopup.COORD_INPUT_KEY].get()
        )

        self.assertFalse(popup.inputs_valid())

        # Validate disabled delete
        self.assertEqual(
            "disabled", popup_window[DataPopup.DELETE_BUTTON_KEY].Widget["state"].string
        )

        popup_window.close()

    @data(1, 2, 3, 4, 5, 6, 7, 8)
    def test_construction_with_existing_location(self, location_id: int):
        """
        Tests the construction of a location popup from an existing location.
        """
        popup: LocationPopup = LocationPopup(Location.from_id(location_id))
        popup_window: Window = popup.window
        _, _ = popup.window.read(timeout=0)

        # Validate basic inputs
        location: Location = Location.from_id(location_id)
        self.assertEqual(
            location.description,
            popup_window[LocationPopup.DESCRIPTION_INPUT_KEY].get(),
        )
        self.assertSqlEqual(
            location.merchant(),
            cast(
                SearchableCombo, popup_window[LocationPopup.MERCHANT_COMBO_KEY]
            ).selected_value,
        )
        self.assertEqual(
            f"{location.lat}, {location.long}",
            popup_window[LocationPopup.COORD_INPUT_KEY].get(),
        )

        self.assertTrue(popup.inputs_valid())

        popup_window.close()

    @data(1, 2, 3, 4, 5, 6, 7, 8)
    def test_submit_unchanged_location(self, location_id: int):
        """
        Tests submitting a location without changing any fields.
        """
        expected_locations: list[Location] = Location.get_all()

        popup: LocationPopup = LocationPopup(Location.from_id(location_id))
        _, _ = popup.window.read(timeout=0)
        popup.check_event(LocationPopup.DONE_BUTTON_KEY, {})

        self.assertSqlListEqual(expected_locations, Location.get_all())

        popup.window.close()

    def test_close_after_edits(self):
        """
        Test making edits to the location popup then closing it.
        """
        expected_locations: list[Location] = Location.get_all()

        popup: LocationPopup = LocationPopup(Location.from_id(4))

        # Fake user inputs
        new_description: str = "Falls shopping center"
        popup.window[LocationPopup.DESCRIPTION_INPUT_KEY].update(new_description)
        popup.check_event(
            LocationPopup.DESCRIPTION_INPUT_KEY,
            {LocationPopup.DESCRIPTION_INPUT_KEY: new_description},
        )

        new_merchant: Merchant = Merchant.from_id(7)
        popup.window[LocationPopup.MERCHANT_COMBO_KEY].update(new_merchant)
        popup.check_event(
            LocationPopup.MERCHANT_COMBO_KEY,
            {LocationPopup.MERCHANT_COMBO_KEY: new_merchant},
        )

        new_coords: str = "35.87297786212306, -78.62322715316918"
        popup.window[LocationPopup.COORD_INPUT_KEY].update(new_coords)
        popup.check_event(
            LocationPopup.COORD_INPUT_KEY,
            {LocationPopup.COORD_INPUT_KEY: new_coords},
        )

        popup.check_event("Exit", {})

        self.assertSqlListEqual(expected_locations, Location.get_all())

        popup.window.close()

    def test_submit_edited_location(self):
        """
        Tests editing the database with the basic inputs fields.
        """
        expected_locations: list[Location] = Location.get_all()
        expected_locations[3] = Location(
            4, "Falls shopping center", 7, 35.87297786212306, -78.62322715316918
        )

        popup: LocationPopup = LocationPopup(Location.from_id(4))

        # Fake user inputs
        new_description: str = "Falls shopping center"
        popup.window[LocationPopup.DESCRIPTION_INPUT_KEY].update(new_description)
        popup.check_event(
            LocationPopup.DESCRIPTION_INPUT_KEY,
            {LocationPopup.DESCRIPTION_INPUT_KEY: new_description},
        )

        new_merchant: Merchant = Merchant.from_id(7)
        popup.window[LocationPopup.MERCHANT_COMBO_KEY].update(new_merchant)
        cast(SearchableCombo, popup.window[LocationPopup.MERCHANT_COMBO_KEY]).set_value(
            new_merchant
        )
        popup.check_event(LocationPopup.MERCHANT_COMBO_KEY, {})

        new_coords: str = "35.87297786212306, -78.62322715316918"
        popup.window[LocationPopup.COORD_INPUT_KEY].update(new_coords)
        popup.check_event(
            LocationPopup.COORD_INPUT_KEY,
            {LocationPopup.COORD_INPUT_KEY: new_coords},
        )

        popup.check_event(LocationPopup.DONE_BUTTON_KEY, {})

        self.assertSqlListEqual(expected_locations, Location.get_all())

        popup.window.close()
