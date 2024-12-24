"""
Contains the LocationPopup class which allows the user to create or edit a location.
"""

from __future__ import annotations

import re
from typing import Optional, cast, Any

from PySimpleGUI import Element, Text, Input, Combo  # type: ignore

from src.model.location import Location
from src.model.merchant import Merchant
from src.view.data_popup import DataPopup
from src.view.validated_input import ValidatedInput, CoordinateInput
from src.view.searchable_combo import SearchableCombo


class LocationPopup(DataPopup):
    """
    Popup that allows the user to create or edit a location.
    """

    LOCATION_ID_TEXT_KEY: str = "-LOCATION ID TEXT-"
    DESCRIPTION_INPUT_KEY: str = "-DESCRIPTION INPUT-"
    MERCHANT_COMBO_KEY: str = "-MERCHANT COMBO-"
    COORD_INPUT_KEY: str = "-COORDINATE INPUT-"

    def __init__(self, location: Optional[Location]) -> None:
        self.location: Location
        """Location that this popup interacts with."""
        if location is not None:
            self.location = location
        else:
            self.location = Location()
        super().__init__(
            f"Location ID = {"New" if self.location.sqlid is None else self.location.sqlid}"
        )

        self.window.read(timeout=0)

        self.merchant: Optional[Merchant] = self.location.merchant()
        """Internal Merchant object updated by the merchant combo element."""

        self.validated_input_keys: list[str] = [
            LocationPopup.COORD_INPUT_KEY,
        ]
        """
        Input widgets that extend ValidatedInput. Their validation functions must be called each 
        event loop.
        """

        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            self.add_callback(validated_input.update_validation_appearance)
        self.add_callback(
            cast(
                SearchableCombo, self.window[LocationPopup.MERCHANT_COMBO_KEY]
            ).event_loop_callback
        )

        self.window[LocationPopup.DONE_BUTTON_KEY].update(
            disabled=not self.inputs_valid()
        )

    def _fields_generator(self) -> list[list[Element]]:
        labels: list[Element] = [
            Text(str_label, size=(15, None))
            for str_label in [
                "Location ID:",
                "Description",
                "Merchant",
                "Latitude",
                "Longitude",
            ]
        ]

        fields: list[Element] = [
            Text(self.location.sqlid, key=LocationPopup.LOCATION_ID_TEXT_KEY),
            Input(
                default_text=(
                    ""
                    if self.location.description is None
                    else self.location.description
                ),
                key=LocationPopup.DESCRIPTION_INPUT_KEY,
                enable_events=True,
            ),
            SearchableCombo(
                values=Merchant.get_all(),
                default_value=self.location.merchant(),
                key=LocationPopup.MERCHANT_COMBO_KEY,
            ),
            CoordinateInput(
                default_text=f"{self.location.lat}, {self.location.long}",
                key=LocationPopup.COORD_INPUT_KEY,
                allow_no_input=False,
            ),
        ]

        return [list(row) for row in zip(labels, fields)]

    def check_event(self, event: Any, values: dict) -> None:
        """
        Responds to events from the user.

        :param event: Event to parse
        :param values: Values related to the event
        """
        super().check_event(event, values)

        if event == LocationPopup.CREATE_BUTTON_KEY:
            self.run_event_loop = False
            self.window.close()
            LocationPopup(None).event_loop()
            return

        if event is not None and LocationPopup.MERCHANT_COMBO_KEY in event:
            self.merchant = cast(
                SearchableCombo, self.window[LocationPopup.MERCHANT_COMBO_KEY]
            ).selected_value

        if event == LocationPopup.DONE_BUTTON_KEY:

            if not self.inputs_valid():
                raise RuntimeError("Cannot submit location while inputs are not valid.")

            # Update Location fields
            self.location.description = (
                None
                if self.window[LocationPopup.DESCRIPTION_INPUT_KEY].get() == ""
                else self.window[LocationPopup.DESCRIPTION_INPUT_KEY].get()
            )
            self.location.merchant_id = (
                None if self.merchant is None else self.merchant.sqlid
            )

            single_coordinate_pattern: str = r"-?\d{1,}\.?\d*"
            coords: list[str] = re.findall(
                single_coordinate_pattern,
                self.window[LocationPopup.COORD_INPUT_KEY].get(),
            )
            if len(coords) == 2:
                self.location.lat = float(coords[0])
                self.location.long = float(coords[1])

            # Sync Location
            self.location.sync()

            self.run_event_loop = False

        # Update done button to be enabled/disabled based on input validity
        self.window[LocationPopup.DONE_BUTTON_KEY].update(
            disabled=not self.inputs_valid()
        )

    def inputs_valid(self) -> bool:
        """
        Checks if all inputs are valid.

        :return: True if all inputs are valid, false otherwise
        """
        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            if validated_input.validation_status() is not None:
                return False

        return True
