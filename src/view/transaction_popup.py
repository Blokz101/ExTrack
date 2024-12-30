"""
Contains the TransactionPopup class which allows the user to create or edit a transaction.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import cast, Optional, Any
from pathlib import Path

from PySimpleGUI import Element, Text, Combo, Input, Button, Frame, Column, pin  # type: ignore

from src import model
from src.model.account import Account
from src.model.amount import Amount
from src.model.merchant import Merchant
from src.model.tag import Tag
from src.model.transaction import Transaction
from src.view import full_date_format, short_date_format
from src.view.data_popup import DataPopup
from src.view.popup import ClosedStatus
from src.view.tag_selector import TagSelector
from src.view.validated_input import (
    ValidatedInput,
    CoordinateInput,
    DateInput,
    AmountInput,
)
from src.view.image_viewer import ImageViewer
from src.view.searchable_combo import SearchableCombo


class TransactionPopup(DataPopup):
    """
    Popup that allows the user to create or edit a transaction.
    """

    def __init__(
        self,
        trans: Optional[Transaction],
        use_default_account: bool = True,
        import_folder: Optional[Path] = None,
        merchant_order: list[int] = None,
    ) -> None:
        """
        :param trans: Transaction to prefill fields with
        :param use_default_account: True if the default account should be used if none is provided with the transaction
        :param import_folder: Folder that the image for this transaction is in if it exists, used to locate and display the photo during import from photo.
        :param merchant_order: Order that merchants options should be displayed in the merchant selector. Merchants that are not in this list will be added to the end.
        """
        self.trans: Transaction
        """Transaction that this popup interacts with."""
        if trans is not None:
            self.trans = trans
        else:
            self.trans = Transaction(reconciled=False)

        if use_default_account and self.trans.account_id is None:
            self.trans.account_id = (
                Account.default_account().sqlid
                if Account.default_account() is not None
                else None
            )

        self.import_folder: Optional[Path] = import_folder
        """Path to the folder that images are being imported from. Used to locate and display the photo during import."""

        self.merchant_order: Optional[list[int]] = merchant_order
        """Order that merchants options should be displayed in the merchant selector."""

        super().__init__(
            f"Transaction ID = {self.trans.sqlid if self.trans.sqlid is not None else "New"}",
            delete_supported=self.trans.exists(),
            layout_generator=self._layout_generator,
        )

        self.account: Optional[Account] = self.trans.account()
        """Internal Account object updated by the account combo element."""

        self.merchant: Optional[Merchant] = self.trans.merchant()
        """Internal Merchant object updated by the merchant combo element."""

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

        self.validated_input_keys: list[str] = [
            "-DATE INPUT-",
            "-COORDINATE INPUT-",
            "-TOTAL AMOUNT INPUT-",
        ]
        """
        Input widgets that extend ValidatedInput. Their validation functions must be called each 
        event loop.
        """

        # Add various callback functions
        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            self.add_callback(validated_input.update_validation_appearance)
        self.add_callback(
            cast(
                SearchableCombo, self.window["-MERCHANT SELECTOR-"]
            ).event_loop_callback
        )
        self.add_callback(
            cast(ImageViewer, self.window["-IMAGE VIEWER-"]).event_loop_callback
        )

        cast(ImageViewer, self.window["-IMAGE VIEWER-"]).set_image(
            self._get_image_path(), self.window
        )
        self.window["-DONE BUTTON-"].update(disabled=not self.inputs_valid())

        self.window.bind("<Escape>", "-ESCAPE-")

    def _layout_generator(self) -> list[list[Element]]:
        return [
            [
                Column(super()._layout_generator()),
                ImageViewer(key="-IMAGE VIEWER-"),
            ]
        ]

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
                "Image Name: ",
                "Reconciled: ",
                "Statement: ",
                "Transfer Transaction: ",
            ]
        )

        merchant_list: list[Merchant]
        if self.merchant_order is None:
            merchant_list = sorted(Merchant.get_all(), key=lambda x: x.name)
        else:
            merchant_list = list(Merchant.from_id(x) for x in self.merchant_order)

            # Add the rest of the merchants
            merchant_list += sorted(
                list(x for x in Merchant.get_all() if x not in merchant_list),
                key=lambda x: x.name,
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
                expand_x=True,
            ),
            SearchableCombo(
                merchant_list,
                default_value=self.trans.merchant(),
                key="-MERCHANT SELECTOR-",
            ),
            CoordinateInput(
                default_text=f"{self.trans.lat}, {self.trans.long}",
                key="-COORDINATE INPUT-",
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
                expand_x=True,
            ),
            Input(
                default_text=(
                    ""
                    if self.trans.receipt_file_name is None
                    else self.trans.receipt_file_name
                ),
                key="-RECEIPT PATH INPUT-",
                expand_x=True,
                enable_events=True,
                disabled=self.import_folder is not None,
            ),
            Text(
                self.trans.reconciled,
                key="-RECONCILED TEXT-",
            ),
            Text(
                (
                    self.trans.statement().date.strftime(short_date_format)  # type: ignore
                    if self.trans.statement_id is not None
                    else "None"
                ),
                key="-STATEMENT TEXT-",
                expand_x=True,
            ),
            Text(
                (
                    self.trans.transfer_trans().description  # type: ignore
                    if self.trans.transfer_trans_id is not None
                    else "None"
                ),
                key="-TRANSFER TRANSACTION TEXT-",
                expand_x=True,
            ),
        ]

        body: list[list[Element]] = [list(row) for row in zip(labels, fields)]

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

        return body + [[amounts_frame]]

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

    def _get_image_path(self) -> Optional[Path]:
        """
        Combines the image name and file path from settings to get the full image path.

        :return: Absolute path to image.
        """
        folder_search_list: list[Path] = [
            model.app_settings.receipts_folder(),
            self.import_folder,
        ]

        for folder in folder_search_list:
            if folder is None:
                continue
            image_path: Path = folder / self.window["-RECEIPT PATH INPUT-"].get()
            if image_path.exists():
                return image_path

        return None

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    def check_event(self, event: Any, values: dict) -> None:
        """
        Respond to events from the user.

        :param event: Event to parse
        :param values: Values related to the event
        """
        super().check_event(event, values)

        if event == "-CREATE BUTTON-":
            self.close(closed_status=ClosedStatus.OPERATION_SUCCESS)
            TransactionPopup(None).event_loop()
            return

        if event == "-DELETE BUTTON-":
            self.trans.delete()
            self.close(closed_status=ClosedStatus.OPERATION_SUCCESS)
            return

        if event == "-ACCOUNT SELECTOR-":
            self.account = values["-ACCOUNT SELECTOR-"]

        if event is not None and "-MERCHANT SELECTOR-" in event:
            self.merchant = cast(
                SearchableCombo, self.window["-MERCHANT SELECTOR-"]
            ).selected_value

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
            elif self.window["-COORDINATE INPUT-"].get() == "None, None":
                self.trans.lat = None
                self.trans.long = None

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

            self.trans.receipt_file_name = self.window["-RECEIPT PATH INPUT-"].get()

            # Sync Transaction and Amounts
            self.trans.sync()

            # Sync the existing and new rows first
            for row in self.amount_rows:
                if not row.visible:
                    continue
                row.amount.transaction_id = self.trans.sqlid
                row.sync_row()

            # Sync the deleted rows last
            for row in self.amount_rows:
                if row.visible:
                    continue
                row.amount.transaction_id = self.trans.sqlid
                row.sync_row()

            self.close(ClosedStatus.OPERATION_SUCCESS)
            return

        if event == "-NEW AMOUNT BUTTON-":
            new_amount_row: TransactionPopup.AmountRow = TransactionPopup.AmountRow(
                self,
                default_amount=(
                    Amount()
                    if self._total_row_amount_difference() is None
                    else Amount(amount=self._total_row_amount_difference())
                ),
                use_default_tags=True,
            )
            self.amount_rows.append(new_amount_row)
            self.window.extend_layout(
                self.window["-AMOUNTS FRAME-"], [[pin(new_amount_row, expand_x=True)]]
            )

        if event == "-RECEIPT PATH INPUT-":
            image_path: Optional[Path] = self._get_image_path()
            if image_path is not None and image_path.exists():
                cast(ImageViewer, self.window["-IMAGE VIEWER-"]).set_image(
                    image_path, self.window
                )
            else:
                cast(ImageViewer, self.window["-IMAGE VIEWER-"]).set_image(
                    None, self.window
                )

        if event == "-ESCAPE-":
            self.close(closed_status=ClosedStatus.OPERATION_SUCCESS)
            return

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
            return round(self._total_amount() - self._amount_rows_total(), 2)  # type: ignore
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
            rows_sum += row_amount
        return round(rows_sum, 2)

    def inputs_valid(self) -> bool:
        """
        Checks if all inputs are valid.

        :return: True if all inputs are valid, false otherwise
        """
        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            if validated_input.validation_status() is not None:
                return False

        if self.account is None:
            return False

        if (
            self._total_amount() is None
            or self._amount_rows_total() is None
            or self._total_amount() != self._amount_rows_total()
        ):
            return False

        return True

    class AmountRow(Column):
        """
        Element that allows the user to edit a single amount and its tags.
        """

        DESCRIPTION_INPUT_WIDTH: int = 40
        """Fixed width of the description input widget."""
        AMOUNT_INPUT_WIDTH: int = 15
        """Fixed width of the amount input widget."""

        def __init__(
            self,
            outer: TransactionPopup,
            default_amount: Optional[Amount] = None,
            use_default_tags: bool = False,
        ) -> None:
            """
            :param outer: Superclass instance
            :param default_amount: Default Amount for this amount row, if None a new Amount will
            be created
            :param use_default_tags: True if the merchant default tags should be used,
            false otherwise
            """

            self.outer: TransactionPopup = outer
            """Instance of outer class."""
            self.amount: Amount = Amount() if default_amount is None else default_amount
            """Underlying SqlObject used to communicate with the database."""
            self.amount_row_id: int = self.outer._next_amount_row_id
            """
            Internal ID of this amount row, used make unique amount rows despite potentially 
            hidden rows.
            """
            self.outer._next_amount_row_id += 1

            self.tag_list: list[Tag] = self.amount.tags()
            """List of selected tags for this amount."""
            if use_default_tags:
                merchant: Optional[Merchant] = self.outer.merchant
                if merchant is None:
                    self.tag_list = []
                else:
                    self.tag_list = merchant.default_tags()
            else:
                self.tag_list = self.amount.tags()

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
                self.amount.set_tags(
                    [
                        tag.sqlid
                        for tag in self.tag_list
                        if tag is not None and tag.sqlid is not None
                    ]
                )
            elif self.amount.exists():
                self.amount.delete()
                del self  # This will cause trouble if the user calls sync on this row again

        def event_loop_callback(self, event: Any, _) -> None:
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
            return ", ".join(
                "None" if tag.name is None else tag.name for tag in self.tag_list
            )
