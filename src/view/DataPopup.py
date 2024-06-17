from PySimpleGUI import *
from abc import ABC
from abc import abstractmethod


class Data_Popup(ABC):

    def __init__(self, title: str, editable_widget_keys: list[str]) -> None:
        self.title: str = title
        self.editable_widget_keys: list[str] = editable_widget_keys

        self.run_event_loop: bool = True
        self.window: Window = Window(
            self.title, self._layout_generator(), resizable=True
        )

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

    def event_loop(self) -> None:
        """
        Event loop for this popup.
        """
        while self.run_event_loop:
            event, values = self.window.read()

            if event == WINDOW_CLOSED or event == "Exit":
                self.run_event_loop = False
                break

            self.check_event(event, values)

        self.window.close()

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
        if self.inputs_valid():
            self.window["-DONE BUTTON-"].update(disabled=False)
        else:
            self.window["-DONE BUTTON-"].update(disabled=True)

    @abstractmethod
    def inputs_valid(self) -> bool:
        """
        Checks if all inputs are valid.

        :return: True if all inputs are valid, false otherwise
        """
