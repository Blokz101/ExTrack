import re

from PySimpleGUI import *

from datetime import datetime

from src.model.Tag import Tag
from src.view.DataPopup import DataPopup
from src.view.ValidatedInput import (
    ValidatedInput,
    CoordinateInput,
    DateInput,
    AmountInput,
)
from src.view import full_date_format, short_date_format
from src.view.TagSelector import TagSelector
from src.model.Transaction import Transaction
from src.model.Account import Account
from src.model.Merchant import Merchant
from typing import cast


class Transaction_Popup(DataPopup):

    def __init__(self, sqlid: int):
        self.trans: Transaction = Transaction.from_id(sqlid)
        """Transaction that this popup interacts with."""

        self.selected_tags: list[Tag] = self.trans.tags()
        """Tags the user has selected but have not been synced to the transaction yet."""

        self.validated_input_keys: list[str] = [
            "-DATE INPUT-",
            "-COORDINATE INPUT-",
            "-TOTAL AMOUNT INPUT-",
        ]

        super().__init__(
            f"Transaction ID = {sqlid}",
            [
                "-ACCOUNT SELECTOR-",
                "-DESCRIPTION INPUT-",
                "-MERCHANT SELECTOR-",
                "-COORD INPUT-",
                "-DATE INPUT-",
                "-AMOUNT TAG SELECTOR-",
            ],
        )

    def _fields_generator(self) -> list[list[Element]]:
        labels: list[Element] = list(
            Text(str_label, size=(15, None))
            for str_label in [
                "Transaction ID: ",
                "Account: ",
                "Description: ",
                "Total Amount: ",
                "Merchant: ",
                "Coordinates: ",
                "Date: ",
                "Reconciled: ",
                "Statement: ",
                "Transfer Transaction: ",
                "Amount 1 Tags: ",
            ]
        )

        fields: list[Element] = [
            Text(self.trans.sqlid),
            Combo(
                Account.get_all(),
                default_value=self.trans.account(),
                key="-ACCOUNT SELECTOR-",
                enable_events=True,
                expand_x=True,
            ),
            Input(
                default_text=self.trans.description,
                key="-DESCRIPTION INPUT-",
                expand_x=True,
            ),
            AmountInput(
                default_text=self.trans.total_amount(),
                key="-TOTAL AMOUNT INPUT-",
                enable_events=True,
            ),
            Combo(
                Merchant.get_all(),
                default_value=(
                    self.trans.merchant().name
                    if self.trans.merchant_id is not None
                    else "None"
                ),
                key="-MERCHANT SELECTOR-",
                enable_events=True,
                expand_x=True,
            ),
            CoordinateInput(
                default_text=f"{self.trans.lat}, {self.trans.long}",
                key="-COORDINATE INPUT-",
                enable_events=True,
                expand_x=True,
            ),
            DateInput(
                default_text=(
                    self.trans.date.strftime(full_date_format)
                    if self.trans.date is not None
                    else "None"
                ),
                key="-DATE INPUT-",
                enable_events=True,
                expand_x=True,
            ),
            Text(self.trans.reconciled),
            Text(
                (
                    self.trans.statement().date
                    if self.trans.statement_id is not None
                    else "None"
                ),
                expand_x=True,
            ),
            Text(
                (
                    self.trans.transfer_trans().description
                    if self.trans.transfer_trans_id is not None
                    else "None"
                ),
                expand_x=True,
            ),
            Button(
                ", ".join(tag.name for tag in self.trans.amounts()[0].tags()),
                key=("-AMOUNT TAG SELECTOR-", self.trans.sqlid, 0),
                expand_x=True,
            ),
        ]

        return zip(labels, fields)

    def check_event(self, event: any, values: dict) -> None:
        super().check_event(event, values)

        for key in self.validated_input_keys:
            if event == key:
                validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
                validated_input.update_validation_appearance()

        if event == "-ACCOUNT SELECTOR-":
            self.trans.account_id = values["-ACCOUNT SELECTOR-"].sqlid

        if event == ("-AMOUNT TAG SELECTOR-", self.trans.sqlid, 0):
            tag_selector: TagSelector = TagSelector(selected_tags=self.selected_tags)
            tag_selector.event_loop()
            self.window[("-AMOUNT TAG SELECTOR-", self.trans.sqlid, 0)].update(
                text=", ".join(tag.name for tag in tag_selector.selected_tags)
            )

        if event == "-DESCRIPTION INPUT-":
            self.trans.description = values["-DESCRIPTION INPUT-"]

        if event == "-MERCHANT SELECTOR-":
            self.trans.merchant_id = values["-MERCHANT SELECTOR-"].sqlid

        if event == "-COORDINATE INPUT-":
            single_coordinate_pattern: str = r"-?\d{1,}\.?\d*"
            coords: list[str] = re.findall(
                single_coordinate_pattern, values["-COORDINATE INPUT-"]
            )
            self.trans.lat = float(coords[0])
            self.trans.long = float(coords[1])

        if event == "-DATE INPUT-":
            date: Optional[datetime] = None
            try:
                date = datetime.strptime(values["-DATE INPUT-"], full_date_format)
            except ValueError:
                pass

            try:
                date = datetime.strptime(values["-DATE INPUT-"], short_date_format)
            except ValueError:
                pass

            if date is not None:
                self.trans.date = date

        if event == "-DONE BUTTON-":
            self.trans.sync()
            self.run_event_loop = False

    def inputs_valid(self) -> bool:
        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            if validated_input.validation_status() is not None:
                return False

        return True
