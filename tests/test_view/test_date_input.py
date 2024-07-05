"""
Tests the DateInput class.
"""

# mypy: ignore-errors
from unittest import TestCase

from PySimpleGUI import Window, theme_input_text_color
from ddt import ddt, data

from src.view.validated_input import DateInput


@ddt
class TestDateInput(TestCase):
    """
    Tests the DateInput class.
    """

    def setUp(self):
        self.date_input: DateInput = DateInput()
        self.window = Window("test", layout=[[self.date_input]])
        self.window.read(timeout=0)

    def tearDown(self):
        self.window.close()

    @data(
        "3/22/2024 20:48:36",
        "3/1/2025 14:38:50",
        "6/2/1943",
        "2/1/2029",
        "7/29/1901 09:38:11",
    )
    def test_valid_dates(self, date: str):
        self.date_input.update(value=date)
        self.date_input.update_validation_appearance()

        self.assertIsNone(self.date_input.validation_status())
        self.assertEqual(theme_input_text_color(), self.date_input.TextColor)

    @data("", "234kkdab", "6/2/1985 20:13:3a", "2092/2/1 ", "09:38:11", "03/22 20:4")
    def test_invalid_dates(self, date: str):
        self.date_input.update(value=date)
        self.date_input.update_validation_appearance()

        self.assertEqual("Invalid date.", self.date_input.validation_status())
        self.assertEqual("red", self.date_input.TextColor)
