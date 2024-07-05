"""
Tests the CoordinateInput class.
"""

# mypy: ignore-errors
from unittest import TestCase

from PySimpleGUI import Window, theme_input_text_color
from ddt import ddt, data

from src.view.validated_input import CoordinateInput


@ddt
class TestCoordinateInput(TestCase):
    """
    Tests the CoordinateInput class.
    """

    def setUp(self):
        self.date_input: CoordinateInput = CoordinateInput()
        self.window = Window("test", layout=[[self.date_input]])
        self.window.read(timeout=0)

    def tearDown(self):
        self.window.close()

    @data(
        "23.46, 89654.34",
        "3245.436,5432.3245",
        "-84932.43875, 2384.2345",
        "-3245543,-2345.2340",
        "324, -324.543",
        "None, None",
        "None,None",
    )
    def test_valid_dates(self, date: str):
        self.date_input.update(value=date)
        self.date_input.update_validation_appearance()

        self.assertIsNone(self.date_input.validation_status())
        self.assertEqual(theme_input_text_color(), self.date_input.TextColor)

    @data(
        "",
        "(23.46, 89654.34",
        "3245.436,5432.3245)",
        "-, 2384.2345",
        "-3245543 -2345.2340",
        "Nne, None",
        "None None",
    )
    def test_invalid_dates(self, date: str):
        self.date_input.update(value=date)
        self.date_input.update_validation_appearance()

        self.assertEqual("Invalid coordinates.", self.date_input.validation_status())
        self.assertEqual("red", self.date_input.TextColor)
