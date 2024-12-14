"""
Contains the DataTableTag class and its subclasses. These classes extend PySimpleGUI's Tab to
provide boilerplate code for that display a main table.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

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

    def __init__(self, tab_name: str, headings: list[str]) -> None:
        self.headings: list[str] = headings
        self.tab_name: str = tab_name
        self._table: Table
        super().__init__(
            tab_name, layout=self._layout_generator(), key=f"-{tab_name.upper()} TAB-"
        )
        self.row_id_list: list[int] = []
        self.values: list[list[str]] = []

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


class TransactionTab(DataTableTab):
    """
    Tab with table and DataPopup for the Transactions table.
    """

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
                for trans in Transaction.get_all()
            ]
            self.row_id_list = [int(row[0]) for row in self.values]
        else:
            self.values = [["", "", "No database connected", "", ""]]
            self.row_id_list = []

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row
        """
        if not 0 <= selected_row < len(self.row_id_list):
            return

        sqlid: int = self.row_id_list[selected_row]
        TransactionPopup(Transaction.from_id(sqlid)).event_loop()

        self.update_table()


class StatementTab(DataTableTab):
    """
    Tab with table and DataPopup for the Statements table.
    """

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
                for statement in Statement.get_all()
            ]
            self.row_id_list = [int(row[0]) for row in self.values]
        else:
            self.values = [["", "No database connected", "", ""]]
            self.row_id_list = []

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.
        """

        if not 0 <= selected_row < len(self.row_id_list):
            return

        sqlid: int = self.row_id_list[selected_row]
        StatementPopup(Statement.from_id(sqlid)).event_loop()

        self.update_table()


class MerchantTab(DataTableTab):
    """
    Tab with table and DataPopup for the Merchants table.
    """

    def __init__(self) -> None:
        super().__init__("Merchants", ["ID", "Name", "Online", "Rule"])

    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        if database.is_connected():
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
                for merchant in Merchant.get_all()
            ]
            self.row_id_list = [int(row[0]) for row in self.values]
        else:
            self.values = [["", "No database connected", "", ""]]
            self.row_id_list = []

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row
        """
        if not 0 <= selected_row < len(self.row_id_list):
            return

        sqlid: int = self.row_id_list[selected_row]
        MerchantPopup(Merchant.from_id(sqlid)).event_loop()

        self.update_table()


class AccountTab(DataTableTab):
    """
    Tab with table and DataPopup for the Accounts table.
    """

    def __init__(self) -> None:
        super().__init__(
            "Accounts", ["ID", "Name", "Amount Idx", "Desc Idx", "Date Idx"]
        )

    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        if database.is_connected():
            self.values = [
                [
                    str(account.sqlid),
                    str(account.name),
                    str(account.amount_idx),
                    str(account.description_idx),
                    str(account.date_idx),
                ]
                for account in Account.get_all()
            ]
            self.row_id_list = [int(row[0]) for row in self.values]
        else:
            self.values = [["", "No database connected", "", "", ""]]
            self.row_id_list = []

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row
        """
        if not 0 <= selected_row < len(self.row_id_list):
            return

        sqlid: int = self.row_id_list[selected_row]
        AccountPopup(Account.from_id(sqlid)).event_loop()

        self.update_table()


class LocationTab(DataTableTab):
    """
    Tab with table and DataPopup for the Locations table.
    """

    def __init__(self) -> None:
        super().__init__(
            "Locations", ["ID", "Description", "Merchant", "Latitude", "Longitude"]
        )

    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        if database.is_connected():
            self.values = [
                [
                    str(location.sqlid),
                    "None" if location.description is None else location.description,
                    location.merchant().name,  # type: ignore
                    str(location.lat),
                    str(location.long),
                ]
                for location in Location.get_all()
            ]
            self.row_id_list = [int(row[0]) for row in self.values]
        else:
            self.values = [["", "No database connected", "", "", ""]]
            self.row_id_list = []

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row
        """
        if not 0 <= selected_row < len(self.row_id_list):
            return

        sqlid: int = self.row_id_list[selected_row]
        LocationPopup(Location.from_id(sqlid)).event_loop()

        self.update_table()


class TagTab(DataTableTab):
    """
    Tab with table and DataPopup for the Tags table.
    """

    def __init__(self) -> None:
        super().__init__("Tags", ["ID", "Name", "Occasional", "Rule"])

    def update_table(self) -> None:
        """
        Updates the table from the database and updates the row id list.
        """
        if database.is_connected():
            self.values = [
                [
                    str(tag.sqlid),
                    "None" if tag.name is None else tag.name,
                    str(tag.occasional),
                    "None" if tag.rule is None else tag.rule,
                ]
                for tag in Tag.get_all()
            ]
            self.row_id_list = [int(row[0]) for row in self.values]
        else:
            self.values = [["", "No database connected", "", ""]]
            self.row_id_list = []

        self._table.update(values=self.values)

    def open_edit_popup(self, selected_row: int) -> None:
        """
        Opens the edit popup for the selected row.

        :param selected_row: Index of the selected row
        """
        if not 0 <= selected_row < len(self.row_id_list):
            return

        sqlid: int = self.row_id_list[selected_row]
        TagPopup(Tag.from_id(sqlid)).event_loop()

        self.update_table()
