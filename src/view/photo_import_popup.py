"""
Contains the PhotoImportPopup class which begins the photo import process.
"""

from pathlib import Path
from typing import Any, Optional

from PySimpleGUI import Element, Input, FolderBrowse, Listbox, Button  # type: ignore

from src.model.receipt_importer import ReceiptImporter
from src.view.popup import Popup


class PhotoImportPopup(Popup):
    """
    Popup that begins the photo import process.
    """

    BROWSE_BUTTON_KEY: str = "-BROWSE BUTTON-"
    BROWSE_INPUT_KEY: str = "-BROWSE INPUT-"
    FILES_LISTBOX_KEY: str = "-FILES LISTBOX-"
    BEGIN_BUTTON_KEY: str = "-BEGIN BUTTON-"

    previously_imported_folder: Optional[Path] = None

    def __init__(self, modal: bool = True) -> None:
        super().__init__("Import Photos", modal=modal)

    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the window

        :return: Layout for the window
        """
        return [
            [
                Input(
                    key=PhotoImportPopup.BROWSE_INPUT_KEY,
                    enable_events=True,
                    expand_x=True,
                ),
                FolderBrowse(
                    key=PhotoImportPopup.BROWSE_BUTTON_KEY,
                    target=PhotoImportPopup.BROWSE_INPUT_KEY,
                ),
            ],
            [
                Listbox(
                    [],
                    key=PhotoImportPopup.FILES_LISTBOX_KEY,
                    expand_x=True,
                    expand_y=True,
                )
            ],
            [
                Button(
                    "Begin Import", key=PhotoImportPopup.BEGIN_BUTTON_KEY, expand_x=True
                )
            ],
        ]

    def check_event(self, event: Any, values: dict[Any, Any]) -> None:
        """
        Responds to events from the user or test.

        :param event: Event to parse
        :param values: Values related to the event
        """

        folder_path: Path = Path(values[PhotoImportPopup.BROWSE_INPUT_KEY])
        if folder_path.exists() and folder_path.is_dir():

            if event == PhotoImportPopup.BROWSE_INPUT_KEY:
                self.window[PhotoImportPopup.FILES_LISTBOX_KEY].update(
                    [
                        str(path.absolute())
                        for path in ReceiptImporter.get_importable_photos(folder_path)
                    ]
                )

            if event == PhotoImportPopup.BEGIN_BUTTON_KEY:
                self.window.close()
                ReceiptImporter.batch_import(
                    ReceiptImporter.get_importable_photos(folder_path)
                )
