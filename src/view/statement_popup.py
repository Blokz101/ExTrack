"""
Contains the statement popup class which allows the user to create or edit a statement.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, cast, Any

from PySimpleGUI import Element, Text, Combo, Checkbox, Input  # type: ignore

from src.model.account import Account
from src.model.statement import Statement
from src.view import short_date_format, full_date_format
from src.view.data_popup import DataPopup
from src.view.validated_input import ValidatedInput, DateInput, AmountInput


class StatementPopup(DataPopup):
    """
    Popup that allows the user to create or edit a statement.
    """

    STATEMENT_ID_TEXT_KEY: str = "-STATEMENT ID TEXT-"
    DATE_INPUT_KEY: str = "-DATE INPUT-"
    ACCOUNT_COMBO_KEY: str = "-ACCOUNT COMBO-"
    STARTING_BALANCE_INPUT_KEY: str = "-STARTING BALANCE INPUT-"
    RECONCILED_CHECKBOX_KEY: str = "-RECONCILED CHECKBOX-"
    FILE_NAME_INPUT_KEY: str = "-FILE NAME INPUT-"

    def __init__(self, statement: Optional[Statement]):
        self.statement: Statement
        """Statement that this popup interacts with."""
        if statement is not None:
            self.statement = statement
        else:
            self.statement = Statement(reconciled=False)

        self.account: Optional[Account] = self.statement.account()
        """Account that this statement belongs to."""

        super().__init__(
            f"Statement ID = {"New" if self.statement.sqlid is None else self.statement.sqlid}"
        )

        self.window.read(timeout=0)

        self.validated_input_keys: list[str] = [
            StatementPopup.DATE_INPUT_KEY,
            StatementPopup.STARTING_BALANCE_INPUT_KEY,
        ]
        """
        Input widgets that extend ValidatedInput. Their validation functions must be called each
        event loop.
        """

        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            self.add_callback(validated_input.update_validation_appearance)

        self.window[StatementPopup.DONE_BUTTON_KEY].update(
            disabled=not self.inputs_valid()
        )

    def _fields_generator(self) -> list[list[Element]]:
        labels: list[Element] = [
            Text(str_label, size=(15, None))
            for str_label in [
                "Statement ID: ",
                "Date",
                "Account",
                "Starting Balance",
                "Reconciled",
                "File Name",
            ]
        ]

        fields: list[Element] = [
            Text(self.statement.sqlid, key=StatementPopup.STATEMENT_ID_TEXT_KEY),
            DateInput(
                default_text=(
                    ""
                    if self.statement.date is None
                    else self.statement.date.strftime(short_date_format)
                ),
                key=StatementPopup.DATE_INPUT_KEY,
            ),
            Combo(
                values=Account.get_all(),
                default_value=(
                    ""
                    if self.statement.account_id is None
                    else self.statement.account().name  # type: ignore
                ),
                key=StatementPopup.ACCOUNT_COMBO_KEY,
                expand_x=True,
                enable_events=True,
            ),
            AmountInput(
                default_text=(
                    ""
                    if self.statement.starting_balance is None
                    else self.statement.starting_balance
                ),
                key=StatementPopup.STARTING_BALANCE_INPUT_KEY,
            ),
            Checkbox(
                text="",
                default=self.statement.reconciled,
                key=StatementPopup.RECONCILED_CHECKBOX_KEY,
            ),
            Input(
                "" if self.statement.file_name is None else self.statement.file_name,
                key=StatementPopup.FILE_NAME_INPUT_KEY,
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

        if event == StatementPopup.CREATE_BUTTON_KEY:
            self.run_event_loop = False
            self.window.close()
            StatementPopup(None).event_loop()
            return

        if event == StatementPopup.ACCOUNT_COMBO_KEY:
            self.account = self.window[StatementPopup.ACCOUNT_COMBO_KEY].get()

        if event == StatementPopup.DONE_BUTTON_KEY:

            if not self.inputs_valid():
                raise RuntimeError(
                    "Cannot submit statement while inputs are not valid."
                )

            # Update Statement fields
            user_input_date: str = self.window[StatementPopup.DATE_INPUT_KEY].get()
            date: Optional[datetime] = None
            try:
                date = datetime.strptime(user_input_date, full_date_format)
            except ValueError:
                pass

            try:
                date = datetime.strptime(user_input_date, short_date_format)
            except ValueError:
                pass

            if date is not None:
                self.statement.date = date

            self.statement.account_id = (
                None if self.account is None else self.account.sqlid
            )
            self.statement.starting_balance = float(
                self.window[StatementPopup.STARTING_BALANCE_INPUT_KEY].get()
            )
            self.statement.reconciled = self.window[
                StatementPopup.RECONCILED_CHECKBOX_KEY
            ].get()
            self.statement.file_name = (
                None
                if self.window[StatementPopup.FILE_NAME_INPUT_KEY].get() == ""
                else self.window[StatementPopup.FILE_NAME_INPUT_KEY].get()
            )

            # Sync Statement
            self.statement.sync()

            self.run_event_loop = False

        # Update done button to be enabled/disabled based on input validity
        self.window[StatementPopup.DONE_BUTTON_KEY].update(
            disabled=not self.inputs_valid()
        )

    def inputs_valid(self) -> bool:
        """
        Checks if the user input is valid.

        :return: True if the user input is valid
        """
        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            if validated_input.validation_status() is not None:
                return False

        return True
