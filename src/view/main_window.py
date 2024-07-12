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

from src import model
from src.model import database
from src.view.data_table_tab import TransactionTab, MerchantTab
from src.view.notify_popup import NotifyPopup
from src.view.popup import Popup


class MainWindow(Popup):
    """
    Main window for the application.
    """

    MENU_DEFINITION: list = [
        ["File", ["New", "Open", "Close"]],
        ["Reconcile", ["Start New Reconcile", "Continue Reconcile"]],
    ]
    """Menu bar definition."""

    def __init__(self) -> None:
        self.transaction_tab: TransactionTab
        self.merchant_tab: MerchantTab

        super().__init__("ExTract")
        database_path: Optional[Path] = self._get_database_path(notify_on_error=True)
        if database_path is not None and database_path.exists():
            database.connect(database_path)

        self.update_table()

    def _get_database_path(self, notify_on_error: bool = False) -> Optional[Path]:
        """
        Get the path to the database and throws an error if the path does not exist.

        :param notify_on_error: True if a notification popup should be thrown on error
        :return: Path to the database
        """
        database_path: Optional[Path]
        try:
            database_path = model.app_settings.database_path()
        except RuntimeError as error:
            if notify_on_error:
                NotifyPopup(str(error)).event_loop()
            return None

        if database_path is None:
            return None

        if not database_path.exists():
            if notify_on_error:
                NotifyPopup(
                    f"Database file at path '{str(database_path.absolute())}' does not exist."
                ).event_loop()
            return None

        return database_path

    def _layout_generator(self) -> list[list[Element]]:
        self.transaction_tab = TransactionTab()
        self.merchant_tab = MerchantTab()
        return [
            [MenuBar(MainWindow.MENU_DEFINITION)],
            [
                TabGroup(
                    [
                        [
                            self.transaction_tab,
                            Tab("Budgets", [[Text("Coming Soon!")]]),
                            Tab("Statements", [[Text("Coming Soon!")]]),
                            Tab("Accounts", [[Text("Coming Soon!")]]),
                            self.merchant_tab,
                            Tab("Locations", [[Text("Coming Soon!")]]),
                            Tab("Tags", [[Text("Coming Soon!")]]),
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
        self.transaction_tab.update_table()
        self.merchant_tab.update_table()

    def check_event(self, event: Any, values: dict[Any, Any]) -> None:
        """
        Respond to events from the user or test.

        :param event: Event to parse
        :param values: Values related to the event
        """

        if event in ["Open", "New"]:
            str_new_path: Optional[str] = popup_get_file(
                "",
                no_window=True,
                file_types=(("Database", "*.db"),),
                modal=True,
            )

            if str_new_path is None:
                return

            if event == "New":
                if Path(str_new_path).exists():
                    NotifyPopup(
                        f"Database file at path '{str_new_path}' already exists."
                    ).event_loop()
                    return
                database.create_new(Path(str_new_path))

            model.app_settings.set_database_path(Path(str_new_path))

            database_path: Optional[Path] = self._get_database_path()
            if database_path is not None:
                database.connect(database_path)
                self.update_table()

        if event == "Close":
            model.app_settings.set_database_path(None)
            database.close()
            self.update_table()

        if event == "-TRANSACTIONS TABLE-" and len(values["-TRANSACTIONS TABLE-"]) == 1:
            self.transaction_tab.open_edit_popup(values["-TRANSACTIONS TABLE-"][0])
