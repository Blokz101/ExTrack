"""
Contains the MainWindow class which represents the main window for the application.
"""

from typing import Any

from PySimpleGUI import Table, TabGroup, Tab, Element, Text  # type: ignore

from src.model.transaction import Transaction
from src.view import full_date_format
from src.view.popup import Popup


class MainWindow(Popup):
    """
    Main window for the application.
    """

    def __init__(self) -> None:
        super().__init__("ExTract")
        self.update_table()

    @staticmethod
    def _transactions_tab_layout_generator() -> list[list[Element]]:
        """
        Generates the layout for the transactions tab.

        :return: Layout for the transactions tab
        """
        return [
            [
                Table(
                    [],
                    headings=[
                        "ID",
                        "Account",
                        "Description",
                        "Total Amount",
                        "Merchant",
                        "Date",
                    ],
                    key="-TRANSACTIONS TABLE-",
                    expand_x=True,
                    expand_y=True,
                    auto_size_columns=True,
                    justification="left",
                )
            ]
        ]

    @staticmethod
    def _budgets_tab_layout_generator() -> list[list[Element]]:
        """
        Generates the layout for the budgets tab.

        :return: Layout for the budgets tab
        """
        return [[Text("Coming Soon!")]]

    @staticmethod
    def _statements_tab_layout_generator() -> list[list[Element]]:
        """
        Generates the layout for the statements tab.

        :return: Layout for the statements tab
        """
        return [[Text("Coming Soon!")]]

    @staticmethod
    def _accounts_tab_layout_generator() -> list[list[Element]]:
        """
        Generates the layout for the accounts tab.

        :return: Layout for the accounts tab
        """
        return [[Text("Coming Soon!")]]

    @staticmethod
    def _merchants_tab_layout_generator() -> list[list[Element]]:
        """
        Generates the layout for the merchants tab.

        :return: Layout for the merchants tab
        """
        return [[Text("Coming Soon!")]]

    @staticmethod
    def _locations_tab_layout_generator() -> list[list[Element]]:
        """
        Generates the layout for the locations tab.

        :return: Layout for the locations tab
        """
        return [[Text("Coming Soon!")]]

    @staticmethod
    def _tags_tab_layout_generator() -> list[list[Element]]:
        """
        Generates the layout for the tags tab.

        :return: Layout for the tags tab
        """
        return [[Text("Coming Soon!")]]

    def _layout_generator(self) -> list[list[Element]]:
        return [
            [
                TabGroup(
                    [
                        [
                            Tab(
                                "Transactions",
                                self._transactions_tab_layout_generator(),
                            ),
                            Tab("Budgets", self._transactions_tab_layout_generator()),
                            Tab("Statements", self._statements_tab_layout_generator()),
                            Tab("Accounts", self._accounts_tab_layout_generator()),
                            Tab("Merchants", self._merchants_tab_layout_generator()),
                            Tab("Locations", self._locations_tab_layout_generator()),
                            Tab("Tags", self._tags_tab_layout_generator()),
                        ]
                    ],
                    expand_x=True,
                    expand_y=True,
                ),
            ]
        ]

    def update_table(self) -> None:
        """
        Updates the table with transactions from the database.
        """
        self.window["-TRANSACTIONS TABLE-"].update(
            values=[
                [
                    str(trans.sqlid),
                    "None" if trans.account_id is None else trans.account().name,  # type: ignore
                    trans.description,
                    trans.total_amount(),
                    "None" if trans.merchant_id is None else trans.merchant().name,  # type: ignore
                    (
                        "None"
                        if trans.date is None
                        else trans.date.strftime(full_date_format)
                    ),
                ]
                for trans in Transaction.get_all()
            ]
        )

    def check_event(self, event: Any, values: dict[Any, Any]) -> None:
        """
        Respond to events from the user or test.

        :param event: Event to parse
        :param values: Values related to the event
        """
