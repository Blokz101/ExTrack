"""
Contains the MainWindow class which represents the main window for the application.
"""

from pathlib import Path
from typing import Any, Optional

from PySimpleGUI import (  # type: ignore
    Table,
    TabGroup,
    Tab,
    Element,
    Text,
    MenuBar,
    popup_get_file,
)

from src.model import user_settings, database
from src.model.transaction import Transaction
from src.view import full_date_format
from src.view.popup import Popup
from src.view.transaction_popup import TransactionPopup


class MainWindow(Popup):
    """
    Main window for the application.
    """

    MENU_DEFINITION: list = [
        ["File", ["Connect", "Disconnect"]],
        ["Reconcile", ["Start New Reconcile", "Continue Reconcile"]],
    ]
    """Menu bar definition."""

    def __init__(self) -> None:
        super().__init__("ExTract")
        database_path: Optional[Path] = user_settings.database_path()
        if database_path is not None:
            database.connect(database_path)

        self._row_id_list: list[int] = []
        """List of transaction sql IDs in the order they appear in the table."""

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
                    enable_events=True,
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
            [MenuBar(MainWindow.MENU_DEFINITION)],
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
            ],
        ]

    def update_table(self) -> None:
        """
        Updates the table with transactions from the database.
        """
        new_values: list[list[str]]
        if user_settings.database_path() is None:
            new_values = [["", "", "No database connected", "", ""]]
            self._row_id_list = []
        else:
            new_values = [
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
            self._row_id_list = [int(row[0]) for row in new_values]

        self.window["-TRANSACTIONS TABLE-"].update(values=new_values)

    def check_event(self, event: Any, values: dict[Any, Any]) -> None:
        """
        Respond to events from the user or test.

        :param event: Event to parse
        :param values: Values related to the event
        """

        if event == "Connect":
            str_new_path: Optional[str] = popup_get_file(
                "",
                no_window=True,
                file_types=(("Database", "*.db"),),
            )

            if str_new_path is None:
                return

            user_settings.set_database_path(Path(str_new_path))

            database_path: Optional[Path] = user_settings.database_path()
            if database_path is not None:
                database.connect(database_path)
                self.update_table()

        if event == "Disconnect":
            user_settings.set_database_path(None)
            database.close()
            self.update_table()

        if event == "-TRANSACTIONS TABLE-":
            selected_row_index_list: list[int] = values["-TRANSACTIONS TABLE-"]

            # If the row is deselected then ignore the event.
            if len(selected_row_index_list) <= 0:
                return

            # If the row is out of bounds then ignore the event.
            if not 0 <= selected_row_index_list[0] < len(self._row_id_list):
                return

            selected_transaction: Transaction = Transaction.from_id(
                self._row_id_list[selected_row_index_list[0]]
            )
            TransactionPopup(selected_transaction).event_loop()

            self.update_table()
