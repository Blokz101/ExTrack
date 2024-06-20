from abc import ABC, abstractmethod
from PySimpleGUI import Window, Element, WINDOW_CLOSED


class Popup(ABC):
    """
    Basic popup with an event loop and layout.
    """

    def __init__(self, title: str) -> None:
        self.title: str = title
        """Title of popup that will be displayed as the window title."""

        self.run_event_loop: bool = True
        """Allows the event loop to run while set to true. Should not be set to True again after this point."""

        self.window: Window = Window(
            self.title, self._layout_generator(), resizable=True
        )
        """Window for this popup."""

    @abstractmethod
    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the window

        :return: Layout for the window
        """

    def event_loop(self) -> None:
        """
        Event loop for this popup.
        Should not be called during testing, instead call check_event directly.

        :raise RuntimeError: If the popup has already been used.
        """
        if not self.run_event_loop:
            raise RuntimeError(
                "Cannot use the same popup instance twice, create a new popup instead."
            )

        while self.run_event_loop:
            event, values = self.window.read()

            if event == WINDOW_CLOSED or event == "Exit":
                self.run_event_loop = False
                break

            self.check_event(event, values)

        self.run_event_loop = False
        self.window.close()

    @abstractmethod
    def check_event(self, event: any, values: dict[any:any]) -> None:
        """
        Respond to events from the user or test.

        :param event: Event to parse
        :param values: Values related to the event
        """

    def __del__(self) -> None:
        if self.window is not None:
            self.window.close()
