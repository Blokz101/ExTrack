from PySimpleGUI import *
from abc import ABC
from abc import abstractmethod
from src.view.Popup import Popup


class DataPopup(Popup, ABC):
    """
    Base class for popups that deal with editing any of the main SqlObjects.
    """

    def __init__(self, title: str, editable_widget_keys: list[str]) -> None:
        super().__init__(title)
        self.editable_widget_keys: list[str] = editable_widget_keys

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
                Button("Create", key="-CREATE BUTTON-", expand_x=True),
                Button("Delete", key="-DELETE BUTTON-", expand_x=True),
            ],
        ]
        body: list[list[Element]] = [
            [Column(self._fields_generator(), expand_x=True, expand_y=True)]
        ]
        footer: list[list[Element]] = [
            [Button("Done", key="-DONE BUTTON-", expand_x=True)],
        ]
        return header + body + footer

    @abstractmethod
    def _fields_generator(self) -> list[list[Element]]:
        """
        Generates the fields section of the layout.

        :return: Fields section of the layout
        """

    def check_event(self, event: any, values: dict) -> None:
        """
        Executes the specified steps for each event and value.

        :param event: Event to respond to
        :param values: Values correlated with the event
        """
        super().check_event(event, values)
        self.window["-DONE BUTTON-"].update(disabled=True)

    @abstractmethod
    def inputs_valid(self) -> bool:
        """
        Checks if all inputs are valid.

        :return: True if all inputs are valid, false otherwise
        """
