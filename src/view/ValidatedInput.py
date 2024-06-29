from datetime import datetime
from typing import Optional

from src.view import full_date_format, short_date_format
from PySimpleGUI import Input, theme_input_text_color
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

    def update_validation_appearance(self, *_) -> None:
        """
        Updates the appearance of this Input based on validation_status.

        This function should be called in the main event loop of the program.
        """
        if self.validation_status() is None:
            super().update(text_color=theme_input_text_color())
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
        if self.get() is None:
            return "Invalid amount."
        return None

    def get(self) -> Optional[float]:
        """
        Read and return the current value of this input widget if it is a float.

        :return: The current value of this input widget as a float or None if the value is not a float
        """
        try:
            return round(float(super().get()), 2)
        except ValueError:
            return None
