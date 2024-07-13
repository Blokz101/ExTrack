"""
Contains the AccountPopup class which allows the user to create or edit an account.
"""

from __future__ import annotations

from typing import Optional, cast, Any

from PySimpleGUI import Element, Text  # type: ignore

from src.model.account import Account
from src.view.data_popup import DataPopup
from src.view.validated_input import ValidatedInput, NonNoneInput, PositiveIntInput


class AccountPopup(DataPopup):
    """
    Popup that allows the user to create or edit an account.
    """

    ACCOUNT_ID_TEXT_KEY: str = "-ACCOUNT ID TEXT-"
    NAME_INPUT_KEY: str = "-NAME INPUT-"
    AMOUNT_IDX_INPUT_KEY: str = "-AMOUNT IDX INPUT-"
    DESCRIPTION_IDX_INPUT_KEY: str = "-DESCRIPTION IDX INPUT-"
    DATE_IDX_INPUT_KEY: str = "-DATE IDX INPUT-"

    def __init__(self, account: Optional[Account]) -> None:
        self.account: Account
        """Account that this popup interacts with."""
        if account is not None:
            self.account = account
        else:
            self.account = Account()
        super().__init__(
            f"Account ID = {"New" if self.account.sqlid is None else self.account.sqlid}"
        )

        self.window.read(timeout=0)

        self.validated_input_keys: list[str] = [
            AccountPopup.NAME_INPUT_KEY,
            AccountPopup.AMOUNT_IDX_INPUT_KEY,
            AccountPopup.DESCRIPTION_IDX_INPUT_KEY,
            AccountPopup.DATE_IDX_INPUT_KEY,
        ]
        """
        Input widgets that extend ValidatedInput. Their validation functions must be called each 
        event loop.
        """

        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            self.add_callback(validated_input.update_validation_appearance)

        self.window[AccountPopup.DONE_BUTTON_KEY].update(
            disabled=not self.inputs_valid()
        )

    def _fields_generator(self) -> list[list[Element]]:
        labels: list[Element] = [
            Text(str_label, size=(15, None))
            for str_label in [
                "Account ID:",
                "Name",
                "Amount Idx",
                "Description Idx",
                "Date Idx",
            ]
        ]

        fields: list[Element] = [
            Text(self.account.sqlid, key=AccountPopup.ACCOUNT_ID_TEXT_KEY),
            NonNoneInput(
                default_text="" if self.account.name is None else self.account.name,
                key=AccountPopup.NAME_INPUT_KEY,
                enable_events=True,
            ),
            PositiveIntInput(
                default_text=(
                    ""
                    if self.account.amount_idx is None
                    else str(self.account.amount_idx)
                ),
                key=AccountPopup.AMOUNT_IDX_INPUT_KEY,
                enable_events=True,
            ),
            PositiveIntInput(
                default_text=(
                    str(self.account.description_idx)
                    if self.account.description_idx is not None
                    else ""
                ),
                key=AccountPopup.DESCRIPTION_IDX_INPUT_KEY,
                enable_events=True,
            ),
            PositiveIntInput(
                default_text=(
                    str(self.account.date_idx)
                    if self.account.date_idx is not None
                    else ""
                ),
                key=AccountPopup.DATE_IDX_INPUT_KEY,
                enable_events=True,
            ),
        ]

        return [list(row) for row in zip(labels, fields)]

    def check_event(self, event: Any, values: dict[str, Any]) -> None:
        """
        Respond to events from the user.

        :param event: Event to parse
        :param values: Values related to the event
        """
        super().check_event(event, values)

        if event == AccountPopup.CREATE_BUTTON_KEY:
            self.run_event_loop = False
            self.window.close()
            AccountPopup(None).event_loop()
            return

        if event == AccountPopup.DONE_BUTTON_KEY:

            if not self.inputs_valid():
                raise RuntimeError("Cannot submit account while inputs are not valid.")

            # Update Account fields
            self.account.name = (
                None
                if self.window[AccountPopup.NAME_INPUT_KEY].get() == ""
                else self.window[AccountPopup.NAME_INPUT_KEY].get()
            )
            self.account.amount_idx = (
                None
                if self.window[AccountPopup.AMOUNT_IDX_INPUT_KEY].get() == ""
                else int(self.window[AccountPopup.AMOUNT_IDX_INPUT_KEY].get())
            )
            self.account.description_idx = (
                None
                if self.window[AccountPopup.DESCRIPTION_IDX_INPUT_KEY].get() == ""
                else int(self.window[AccountPopup.DESCRIPTION_IDX_INPUT_KEY].get())
            )
            self.account.date_idx = (
                None
                if self.window[AccountPopup.DATE_IDX_INPUT_KEY].get() == ""
                else int(self.window[AccountPopup.DATE_IDX_INPUT_KEY].get())
            )

            # Sync Account
            self.account.sync()

            self.run_event_loop = False

        # Update done button to be enabled/disabled based on input validity
        self.window[AccountPopup.DONE_BUTTON_KEY].update(
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
