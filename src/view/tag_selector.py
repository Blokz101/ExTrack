"""
Contains the TagSelector class which is a popup window that allows the user to select any number
of tags.
"""

from difflib import SequenceMatcher
from typing import Optional, Any

from PySimpleGUI import Column, Input, Listbox, Element, Text, Button, WINDOW_CLOSED  # type: ignore

from src.model.tag import Tag
from src.view.popup import Popup


class TagSelector(Popup):
    """
    Popup that allows the user to search for and select any number of tags.
    """

    def __init__(self, selected_tags: Optional[list[Tag]] = None):
        super().__init__("Tag Selector")
        self.selected_tags: list[Tag] = (
            selected_tags if selected_tags is not None else []
        )
        self._previous_tags: list[Tag] = self.selected_tags

    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the input popup.

        :return: Layout for the input popup.
        """
        search_column: Column = Column(
            [
                [Text("All Tags")],
                [
                    Input(
                        key="-TAG SEARCH-",
                        enable_events=True,
                        expand_x=True,
                        size=(24, None),
                    )
                ],
                [
                    Listbox(
                        values=[],
                        key="-TAGS LISTBOX-",
                        enable_events=True,
                        expand_x=True,
                        expand_y=True,
                    )
                ],
            ],
            expand_x=True,
            expand_y=True,
        )
        selected_column: Column = Column(
            [
                [Text("Selected Tags")],
                [
                    Listbox(
                        values=[],
                        key="-SELECTED TAGS LISTBOX-",
                        enable_events=True,
                        expand_x=True,
                        expand_y=True,
                        size=(25, None),
                    )
                ],
            ],
            expand_x=True,
            expand_y=True,
        )
        return [
            [search_column, selected_column],
            [Button("Done", key="-DONE BUTTON-", expand_x=True)],
        ]

    def event_loop(self) -> None:
        """
        Event loop for this popup. Should not be called during testing, instead call check_event
        directly.

        :raise RuntimeError: If the popup has already been used.
        """
        self.window.read(timeout=0)
        self.window["-TAG SEARCH-"].bind("<Return>", "ENTER")
        self.update_list_boxes()
        super().event_loop()

    def check_event(self, event: Any, values: dict[Any, Any]) -> None:

        if event in [WINDOW_CLOSED, "Exit"]:
            self.selected_tags = self._previous_tags
            self.run_event_loop = False
            return

        if event == "-DONE BUTTON-":
            self.run_event_loop = False
            return

        if event == "-TAG SEARCH-ENTER":
            self.selected_tags.append(
                self.window["-TAGS LISTBOX-"].get_list_values()[0]
            )

        if event == "-TAGS LISTBOX-":
            self.selected_tags.append(values["-TAGS LISTBOX-"][0])

        if event == "-SELECTED TAGS LISTBOX-":
            self.selected_tags.remove(values["-SELECTED TAGS LISTBOX-"][0])

        self.update_list_boxes()

    def update_list_boxes(self) -> None:
        """
        Updates the two list boxes based on the selected tags.
        """
        if self.window is None:
            raise RuntimeError(
                "Cannot update list boxes because there is no active popup."
            )

        non_selected_tags: list[Tag] = []
        for tag in Tag.get_all():
            if tag not in self.selected_tags:
                non_selected_tags.append(tag)

        # If the user has entered nothing in the search box sort by occasional value then name
        if self.window["-TAG SEARCH-"].get() == "":
            recurring_tags: list[Tag] = []
            occasional_tags: list[Tag] = []

            for tag in non_selected_tags:
                if tag.occasional:
                    occasional_tags.append(tag)
                else:
                    recurring_tags.append(tag)

            recurring_tags.sort(key=lambda t: t.name)  # type: ignore
            occasional_tags.sort(key=lambda t: t.name)  # type: ignore

            non_selected_tags = recurring_tags + occasional_tags

        # If the user has entered something in the search box sort by similarity to searched text
        else:
            non_selected_tags.sort(
                key=lambda t: SequenceMatcher(
                    None, t.name, self.window["-TAG SEARCH-"].get()  # type: ignore
                ).ratio(),
                reverse=True,
            )

        self.window["-SELECTED TAGS LISTBOX-"].update(values=self.selected_tags)
        self.window["-TAGS LISTBOX-"].update(values=non_selected_tags)
