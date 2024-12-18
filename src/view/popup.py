"""
Contains the Popup class which is the base for all windows in the application.
"""

from enum import Enum
from typing import Any, Optional

from PySimpleGUI import Window, Element, WINDOW_CLOSED, theme  # type: ignore

from src.view import gui_theme


class ClosedStatus(Enum):
    """
    Enum for the status of a popup.
    """

    OPEN: int = 0
    STANDARD: int = 1
    OPERATION_SUCCESS: int = 2
    OPERATION_CANCELED: int = 3
    UNACKNOWLEDGED: int = 4


class Popup:
    """
    Basic popup with an event loop and layout.
    """

    def __init__(
        self,
        title: str,
        modal: bool = True,
        layout: Optional[list[list[Element]]] = None,
    ) -> None:
        """
        :param title: Title of the popup, will be displayed as the window title
        :param modal: True if the popup should be modal
        :param layout: The layout of the popup if, if not specified then _layout_generator will be called to generate the layout instead.
        """
        theme(gui_theme)

        self.title: str = title
        """Title of popup that will be displayed as the window title."""

        self.run_event_loop: bool = True
        """
        Allows the event loop to run while set to true. Should not be set to True again after 
        this point.
        """

        self.closed_status: ClosedStatus = ClosedStatus.OPEN
        """Status of the popup when it is closed."""

        self.window: Window = Window(
            self.title,
            layout if layout is not None else self._layout_generator(),
            resizable=True,
            finalize=True,
            modal=modal,
        )
        """Window for this popup."""

        self._event_loop_callback: list[Any] = []
        """List of functions to call every time the event loop runs."""

    def close(self, closed_status: ClosedStatus = ClosedStatus.STANDARD) -> None:
        """
        Close the popup with a status.

        :param closed_status: Status of the close operation
        """
        self.closed_status = closed_status
        self.run_event_loop = False
        self.window.close()

    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the window. This method gets called if layout was not defined in the constructor.
        Implemented separately to separate construction code from logic code.

        :return: Layout for the window
        """

    def event_loop(self) -> None:
        """
        Event loop for this popup. Should not be called during testing, instead call check_event
        directly.

        :raise RuntimeError: If the popup has already been used.
        """
        if not self.run_event_loop:
            raise RuntimeError(
                "Cannot use the same popup instance twice, create a new popup instead."
            )

        while self.run_event_loop:
            event, values = self.window.read()

            if event in [WINDOW_CLOSED, "Exit"]:
                self.closed_status = ClosedStatus.OPERATION_CANCELED
                break

            self.check_event(event, values)

        if self.closed_status == ClosedStatus.OPEN:
            self.close(closed_status=ClosedStatus.UNACKNOWLEDGED)

    def check_event(self, event: Any, values: dict[Any, Any]) -> None:
        """
        Respond to events from the user or test.

        :param event: Event to parse
        :param values: Values related to the event
        """
        for callback in self._event_loop_callback:
            callback(event, values)

    def add_callback(self, func: Any) -> None:
        """
        Add a callback function to be run with every event loop.
        Each callback function will take parameters (event, values).

        :param func: Function to run
        """
        self._event_loop_callback.append(func)

    def __del__(self) -> None:
        if self.window is not None:
            self.window.close()
