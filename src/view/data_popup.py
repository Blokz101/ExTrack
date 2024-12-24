"""
Contains the DataPopup class which is a base class for popups that deal with editing any SqlObjects.
"""

from abc import ABC
from abc import abstractmethod
from typing import Any, Optional

from PySimpleGUI import Element, Text, Button, Column  # type: ignore

from src.view.popup import Popup


class DataPopup(Popup, ABC):
    """
    Base class for popups that deal with editing any of the main SqlObjects.
    """

    CREATE_BUTTON_KEY: str = "-CREATE BUTTON-"
    DELETE_BUTTON_KEY: str = "-DELETE BUTTON-"
    DONE_BUTTON_KEY: str = "-DONE BUTTON-"

    def __init__(
        self,
        title: str,
        delete_supported: bool = False,
        layout_generator: Any = None,
    ) -> None:
        """
        :param title: Title of popup
        :param delete_supported: True if the delete button should be enabled, false otherwise
        :param layout_generator: Alternative layout generator to use for this popup if the default layout behavior should be overridden
        """
        self._delete_supported: bool = delete_supported
        super().__init__(title, layout_generator=layout_generator)

    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the data input popup.

        :return: Layout for this data popup
        """
        header: list[list[Element]] = [
            [
                Text(self.title),
            ],
            [
                Button("Create", key=DataPopup.CREATE_BUTTON_KEY, expand_x=True),
                Button(
                    "Delete",
                    key=DataPopup.DELETE_BUTTON_KEY,
                    expand_x=True,
                    disabled=not self._delete_supported,
                ),
            ],
        ]
        body: list[list[Element]] = [
            [Column(self._fields_generator(), expand_x=True, expand_y=True)]
        ]
        footer: list[list[Element]] = [
            [Button("Done", key=DataPopup.DONE_BUTTON_KEY, expand_x=True)],
        ]
        return header + body + footer

    @abstractmethod
    def _fields_generator(self) -> list[list[Element]]:
        """
        Generates the fields section of the layout.

        :return: Fields section of the layout
        """

    def check_event(self, event: Any, values: dict) -> None:
        """
        Executes the specified steps for each event and value.

        :param event: Event to respond to
        :param values: Values correlated with the event
        """
        super().check_event(event, values)
        self.window[DataPopup.DONE_BUTTON_KEY].update(disabled=True)

    @abstractmethod
    def inputs_valid(self) -> bool:
        """
        Checks if all inputs are valid.

        :return: True if all inputs are valid, false otherwise
        """
