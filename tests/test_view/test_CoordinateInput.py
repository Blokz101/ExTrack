from unittest import TestCase
from ddt import ddt, data
from src.view.ValidatedInput import CoordinateInput
from PySimpleGUI import Window


@ddt
class TestCoordinateInput(TestCase):

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

        self.assertEqual("black", self.date_input.TextColor)
        self.assertEqual(None, self.date_input.validation_status())

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

        self.assertEqual("red", self.date_input.TextColor)
        self.assertEqual("Invalid coordinates.", self.date_input.validation_status())
