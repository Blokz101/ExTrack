"""
Contains the MerchantPopup class which allows the user to create or edit a merchant.
"""

from __future__ import annotations

from typing import Optional, cast

from PySimpleGUI import Element, Text, Input, Checkbox  # type: ignore

from src.model.merchant import Merchant
from src.view.data_popup import DataPopup
from src.view.validated_input import ValidatedInput, NonNoneInput


class MerchantPopup(DataPopup):
    """
    Popup that allows the user to create or edit a merchant.
    """

    MERCHANT_ID_TET_KEY: str = "-MERCHANT ID TEXT-"
    NAME_INPUT_KEY: str = "-NAME INPUT-"
    ONLINE_CHECKBOX_KEY: str = "-ONLINE CHECKBOX-"
    RULE_INPUT_KEY: str = "-RULE INPUT-"

    def __init__(self, merchant: Optional[Merchant] = None) -> None:
        self.merchant: Merchant
        """Merchant that this popup interacts with."""
        if merchant is not None:
            self.merchant = merchant
        else:
            self.merchant = Merchant(online=False)
        super().__init__(
            f"Merchant ID = {self.merchant.sqlid if self.merchant.sqlid is not None else "New"}"
        )

        self.window.read(timeout=0)

        self.validated_input_keys: list[str] = [MerchantPopup.NAME_INPUT_KEY]
        """
        Input widgets that extend ValidatedInput. Their validation functions must be called each 
        event loop.
        """

        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            self.add_callback(validated_input.update_validation_appearance)

        self.window[MerchantPopup.DONE_BUTTON_KEY].update(
            disabled=not self.inputs_valid()
        )

    def _fields_generator(self) -> list[list[Element]]:
        labels: list[Element] = [
            Text(str_label, size=(15, None))
            for str_label in ["Merchant ID:", "Name", "Online", "Rule"]
        ]

        fields: list[Element] = [
            Text(self.merchant.sqlid, key=MerchantPopup.MERCHANT_ID_TET_KEY),
            NonNoneInput(
                default_text=("" if self.merchant.name is None else self.merchant.name),
                key=MerchantPopup.NAME_INPUT_KEY,
                enable_events=True,
            ),
            Checkbox(
                text="",
                default=self.merchant.online,
                key=MerchantPopup.ONLINE_CHECKBOX_KEY,
            ),
            Input(
                default_text=("" if self.merchant.rule is None else self.merchant.rule),
                key=MerchantPopup.RULE_INPUT_KEY,
            ),
        ]

        return [list(row) for row in zip(labels, fields)]

    def check_event(self, event: str, values: dict[str, str]) -> None:
        """
        Responds to events from the user.

        :param event: Event to parse
        :param values: Values related to the event
        """
        super().check_event(event, values)

        if event == MerchantPopup.CREATE_BUTTON_KEY:
            self.run_event_loop = False
            self.window.close()
            MerchantPopup(None).event_loop()
            return

        if event == MerchantPopup.DONE_BUTTON_KEY:

            if not self.inputs_valid():
                raise RuntimeError("Cannot submit merchant while inputs are not valid.")

            # Update Merchant fields
            self.merchant.name = (
                None
                if self.window[MerchantPopup.NAME_INPUT_KEY].get() == ""
                else self.window[MerchantPopup.NAME_INPUT_KEY].get()
            )
            self.merchant.online = self.window[MerchantPopup.ONLINE_CHECKBOX_KEY].get()
            self.merchant.rule = (
                None
                if self.window[MerchantPopup.RULE_INPUT_KEY].get() == ""
                else self.window[MerchantPopup.RULE_INPUT_KEY].get()
            )

            # Sync Merchant
            self.merchant.sync()

            self.run_event_loop = False

        # Update done button to be enabled/disabled based on input validity
        self.window[MerchantPopup.DONE_BUTTON_KEY].update(
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
