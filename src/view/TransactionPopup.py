from __future__ import annotations
import re
from PySimpleGUI import *
from datetime import datetime

from src.model.Amount import Amount
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


class TransactionPopup(DataPopup):

    def __init__(self, trans: Optional[Transaction]):
        self.trans: Transaction
        """Transaction that this popup interacts with."""
        if trans is not None:
            self.trans = trans
        else:
            self.trans = Transaction(reconciled=False)

        super().__init__(
            f"Transaction ID = {self.trans.sqlid if self.trans.sqlid is not None else 'New'}",
        )

        self.window.read(timeout=0)

        self._next_amount_row_id: int = 0
        self.amount_rows: list[TransactionPopup.AmountRow] = []
        """Amount rows elements that this popup has."""
        if trans is None:
            self._set_amount_rows([])
        else:
            self._set_amount_rows(
                list(
                    TransactionPopup.AmountRow(self, amount)
                    for amount in self.trans.amounts()
                )
            )

        self.account: Optional[Account] = self.trans.account()
        """Internal Account object updated by the account combo element."""

        self.merchant: Optional[Merchant] = self.trans.merchant()
        """Internal Merchant object updated by the merchant combo element."""

        self.validated_input_keys: list[str] = [
            "-DATE INPUT-",
            "-COORDINATE INPUT-",
            "-TOTAL AMOUNT INPUT-",
        ]
        """Input widgets that extend ValidatedInput. Their validation functions must be called each event loop."""

        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            self.add_callback(validated_input.update_validation_appearance)

        self.window["-DONE BUTTON-"].update(disabled=not self.inputs_valid())

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
            ]
        )

        fields: list[Element] = [
            Text(self.trans.sqlid, key="-TRANS ID TEXT-"),
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
                default_text=(
                    "" if self.trans.amounts() == [] else self.trans.total_amount()
                ),
                key="-TOTAL AMOUNT INPUT-",
                enable_events=True,
                expand_x=True,
            ),
            Combo(
                Merchant.get_all(),
                default_value=(
                    ""
                    if self.trans.merchant_id is None
                    else (
                        self.trans.merchant().name
                        if self.trans.merchant_id is not None
                        else "None"
                    )
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
                    datetime.now().strftime(short_date_format)
                    if self.trans.date is None
                    else (
                        self.trans.date.strftime(full_date_format)
                        if self.trans.date is not None
                        else "None"
                    )
                ),
                key="-DATE INPUT-",
                enable_events=True,
                expand_x=True,
            ),
            Text(
                self.trans.reconciled,
                key="-RECONCILED TEXT-",
            ),
            Text(
                (
                    self.trans.statement().date.strftime(short_date_format)
                    if self.trans.statement_id is not None
                    else "None"
                ),
                key="-STATEMENT TEXT-",
                expand_x=True,
            ),
            Text(
                (
                    self.trans.transfer_trans().description
                    if self.trans.transfer_trans_id is not None
                    else "None"
                ),
                key="-TRANSFER TRANSACTION TEXT-",
                expand_x=True,
            ),
        ]

        fields: list[list[Element]] = list(zip(labels, fields))

        amounts_frame: Frame = Frame(
            "Amounts",
            [
                [
                    Button(
                        "Create New Amount ($0.0 left)",
                        key="-NEW AMOUNT BUTTON-",
                        expand_x=True,
                    )
                ],
                [
                    Text(
                        "Description",
                        size=TransactionPopup.AmountRow.DESCRIPTION_INPUT_WIDTH - 3,
                    ),
                    Text(
                        "Amount", size=TransactionPopup.AmountRow.AMOUNT_INPUT_WIDTH - 2
                    ),
                    Text("Tags"),
                ],
            ],
            key="-AMOUNTS FRAME-",
            expand_x=True,
            expand_y=True,
        )

        return fields + [[amounts_frame]]

    def _set_amount_rows(self, new_rows: list[AmountRow]) -> None:
        """
        Sets the amount rows.
        """
        for row in self.amount_rows:
            row.update(visible=False)

        self.amount_rows = new_rows
        for row in self.amount_rows:
            self.window.extend_layout(
                self.window["-AMOUNTS FRAME-"],
                [[pin(row, expand_x=True)]],
            )

    def check_event(self, event: any, values: dict) -> None:
        super().check_event(event, values)

        if event == "-CREATE BUTTON-":
            self.run_event_loop = False
            self.window.close()
            TransactionPopup(None).event_loop()
            return

        if event == "-ACCOUNT SELECTOR-":
            self.account = values["-ACCOUNT SELECTOR-"]

        if event == "-MERCHANT SELECTOR-":
            self.merchant = values["-MERCHANT SELECTOR-"]

        if event == "-DONE BUTTON-":

            if not self.inputs_valid():
                raise RuntimeError(
                    "Cannot submit transaction while inputs are not valid."
                )

            # Update Transaction fields
            self.trans.account_id = None if self.account is None else self.account.sqlid
            self.trans.description = self.window["-DESCRIPTION INPUT-"].get()
            self.trans.merchant_id = (
                None if self.merchant is None else self.merchant.sqlid
            )
            single_coordinate_pattern: str = r"-?\d{1,}\.?\d*"
            coords: list[str] = re.findall(
                single_coordinate_pattern, self.window["-COORDINATE INPUT-"].get()
            )
            if len(coords) == 2:
                self.trans.lat = float(coords[0])
                self.trans.long = float(coords[1])

            user_input_date: str = self.window["-DATE INPUT-"].get()
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
                self.trans.date = date

            # Sync Transaction and Amounts
            self.trans.sync()
            for row in self.amount_rows:
                row.amount.transaction_id = self.trans.sqlid
                row.sync_row()

            self.run_event_loop = False

        if event == "-NEW AMOUNT BUTTON-":
            new_amount_row: TransactionPopup.AmountRow = TransactionPopup.AmountRow(
                self,
                default_amount=(
                    Amount()
                    if self._total_row_amount_difference() is None
                    else Amount(amount=self._total_row_amount_difference())
                ),
            )
            self.amount_rows.append(new_amount_row)
            self.window.extend_layout(
                self.window["-AMOUNTS FRAME-"], [[pin(new_amount_row, expand_x=True)]]
            )

        # Update done button to be enabled/disabled based on input validity
        self.window["-DONE BUTTON-"].update(disabled=not self.inputs_valid())

        # Update create new amount button to show the total amount vs sum of row amounts difference
        if self._total_row_amount_difference() is not None:
            self.window["-NEW AMOUNT BUTTON-"].update(
                text=f"Create New Amount (${self._total_row_amount_difference()} left)"
            )
        else:
            self.window["-NEW AMOUNT BUTTON-"].update(text="Create New Amount")

    def _total_row_amount_difference(self) -> Optional[float]:
        """
        Gets the difference between the total amount and the sum of the amount rows if it exists.

        :return: Difference if it exists or None if it does not
        """
        if self._total_amount() is not None and self._amount_rows_total() is not None:
            return round(self._total_amount() - self._amount_rows_total(), 2)
        else:
            return None

    def _total_amount(self) -> Optional[float]:
        """
        Gets the total amount from the total amount input.

        :return: Total amount from the total amount input or None if total amount is invalid
        """
        return self.window["-TOTAL AMOUNT INPUT-"].get()

    def _amount_rows_total(self) -> Optional[float]:
        """
        Calculates the total amount from all amount rows that have not been deleted.

        :return: Total amount from all amount rows or None if one or more amount rows is invalid
        """
        rows_sum: float = 0
        for row_id in (row.amount_row_id for row in self.amount_rows if row.visible):
            row_amount: Optional[float] = self.window[
                ("-AMOUNT ROW AMOUNT-", row_id)
            ].get()
            if row_amount is None:
                return None
            else:
                rows_sum += row_amount
        return round(rows_sum, 2)

    def inputs_valid(self) -> bool:
        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            if validated_input.validation_status() is not None:
                return False

        if (
            self._total_amount() is None
            or self._amount_rows_total() is None
            or self._total_amount() != self._amount_rows_total()
        ):

            return False

        return True

    class AmountRow(Column):

        DESCRIPTION_INPUT_WIDTH: int = 40
        """Fixed width of the description input widget."""
        AMOUNT_INPUT_WIDTH: int = 15
        """Fixed width of the amount input widget."""

        def __init__(
            self,
            outer: TransactionPopup,
            default_amount: Optional[Amount] = None,
        ) -> None:
            """
            :param outer: Superclass instance
            :param default_amount: Default Amount for this amount row, if None a new Amount will be created
            """

            self.outer: TransactionPopup = outer
            """Instance of outer class."""
            self.amount: Amount = Amount() if not default_amount else default_amount
            """Underlying SqlObject used to communicate with the database."""
            self.amount_row_id: int = self.outer._next_amount_row_id
            """Internal ID of this amount row, used make unique amount rows despite potentially hidden rows."""
            self.outer._next_amount_row_id += 1

            self.tag_list: list[Tag] = self.amount.tags()
            """List of selected tags for this amount."""

            super().__init__(
                [
                    [
                        Input(
                            self.amount.description,
                            key=("-AMOUNT ROW DESCRIPTION-", self.amount_row_id),
                            size=TransactionPopup.AmountRow.DESCRIPTION_INPUT_WIDTH,
                        ),
                        Text(" $", pad=0),
                        AmountInput(
                            default_text=(
                                "" if self.amount.amount is None else self.amount.amount
                            ),
                            key=("-AMOUNT ROW AMOUNT-", self.amount_row_id),
                            size=TransactionPopup.AmountRow.AMOUNT_INPUT_WIDTH,
                            enable_events=True,
                        ),
                        Button(
                            self.tags_as_string(),
                            key=("-AMOUNT ROW TAG SELECTOR-", self.amount_row_id),
                            expand_x=True,
                        ),
                        Button(
                            "DEL",
                            key=("-AMOUNT ROW DELETE-", self.amount_row_id),
                            button_color=("white", "dark red"),
                        ),
                    ]
                ],
                key=("-AMOUNT ROW-", self.amount_row_id),
                expand_x=True,
            )

            self.outer.add_callback(self.event_loop_callback)

        def sync_row(self) -> None:
            """
            Syncs this amount row to the database.
            """
            if self.visible:
                self.amount.description = self.outer.window[
                    ("-AMOUNT ROW DESCRIPTION-", self.amount_row_id)
                ].get()
                self.amount.amount = float(
                    self.outer.window[("-AMOUNT ROW AMOUNT-", self.amount_row_id)].get()
                )

                self.amount.sync()
                self.amount.set_tags(list(tag.sqlid for tag in self.tag_list))
            elif self.amount.exists():
                self.amount.delete()
                del self  # This will cause trouble if the user calls sync on this row again

        def event_loop_callback(self, event: any, _) -> None:
            """
            Should be called each time the event loop runs to update this widget.
            """
            if not self.visible:
                return

            validated_input: ValidatedInput = cast(
                ValidatedInput,
                self.outer.window[("-AMOUNT ROW AMOUNT-", self.amount_row_id)],
            )
            validated_input.update_validation_appearance()

            if event == ("-AMOUNT ROW DELETE-", self.amount_row_id):
                self.update(visible=False)

            if event == ("-AMOUNT ROW TAG SELECTOR-", self.amount_row_id):
                tag_selector: TagSelector = TagSelector(self.tag_list)
                tag_selector.event_loop()
                self.tag_list = tag_selector.selected_tags

            self.outer.window[("-AMOUNT ROW TAG SELECTOR-", self.amount_row_id)].update(
                self.tags_as_string()
            )

        def tags_as_string(self) -> str:
            """
            Formats the tags this amount row has as a single string.

            :return: Tags this amount row has as a single string
            """
            if len(self.tag_list) == 0:
                return "No Tags"
            else:
                return ", ".join(tag.name for tag in self.tag_list)
