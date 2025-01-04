"""
Contains the MainWindow class which represents the main window for the application.
"""

from pathlib import Path
from typing import Any, Optional

from PySimpleGUI import (  # type: ignore
    TabGroup,
    Tab,
    Element,
    Text,
    MenuBar,
    popup_get_file,
)

from src.model.transaction import Transaction
from src import model
from src.model import database
from src.view.data_table_tab import (
    StatementTab,
    TransactionTab,
    MerchantTab,
    AccountTab,
    LocationTab,
    TagTab,
)
from src.view.notify_popup import NotifyPopup
from src.view.photo_import_popup import PhotoImportPopup
from src.view.popup import Popup
from src.view.account_popup import AccountPopup
from src.view.location_popup import LocationPopup
from src.view.merchant_popup import MerchantPopup
from src.view.statement_popup import StatementPopup
from src.view.tag_popup import TagPopup
from src.view.transaction_popup import TransactionPopup


class MainWindow(Popup):
    """
    Main window for the application.
    """

    MENU_DEFINITION: list = [
        ["File", ["New", "Open", "Close"]],
        [
            "New Entry",
            [
                "New Transaction",
                "New Budget",
                "New Statement",
                "New Account",
                "New Merchant",
                "New Location",
                "New Tag",
            ],
        ],
        ["Import", ["From Photos", "From Statement"]],
        ["Export", ["Transactions"]],
        ["Reconcile", ["Start New Reconcile", "Continue Reconcile"]],
    ]
    """Menu bar definition."""

    def __init__(self) -> None:
        self.statement_tab: StatementTab
        self.transaction_tab: TransactionTab
        self.account_tab: AccountTab
        self.merchant_tab: MerchantTab
        self.location_tab: LocationTab
        self.tag_tab: TagTab

        super().__init__("ExTract")
        database_path: Optional[Path] = self._get_database_path(notify_on_error=True)
        if database_path is not None and database_path.exists():
            database.connect(database_path)

        self.add_callback(self.statement_tab.event_loop_callback)
        self.add_callback(self.transaction_tab.event_loop_callback)
        self.add_callback(self.account_tab.event_loop_callback)
        self.add_callback(self.merchant_tab.event_loop_callback)
        self.add_callback(self.location_tab.event_loop_callback)
        self.add_callback(self.tag_tab.event_loop_callback)

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
        self.statement_tab = StatementTab()
        self.transaction_tab = TransactionTab()
        self.account_tab = AccountTab()
        self.merchant_tab = MerchantTab()
        self.location_tab = LocationTab()
        self.tag_tab = TagTab()
        return [
            [MenuBar(MainWindow.MENU_DEFINITION)],
            [
                TabGroup(
                    [
                        [
                            self.transaction_tab,
                            Tab("Budgets", [[Text("Coming Soon!")]]),
                            self.statement_tab,
                            self.account_tab,
                            self.merchant_tab,
                            self.location_tab,
                            self.tag_tab,
                        ]
                    ],
                    key="-TAB GROUP-",
                    expand_x=True,
                    expand_y=True,
                ),
            ],
        ]

    def update_table(self) -> None:
        """
        Updates the table with transactions from the database.
        """
        self.statement_tab.update_table()
        self.transaction_tab.update_table()
        self.account_tab.update_table()
        self.merchant_tab.update_table()
        self.location_tab.update_table()
        self.tag_tab.update_table()

    def check_event(self, event: Any, values: dict[Any, Any]) -> None:
        """
        Respond to events from the user or test.

        :param event: Event to parse
        :param values: Values related to the event
        """
        super().check_event(event, values)

        if event in ["Open", "New"]:
            str_new_path: Optional[str] = popup_get_file(
                "",
                no_window=True,
                file_types=(("Database", "*.db"),),
                modal=True,
                save_as=event == "New",
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

        # Handle menu item events
        if (
            event in MainWindow.MENU_DEFINITION[1][1]
            and self.window.TKroot.focus_displayof() is not None
        ):
            if event == "New Transaction":
                self.window["-TRANSACTIONS TAB-"].select()
                TransactionPopup(None).event_loop()
            if event == "New Budget":
                NotifyPopup("Coming Soon!").event_loop()
            if event == "New Statement":
                self.window["-STATEMENTS TAB-"].select()
                StatementPopup(None).event_loop()
            if event == "New Account":
                self.window["-ACCOUNTS TAB-"].select()
                AccountPopup(None).event_loop()
            if event == "New Merchant":
                self.window["-MERCHANTS TAB-"].select()
                MerchantPopup(None).event_loop()
            if event == "New Location":
                self.window["-LOCATIONS TAB-"].select()
                LocationPopup(None).event_loop()
            if event == "New Tag":
                self.window["-TAGS TAB-"].select()
                TagPopup(None).event_loop()
            self.update_table()

        if event == "From Photos":
            PhotoImportPopup().event_loop()
            self.update_table()

        if event == "Close":
            model.app_settings.set_database_path(None)
            database.close()
            self.update_table()

        if event == "Transactions":
            file: Optional[str] = popup_get_file("Save file to", save_as=True)
            if file is None:
                NotifyPopup("No file selected.").event_loop()
            else:
                Transaction.export_to_csv(Path(file).with_suffix(".csv"))

        for tab_key, tab in [
            ("-STATEMENTS TABLE-", self.statement_tab),
            ("-TRANSACTIONS TABLE-", self.transaction_tab),
            ("-ACCOUNTS TABLE-", self.account_tab),
            ("-MERCHANTS TABLE-", self.merchant_tab),
            ("-LOCATIONS TABLE-", self.location_tab),
            ("-TAGS TABLE-", self.tag_tab),
        ]:
            if event == tab_key and len(values[tab_key]) == 1:
                tab.open_edit_popup(values[tab_key][0])
