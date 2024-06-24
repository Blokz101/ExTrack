from __future__ import annotations
import re
from PySimpleGUI import *
from datetime import datetime
from src.view import gui_theme
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

    def __init__(self, sqlid: Optional[int]):
        self.trans: Transaction
        """Transaction that this popup interacts with."""
        if sqlid is not None:
            self.trans = Transaction.from_id(sqlid)
        else:
            self.trans = Transaction()

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

        self.window.read(timeout=0)

        self._next_amount_row_id: int = 0
        self.amount_rows: list[TransactionPopup.AmountRow] = []
        if sqlid is None:
            self._set_amount_rows([TransactionPopup.AmountRow(self)])
        else:
            self._set_amount_rows(
                list(
                    TransactionPopup.AmountRow(
                        self, amount.description, str(amount.amount), amount.tags()
                    )
                    for amount in self.trans.amounts()
                )
            )

        self.selected_tags: list[Tag] = self.trans.tags()
        """Tags the user has selected but have not been synced to the transaction yet."""

        self.validated_input_keys: list[str] = [
            "-DATE INPUT-",
            "-COORDINATE INPUT-",
            "-TOTAL AMOUNT INPUT-",
        ]
        """Input widgets that extend ValidatedInput. Their validation functions must be called each event loop."""

        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            self.add_callback(validated_input.update_validation_appearance)

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
                expand_x=True,
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
        ]

        fields: list[list[Element]] = list(zip(labels, fields))

        amounts_frame: Frame = Frame(
            "Amounts",
            [
                [Button("Create New Amount", key="-NEW AMOUNT BUTTON-", expand_x=True)],
                [
                    Text(
                        "Description",
                        size=TransactionPopup.AmountRow.DESCRIPTION_INPUT_WIDTH - 5,
                    ),
                    Text(
                        "Amount",
                        size=TransactionPopup.AmountRow.AMOUNT_INPUT_WIDTH - 2,
                        key="-AMOUNTS STATUS-",
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

        if event == "-ACCOUNT SELECTOR-":
            self.trans.account_id = values["-ACCOUNT SELECTOR-"].sqlid

        if event == "-DESCRIPTION INPUT-":
            self.trans.description = values["-DESCRIPTION INPUT-"]

        if event == "-MERCHANT SELECTOR-":
            self.trans.merchant_id = values["-MERCHANT SELECTOR-"].sqlid

        if event == "-COORDINATE INPUT-":
            single_coordinate_pattern: str = r"-?\d{1,}\.?\d*"
            coords: list[str] = re.findall(
                single_coordinate_pattern, values["-COORDINATE INPUT-"]
            )
            if len(coords) == 2:
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

        if event == "-NEW AMOUNT BUTTON-":
            new_amount_row: TransactionPopup.AmountRow = TransactionPopup.AmountRow(
                self
            )
            self.amount_rows.append(new_amount_row)
            self.window.extend_layout(
                self.window["-AMOUNTS FRAME-"], [[pin(new_amount_row, expand_x=True)]]
            )

        # Update amounts counter thing
        if self._total_amount() is not None and self._amount_rows_total() is not None:
            self.window["-AMOUNTS STATUS-"].update(
                value=f"Amount ({self._total_amount() - self._amount_rows_total()} left)"
            )
        else:
            self.window["-AMOUNTS STATUS-"].update("Amount (Invalid)")

    def _total_amount(self) -> Optional[float]:
        """
        Gets the total amount from the total amount input.

        :return: Total amount from the total amount input or None if total amount is invalid
        """
        try:
            return float(self.window["-TOTAL AMOUNT INPUT-"].get())
        except ValueError:
            return None

    def _amount_rows_total(self) -> Optional[float]:
        """
        Calculates the total amount from all amount rows.

        :return: Total amount from all amount rows or None if one or more amout rows is invalid
        """
        try:
            return sum(row.amount() for row in self.amount_rows)
        except ValueError:
            return None

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
            default_description: str = "",
            default_amount: str = "",
            default_tags: Optional[list[Tag]] = None,
        ) -> None:
            self.outer: TransactionPopup = outer
            """Instance of outer class."""
            self.amount_row_id: int = self.outer._next_amount_row_id
            """Internal ID of this amount row, used make unique amount rows despite potentially hidden rows."""
            self.outer._next_amount_row_id += 1

            self.tag_list: list[Tag] = default_tags if default_tags is not None else []
            """List of selected tags for this amount."""

            super().__init__(
                [
                    [
                        Input(
                            default_description,
                            key=("-AMOUNT ROW DESCRIPTION-", self.amount_row_id),
                            size=TransactionPopup.AmountRow.DESCRIPTION_INPUT_WIDTH,
                        ),
                        Text(" $", pad=0),
                        AmountInput(
                            default_text=default_amount,
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
                expand_x=True,
            )

            self.outer.add_callback(self.event_loop_callback)

        def description(self) -> str:
            """
            Gets the description of this amount row.

            :return: Description of this amount row
            """
            return self.outer.window[
                ("-AMOUNT ROW DESCRIPTION-", self.amount_row_id)
            ].get()

        def amount(self) -> float:
            """
            Gets the amount of this amount row.

            :return: Amount of this amount row
            """
            return float(
                self.outer.window[("-AMOUNT ROW AMOUNT-", self.amount_row_id)].get()
            )

        def tags(self) -> list[Tag]:
            """
            Gets the list of tags for this amount row.

            :return: List of tags for this amount row
            """
            return self.tag_list

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
                self.outer.amount_rows.remove(self)

            if event == ("-AMOUNT ROW TAG SELECTOR-", self.amount_row_id):
                tag_selector: TagSelector = TagSelector(self.tag_list)
                tag_selector.event_loop()
                self.tag_list = tag_selector.selected_tags
                self.outer.window[
                    ("-AMOUNT ROW TAG SELECTOR-", self.amount_row_id)
                ].update(self.tags_as_string())

        def tags_as_string(self) -> str:
            """
            Formats the tags this amount row has as a single string.

            :return: Tags this amount row has as a single string
            """
            if len(self.tag_list) == 0:
                return "No Tags"
            else:
                return ", ".join(tag.name for tag in self.tag_list)
