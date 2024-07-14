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

    @data(
        "23.46, 89654.34",
        "3245.436,5432.3245",
        "-84932.43875, 2384.2345",
        "-3245543,-2345.2340",
        "324, -324.543",
    )
    def test_valid_coords(self, coords: str):
        """
        Tests valid coordinates.
        """

        # Setup
        self.coords_input: CoordinateInput = CoordinateInput()
        self.window = Window("test", layout=[[self.coords_input]])
        self.window.read(timeout=0)

        # Update coords and test result
        self.coords_input.update(value=coords)
        self.coords_input.update_validation_appearance()

        self.assertIsNone(self.coords_input.validation_status())
        self.assertEqual(theme_input_text_color(), self.coords_input.TextColor)

        # Close window
        self.window.close()

    def test_no_coords(self):
        """
        Tests no coordinates.
        """

        # Setup with allow no inputs set to True
        self.coords_input: CoordinateInput = CoordinateInput(allow_no_input=True)
        self.window = Window("test", layout=[[self.coords_input]])
        self.window.read(timeout=0)

        # Update coords and test result
        self.coords_input.update(value="None, None")
        self.coords_input.update_validation_appearance()

        self.assertIsNone(self.coords_input.validation_status())
        self.assertEqual(theme_input_text_color(), self.coords_input.TextColor)

        # Close window
        self.window.close()

        # Setup with allow no inputs set to false
        self.coords_input: CoordinateInput = CoordinateInput(allow_no_input=False)
        self.window = Window("test", layout=[[self.coords_input]])
        self.window.read(timeout=0)

        # Update coords and test result
        self.coords_input.update(value="None, None")
        self.coords_input.update_validation_appearance()

        self.assertEqual("Invalid coordinates.", self.coords_input.validation_status())
        self.assertEqual("red", self.coords_input.TextColor)

        # Close window
        self.window.close()

    @data(
        "",
        "(23.46, 89654.34",
        "3245.436,5432.3245)",
        "-, 2384.2345",
        "-3245543 -2345.2340",
        "Nne, None",
        "None None",
    )
    def test_invalid_coords(self, coords: str):
        """
        Tests invalid coordinates.
        """

        # Setup
        self.coords_input: CoordinateInput = CoordinateInput()
        self.window = Window("test", layout=[[self.coords_input]])
        self.window.read(timeout=0)

        # Update coords and test result
        self.coords_input.update(value=coords)
        self.coords_input.update_validation_appearance()

        self.assertEqual("Invalid coordinates.", self.coords_input.validation_status())
        self.assertEqual("red", self.coords_input.TextColor)

        # Close window
        self.window.close()
