"""
Contains the DataTableTag class and its subclasses. These classes extend PySimpleGUI's Tab to
provide boilerplate code for that display a main table.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any

from PySimpleGUI import Element, Table, Tab  # type: ignore

from src.model import database
from src.model.account import Account
from src.model.location import Location
from src.model.merchant import Merchant
from src.model.statement import Statement
from src.model.tag import Tag
from src.model.transaction import Transaction
from src.view import full_date_format
from src.view import short_date_format
from src.view.account_popup import AccountPopup
from src.view.data_popup import DataPopup
from src.view.location_popup import LocationPopup
from src.view.merchant_popup import MerchantPopup
from src.view.statement_popup import StatementPopup
from src.view.tag_popup import TagPopup
from src.view.transaction_popup import TransactionPopup

T = TypeVar("T", bound=DataPopup)


class DataTableTab(Tab, ABC, Generic[T]):
    """
    Tab with table and DataPopup for the main tables.
    """

    HEADER_CLICKED_EVENT: str = "+CLICKED+"

    def __init__(self, tab_name: str, headings: list[str]) -> None:
        self.headings: list[str] = headings
        """List of table headings."""
        self.tab_name: str = tab_name
        """Name of the tab."""
        self._table: Table
        """Internal table element."""
        super().__init__(
            tab_name, layout=self._layout_generator(), key=f"-{tab_name.upper()} TAB-"
        )
        self.values: list[list[str]] = []
        """List of table values."""
        self.sort_by_column_index: int = 0
        """Index of the table column that the values should be sorted by."""
        self.sort_by_ascending: bool = True
        """True if the sort by column should be sorted in ascending or descending order."""

    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the window

        :return: Layout for the window
        """
        self._table = Table(
            [],
            headings=self.headings,
            key=f"-{self.tab_name.upper()} TABLE-",
            enable_events=True,
            enable_click_events=True,
            expand_x=True,
            expand_y=True,
            justification="left",
        )
        return [[self._table]]

    @abstractmethod
    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        raise NotImplementedError()

    @abstractmethod
    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row.
        """
        raise NotImplementedError()

    def event_loop_callback(self, event: Any, values: dict[Any, Any]) -> None:
        """
        Event loop callback. Gets called every event loop iteration to respond to element specific events.
        """
        if event is not None and DataTableTab.HEADER_CLICKED_EVENT in event:
            selected_column_index: int = event[2][1]

            if selected_column_index == self.sort_by_column_index:
                self.sort_by_ascending = not self.sort_by_ascending
            else:
                self.sort_by_column_index = selected_column_index
                self.sort_by_ascending = True

        self.update_table()


class TransactionTab(DataTableTab):
    """
    Tab with table and DataPopup for the Transactions table.
    """

    ACCOUNT_COLUMN_INDEX: int = 1
    DESCRIPTION_COLUMN_INDEX: int = 2
    TOTAL_AMOUNT_COLUMN_INDEX: int = 3
    MERCHANT_COLUMN_INDEX: int = 4
    DATE_COLUMN_INDEX: int = 5

    def __init__(self) -> None:
        super().__init__(
            "Transactions",
            ["ID", "Account", "Description", "Total Amount", "Merchant", "Date"],
        )

    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        if database.is_connected():

            sort_key: Any
            invert: bool = False

            if self.sort_by_column_index == TransactionTab.ACCOUNT_COLUMN_INDEX:
                sort_key = lambda x: (
                    "None" if x.account_id is None else x.account().name
                )
            elif self.sort_by_column_index == TransactionTab.DESCRIPTION_COLUMN_INDEX:
                sort_key = lambda x: str(x.description)
            elif self.sort_by_column_index == TransactionTab.TOTAL_AMOUNT_COLUMN_INDEX:
                sort_key = lambda x: abs(x.total_amount())
                invert = True
            elif self.sort_by_column_index == TransactionTab.MERCHANT_COLUMN_INDEX:
                sort_key = lambda x: (
                    "None" if x.merchant_id is None else x.merchant().name
                )
            elif self.sort_by_column_index == TransactionTab.DATE_COLUMN_INDEX:
                sort_key = lambda x: 0 if x.date is None else x.date.timestamp()
                invert = True
            else:
                sort_key = lambda x: x.sqlid

            self.values = [
                [
                    str(trans.sqlid),
                    "None" if trans.account_id is None else trans.account().name,  # type: ignore
                    "None" if trans.description is None else trans.description,
                    str(trans.total_amount()),
                    "None" if trans.merchant_id is None else trans.merchant().name,  # type: ignore
                    (
                        "None"
                        if trans.date is None
                        else trans.date.strftime(full_date_format)
                    ),
                ]
                for trans in sorted(
                    Transaction.get_all(),
                    key=sort_key,
                    reverse=self.sort_by_ascending == invert,
                )
            ]

        else:
            self.values = [["", "", "No database connected", "", ""]]

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row
        """
        if not 0 <= selected_row < len(self.values):
            return

        sqlid: int = int(self.values[selected_row][0])
        TransactionPopup(Transaction.from_id(sqlid)).event_loop()

        self.update_table()


class StatementTab(DataTableTab):
    """
    Tab with table and DataPopup for the Statements table.
    """

    DATE_COLUMN_INDEX: int = 1
    ACCOUNT_COLUMN_INDEX: int = 2
    STARTING_BALANCE_COLUMN_INDEX: int = 3
    RECONCILED_COLUMN_INDEX: int = 4

    def __init__(self) -> None:
        super().__init__(
            "Statements",
            ["ID", "Date", "Account", "Starting Balance", "Reconciled"],
        )

    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        if database.is_connected():

            sort_key: Any
            invert: bool = False

            if self.sort_by_column_index == StatementTab.DATE_COLUMN_INDEX:
                sort_key = lambda x: 0 if x.date is None else x.date.timestamp()
                invert = True
            elif self.sort_by_column_index == StatementTab.ACCOUNT_COLUMN_INDEX:
                sort_key = lambda x: (
                    "None" if x.account_id is None else x.account().name
                )
            elif (
                self.sort_by_column_index == StatementTab.STARTING_BALANCE_COLUMN_INDEX
            ):
                sort_key = lambda x: abs(x.starting_balance)
                invert = True
            elif self.sort_by_column_index == StatementTab.RECONCILED_COLUMN_INDEX:
                sort_key = lambda x: x.reconciled
            else:
                sort_key = lambda x: x.sqlid

            self.values = [
                [
                    str(statement.sqlid),
                    (
                        "None"
                        if statement.date is None
                        else statement.date.strftime(short_date_format)
                    ),
                    (
                        "None"
                        if statement.account_id is None
                        else statement.account().name  # type: ignore
                    ),
                    str(statement.starting_balance),
                    str(statement.reconciled),
                ]
                for statement in sorted(
                    Statement.get_all(),
                    key=sort_key,
                    reverse=self.sort_by_ascending == invert,
                )
            ]
        else:
            self.values = [["", "No database connected", "", ""]]

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.
        """

        if not 0 <= selected_row < len(self.values):
            return

        sqlid: int = int(self.values[selected_row][0])
        StatementPopup(Statement.from_id(sqlid)).event_loop()

        self.update_table()


class MerchantTab(DataTableTab):
    """
    Tab with table and DataPopup for the Merchants table.
    """

    NAME_COLUMN_INDEX: int = 1
    ONLINE_COLUMN_INDEX: int = 2
    RULE_COLUMN_INDEX: int = 3

    def __init__(self) -> None:
        super().__init__("Merchants", ["ID", "Name", "Online", "Rule"])

    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        if database.is_connected():

            sort_key: Any
            invert: bool = False

            if self.sort_by_column_index == MerchantTab.NAME_COLUMN_INDEX:
                sort_key = lambda x: str(x.name)
            elif self.sort_by_column_index == MerchantTab.ONLINE_COLUMN_INDEX:
                sort_key = lambda x: {False: 0, True: 1, None: 2}[x.online]
            elif self.sort_by_column_index == MerchantTab.RULE_COLUMN_INDEX:
                sort_key = lambda x: str(x.rule)
                invert = True
            else:
                sort_key = lambda x: x.sqlid

            self.values = [
                [
                    str(merchant.sqlid),
                    "None" if merchant.name is None else merchant.name,
                    {None: "Error", True: "True", False: "False"}[merchant.online],
                    (
                        "No Tags"
                        if merchant.default_tags() == []
                        else ", ".join(
                            tag.name
                            for tag in merchant.default_tags()
                            if tag.name is not None
                        )
                    ),
                    "None" if merchant.rule is None else merchant.rule,
                ]
                for merchant in sorted(
                    Merchant.get_all(),
                    key=sort_key,
                    reverse=self.sort_by_ascending == invert,
                )
            ]
        else:
            self.values = [["", "No database connected", "", ""]]

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row
        """
        if not 0 <= selected_row < len(self.values):
            return

        sqlid: int = int(self.values[selected_row][0])
        MerchantPopup(Merchant.from_id(sqlid)).event_loop()

        self.update_table()


class AccountTab(DataTableTab):
    """
    Tab with table and DataPopup for the Accounts table.
    """

    NAME_COLUMN_INDEX: int = 1
    AMOUNT_IDX_COLUMN_INDEX: int = 2
    DESC_IDX_COLUMN_INDEX: int = 3
    DATE_IDX_COLUMN_INDEX: int = 4

    def __init__(self) -> None:
        super().__init__(
            "Accounts", ["ID", "Name", "Amount Idx", "Desc Idx", "Date Idx"]
        )

    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        if database.is_connected():

            sort_key: Any
            invert: bool = False

            if self.sort_by_column_index == AccountTab.NAME_COLUMN_INDEX:
                sort_key = lambda x: str(x.name)
            elif self.sort_by_column_index == AccountTab.AMOUNT_IDX_COLUMN_INDEX:
                sort_key = lambda x: 999 if x.amount_idx is None else x.amount_idx
            elif self.sort_by_column_index == AccountTab.DESC_IDX_COLUMN_INDEX:
                sort_key = lambda x: (
                    999 if x.description_idx is None else x.description_idx
                )
            elif self.sort_by_column_index == AccountTab.DATE_IDX_COLUMN_INDEX:
                sort_key = lambda x: 999 if x.date_idx is None else x.date_idx
            else:
                sort_key = lambda x: x.sqlid

            self.values = [
                [
                    str(account.sqlid),
                    str(account.name),
                    str(account.amount_idx),
                    str(account.description_idx),
                    str(account.date_idx),
                ]
                for account in sorted(
                    Account.get_all(),
                    key=sort_key,
                    reverse=self.sort_by_ascending == invert,
                )
            ]
        else:
            self.values = [["", "No database connected", "", "", ""]]

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row
        """
        if not 0 <= selected_row < len(self.values):
            return

        sqlid: int = int(self.values[selected_row][0])
        AccountPopup(Account.from_id(sqlid)).event_loop()

        self.update_table()


class LocationTab(DataTableTab):
    """
    Tab with table and DataPopup for the Locations table.
    """

    DESCRIPTION_COLUMN_INDEX: int = 1
    MERCHANT_COLUMN_INDEX: int = 2
    LATITUDE_COLUMN_INDEX: int = 3
    LONGITUDE_COLUMN_INDEX: int = 4

    def __init__(self) -> None:
        super().__init__(
            "Locations", ["ID", "Description", "Merchant", "Latitude", "Longitude"]
        )

    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        if database.is_connected():

            sort_key: Any
            invert: bool = False

            if self.sort_by_column_index == LocationTab.DESCRIPTION_COLUMN_INDEX:
                sort_key = lambda x: str(x.description)
            elif self.sort_by_column_index == LocationTab.MERCHANT_COLUMN_INDEX:
                sort_key = lambda x: x.merchant().name
            elif self.sort_by_column_index == LocationTab.LATITUDE_COLUMN_INDEX:
                sort_key = lambda x: 0 if x.lat is None else x.lat
            elif self.sort_by_column_index == LocationTab.LONGITUDE_COLUMN_INDEX:
                sort_key = lambda x: 0 if x.long is None else x.long
            else:
                sort_key = lambda x: x.sqlid

            self.values = [
                [
                    str(location.sqlid),
                    "None" if location.description is None else location.description,
                    location.merchant().name,  # type: ignore
                    str(location.lat),
                    str(location.long),
                ]
                for location in sorted(
                    Location.get_all(),
                    key=sort_key,
                    reverse=self.sort_by_ascending == invert,
                )
            ]
        else:
            self.values = [["", "No database connected", "", "", ""]]

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row
        """
        if not 0 <= selected_row < len(self.values):
            return

        sqlid: int = int(self.values[selected_row][0])
        LocationPopup(Location.from_id(sqlid)).event_loop()

        self.update_table()


class TagTab(DataTableTab):
    """
    Tab with table and DataPopup for the Tags table.
    """

    NAME_COLUMN_INDEX: int = 1
    OCCASIONAL_COLUMN_INDEX: int = 2
    RULES_COLUMN_INDEX: int = 3

    def __init__(self) -> None:
        super().__init__("Tags", ["ID", "Name", "Occasional", "Rule"])

    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        if database.is_connected():

            sort_key: Any
            invert: bool = False

            if self.sort_by_column_index == TagTab.NAME_COLUMN_INDEX:
                sort_key = lambda x: str(x.name)
            elif self.sort_by_column_index == TagTab.OCCASIONAL_COLUMN_INDEX:
                sort_key = lambda x: {False: 0, True: 1, None: 2}[x.occasional]
            elif self.sort_by_column_index == TagTab.RULES_COLUMN_INDEX:
                sort_key = lambda x: "None" if x.rule is None else x.rule
            else:
                sort_key = lambda x: x.sqlid

            self.values = [
                [
                    str(tag.sqlid),
                    "None" if tag.name is None else tag.name,
                    str(tag.occasional),
                    "None" if tag.rule is None else tag.rule,
                ]
                for tag in sorted(
                    Tag.get_all(),
                    key=sort_key,
                    reverse=self.sort_by_ascending == invert,
                )
            ]
        else:
            self.values = [["", "No database connected", "", ""]]

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row
        """
        if not 0 <= selected_row < len(self.values):
            return

        sqlid: int = int(self.values[selected_row][0])
        TagPopup(Tag.from_id(sqlid)).event_loop()

        self.update_table()
