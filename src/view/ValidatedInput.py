from datetime import datetime
from typing import Optional

from src.view import full_date_format, short_date_format
from PySimpleGUI import Input
from abc import ABC
from abc import abstractmethod
import re


class ValidatedInput(Input, ABC):

    @abstractmethod
    def validation_status(self) -> Optional[str]:
        """
        Checks if the input is valid.

        :return: None if the input is valid or error message if the input is invalid.
        """

    def update_validation_appearance(self) -> None:
        """
        Updates the appearance of this Input based on validation_status.

        This function should be called in the main event loop of the program.
        """
        if self.validation_status() is None:
            super().update(text_color="black")
        else:
            super().update(text_color="red")


class CoordinateInput(ValidatedInput):

    valid_coordinate_pattern: str = r"-?\d{1,}\.?\d*, ?-?\d{1,}\.?\d*"

    def validation_status(self) -> Optional[str]:
        if (
            re.fullmatch(CoordinateInput.valid_coordinate_pattern, self.get()) is None
            and re.fullmatch(r"None, ?None", self.get()) is None
        ):
            return "Invalid coordinates."
        return None


class DateInput(ValidatedInput):

    def validation_status(self) -> Optional[str]:
        try:
            datetime.strptime(self.get(), full_date_format)
            return None
        except ValueError:
            pass

        try:
            datetime.strptime(self.get(), short_date_format)
            return None
        except ValueError:
            pass

        return "Invalid date."


class AmountInput(ValidatedInput):

    def validation_status(self) -> Optional[str]:
        if self.get() == "":
            return "Invalid amount."

        try:
            float(self.get())
        except ValueError:
            return "Invalid amount."
        return None
