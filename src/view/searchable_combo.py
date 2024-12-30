"""
Contains the SearchableCombo class which is a Combo element that can be filtered and searched.
"""

from typing import Any
from difflib import SequenceMatcher
from typing import Optional
from PySimpleGUI import Column, Element, Listbox, Input


class SearchableCombo(Column):

    COMBO_LISTBOX_KEY: str = "-COMBO LISTBOX-"
    COMBO_INPUT_KEY: str = "-COMBO INPUT-"
    COMBO_LISTBOX_HEIGHT: int = 4
    VALID_INPUT_TEXT_COLOR: str = "white"
    INVALID_INPUT_TEXT_COLOR: str = "red"

    def __init__(
        self,
        values: list[Any],
        default_value: Any = None,
        input_height: Optional[int] = None,
        sorting_function: Optional[Any] = None,
        key: str = "",
    ):
        """
        :param values: List of objects that are the options, each object's __str__ function is used to find their display values
        :param default_value: Object that should be selected initially
        :param input_height: Height of the input element
        :param key: Key for this element
        """
        self.values: list[Any] = values
        """
        List of values that the searchable combo displays. 
        If a list of objects is provided their __str__ function is used to find their display values.
        """
        self.listbox_height: Optional[int] = input_height
        """Height of the input element."""
        self._original_values: list[Any] = values.copy()
        """Original list of values in their original order."""
        self.display_values: list[Any] = values.copy()
        """List of values to be displayed in the listbox. Changes as the value in the Input element is changed."""
        self.selected_value: Any = None
        """Value that has been selected."""
        self.set_value(default_value)
        self._enter_bound: bool = False
        """True if the input has had the enter key bound, false otherwise."""
        self.combo_listbox_key: str = key + SearchableCombo.COMBO_LISTBOX_KEY
        """Combo Listbox key."""
        self.combo_input_key: str = key + SearchableCombo.COMBO_INPUT_KEY
        """Combo Input key."""
        self.combo_listbox: Listbox
        """Combo Listbox element."""
        self.combo_input: Input
        """Combo Input element."""

        super().__init__(
            layout=self._layout_generator(),
            key=key,
            expand_y=True,
            expand_x=True,
        )

    def _layout_generator(self) -> list[list[Element]]:
        """
        Generates the layout for the element.
        """
        self.combo_listbox = Listbox(
            values=self.display_values,
            expand_y=True,
            expand_x=True,
            enable_events=True,
            size=(1, SearchableCombo.COMBO_LISTBOX_HEIGHT),
            key=self.combo_listbox_key,
        )
        self.combo_input = Input(
            default_text=(
                None if self.selected_value is None else str(self.selected_value)
            ),
            expand_x=True,
            enable_events=True,
            key=self.combo_input_key,
        )
        return [
            [self.combo_input],
            [self.combo_listbox],
        ]

    def valid(self) -> bool:
        """
        Checks if a value is currently selected.

        :return: True if a value is currently selected, false otherwise
        """
        return self.selected_value is not None

    def set_value(self, new_value: Any) -> None:
        """
        Set the value of this element.

        :param new_value: New value to set the selected value to
        """
        if new_value is not None and new_value not in self.values:
            raise ValueError("Default value must be in values.")
        self.selected_value = new_value

    def event_loop_callback(self, event: Any, values: dict[Any, Any]) -> None:
        """
        Gets called every event loop to respond to key inputs and update the list.
        """
        # Bind the enter key to the input widget
        if not self._enter_bound:
            self._enter_bound = True
            self.combo_input.bind("<Return>", "ENTER")

        # Select the value by clicking a row in the list box
        if event == self.combo_listbox_key:
            self.selected_value = values[self.combo_listbox_key][0]
            self.combo_input.update(str(self.selected_value))

        # Select the value by clicking pressing enter while focused on the list box
        elif event == self.combo_input_key + "ENTER":
            self.selected_value = self.display_values[0]
            self.combo_input.update(str(self.selected_value))

        # If the input is updated and a value is not selected then clear the selected value
        elif event == self.combo_input_key and self.selected_value is not None:
            self.selected_value = None

        # Update the appearance
        self._update_appearance()

        # Update the listbox
        if self._being_searched():
            self.display_values.sort(
                key=lambda x: SequenceMatcher(
                    None, str(x).lower(), self.combo_input.get().lower()
                ).ratio(),
                reverse=True,
            )
        else:
            self.display_values = self._original_values.copy()

        self.combo_listbox.update(values=self.display_values)

    def _update_appearance(self) -> None:
        """
        Helper method for event_loop_callback.
        Updates the appearance of the element to reflect if a value has been selected.
        """
        if self.valid():
            self.combo_input.update(text_color=SearchableCombo.VALID_INPUT_TEXT_COLOR)

        else:
            self.combo_input.update(text_color=SearchableCombo.INVALID_INPUT_TEXT_COLOR)

    def _being_searched(self) -> bool:
        """
        Returns true if the listbox is being searched and false otherwise.
        :return: True if the list box is being searched and false otherwise
        """
        return self.combo_input.get() != "" and self.selected_value is None
