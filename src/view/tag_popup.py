"""
Contains the TagPopup class which allows the user to create or edit a tag.
"""

from __future__ import annotations

from typing import Optional, cast, Any

from PySimpleGUI import Element, Text, Checkbox, Input  # type: ignore

from src.model.tag import Tag
from src.view.data_popup import DataPopup
from src.view.validated_input import ValidatedInput, NonNoneInput


class TagPopup(DataPopup):
    """
    Popup that allows the user to create or edit a tag.
    """

    TAG_ID_TEXT_KEY: str = "-TAG ID TEXT-"
    NAME_INPUT_KEY: str = "-NAME INPUT-"
    OCCASIONAL_CHECKBOX_KEY: str = "-OCCASIONAL CHECKBOX-"
    RULE_INPUT_KEY: str = "-RULE INPUT-"

    def __init__(self, tag: Optional[Tag]) -> None:
        self.tag: Tag
        if tag is not None:
            self.tag = tag
        else:
            self.tag = Tag(occasional=False)

        super().__init__(
            f"Tag ID = {"New" if self.tag.sqlid is None else self.tag.sqlid}"
        )

        self.window.read(timeout=0)

        self.validated_input_keys: list[str] = [TagPopup.NAME_INPUT_KEY]
        """
        Input widget that extends ValidatedInput. Their validation functions must be called each 
        event loop.
        """

        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            self.add_callback(validated_input.update_validation_appearance)

        self.window[TagPopup.DONE_BUTTON_KEY].update(disabled=not self.inputs_valid())

    def _fields_generator(self) -> list[list[Element]]:
        labels: list[Element] = [
            Text(str_label, size=(15, None))
            for str_label in ["Tag ID", "Name", "Occasional", "Rule"]
        ]

        fields: list[Element] = [
            Text(self.tag.sqlid, key=TagPopup.TAG_ID_TEXT_KEY),
            NonNoneInput(
                "" if self.tag.name is None else self.tag.name,
                key=TagPopup.NAME_INPUT_KEY,
            ),
            Checkbox(
                "",
                default=self.tag.occasional,
                key=TagPopup.OCCASIONAL_CHECKBOX_KEY,
            ),
            Input(
                "" if self.tag.rule is None else self.tag.rule,
                key=TagPopup.RULE_INPUT_KEY,
            ),
        ]

        return [list(row) for row in zip(labels, fields)]

    def check_event(self, event: Any, values: dict) -> None:
        """
        Responds to events from the user.

        :param event: Event to parse
        :param values: Values related to the event
        """
        super().check_event(event, values)

        if event == TagPopup.CREATE_BUTTON_KEY:
            self.run_event_loop = False
            self.window.close()
            TagPopup(None).event_loop()
            return

        if event == TagPopup.DONE_BUTTON_KEY:

            if not self.inputs_valid():
                raise RuntimeError("Cannot submit tag while inputs are not valid.")

            # Update Tag fields
            self.tag.name = self.window[TagPopup.NAME_INPUT_KEY].get()
            self.tag.occasional = self.window[TagPopup.OCCASIONAL_CHECKBOX_KEY].get()
            self.tag.rule = (
                None
                if self.window[TagPopup.RULE_INPUT_KEY].get() == ""
                else self.window[TagPopup.RULE_INPUT_KEY].get()
            )

            # Sync Tag
            self.tag.sync()

            self.run_event_loop = False

        # Update done button to be enabled/disabled bas on input validity
        self.window[TagPopup.DONE_BUTTON_KEY].update(disabled=not self.inputs_valid())

    def inputs_valid(self) -> bool:
        """
        Checks if all inputs are valid.

        :return: True if all inputs are valid, False otherwise
        """
        for key in self.validated_input_keys:
            validated_input: ValidatedInput = cast(ValidatedInput, self.window[key])
            if validated_input.validation_status() is not None:
                return False

        return True
