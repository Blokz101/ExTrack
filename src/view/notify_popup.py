"""
Contains the NotifyPopup class which is a popup that displays a message to the user.
"""

from typing import Any

from PySimpleGUI import Element, Text, Button, Push  # type: ignore

from src.view.popup import Popup
from src import view


class NotifyPopup(Popup):
    """
    Popup that displays a message to the user.
    """

    def __init__(self, message: str) -> None:
        self.message: str = message
        """Message to display to the user."""

        super().__init__("Notification")

    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the window

        :return: Layout for the window
        """
        return [
            [Text(self.message)],
            [Push(), Button("OK", key="-OK-"), Push()],
        ]

    def event_loop(self) -> None:
        """
        Event loop for this popup. Adds message to the notification message queue if in testing
        mode.
        """
        if view.testing_mode:
            if self.message not in view.notification_message_queue.queue:
                view.notification_message_queue.put(self.message)
            return

        super().event_loop()

    def check_event(self, event: str, _: dict[str, Any]) -> None:
        """
        Checks the event and handles it if necessary.

        :param event: Event that occurred
        :param _: Values of the event
        """
        if event == "-OK-":
            self.run_event_loop = False
