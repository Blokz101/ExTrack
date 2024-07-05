"""
Contains the Popup class which is the base for all windows in the application.
"""

from abc import ABC, abstractmethod
from typing import Any

from PySimpleGUI import Window, Element, WINDOW_CLOSED, theme  # type: ignore

from src.view import gui_theme


class Popup(ABC):
    """
    Basic popup with an event loop and layout.
    """

    def __init__(self, title: str, modal: bool = True) -> None:
        theme(gui_theme)

        self.title: str = title
        """Title of popup that will be displayed as the window title."""

        self.run_event_loop: bool = True
        """
        Allows the event loop to run while set to true. Should not be set to True again after 
        this point.
        """

        self.window: Window = Window(
            self.title,
            self._layout_generator(),
            resizable=True,
            finalize=True,
            modal=modal,
        )
        """Window for this popup."""

        self._event_loop_callback: list[Any] = []
        """List of functions to call every time the event loop runs."""

    @abstractmethod
    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the window

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
                break

            self.check_event(event, values)

        self.window.close()

    @abstractmethod
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
