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

    selected_folder: Optional[Path] = None

    def __init__(self, modal: bool = True) -> None:
        super().__init__("Import Photos", modal=modal)
        self._select_folder(PhotoImportPopup.selected_folder)

    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the window

        :return: Layout for the window
        """
        return [
            [
                Input(
                    default_text=(
                        ""
                        if PhotoImportPopup.selected_folder is None
                        else str(PhotoImportPopup.selected_folder.absolute())
                    ),
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
                    size=(50, 20),
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

        if event == PhotoImportPopup.BROWSE_INPUT_KEY:
            self._select_folder(Path(values[PhotoImportPopup.BROWSE_INPUT_KEY]))

        if event == PhotoImportPopup.BEGIN_BUTTON_KEY:
            self.window.close()
            if PhotoImportPopup.selected_folder is not None:
                ReceiptImporter.batch_import(
                    ReceiptImporter.get_importable_photos(
                        PhotoImportPopup.selected_folder
                    )
                )

    def _select_folder(self, folder_path: Optional[Path]) -> None:
        """
        Selects a folder for import.

        :param folder_path: Path to the folder
        """
        if folder_path is None or not folder_path.exists() or not folder_path.is_dir():
            return

        self.window[PhotoImportPopup.FILES_LISTBOX_KEY].update(
            [
                str(path.absolute())
                for path in ReceiptImporter.get_importable_photos(folder_path)
            ]
        )
        PhotoImportPopup.selected_folder = folder_path
