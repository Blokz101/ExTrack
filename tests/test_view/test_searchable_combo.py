"""
Tests for the SearchableCombo widget.
"""

from unittest import skipIf

from src.model.account import Account
from tests.test_model.sample_1_test_case import Sample1TestCase
from PySimpleGUI import Window
from unittest import skip
from src.view.searchable_combo import SearchableCombo
from src.view.popup import Popup
from ddt import ddt, data
from src.model.merchant import Merchant


@ddt
class TestSearchableCombo(Sample1TestCase):
    """
    Tests for the SearchableCombo widget.
    """

    def create_window(self, searchable_combo: SearchableCombo) -> None:
        self.searchable_combo: SearchableCombo = searchable_combo
        self.popup: Popup = Popup(
            "Searchable Combo Test", layout=[[self.searchable_combo]]
        )
        self.window: Window = self.popup.window

        self.popup.add_callback(self.searchable_combo.event_loop_callback)
        self.window.read(timeout=0)

    def close_window(self):
        self.popup.close()

    def test_constructor(self):
        """
        Test the constructor.
        """
        # Test searchable combo with a list and no default value
        self.create_window(SearchableCombo(Merchant.get_all()))

        self.assertEqual("", self.searchable_combo.combo_input.get())
        self.assertSqlListEqual(Merchant.get_all(), self.searchable_combo.values)
        sorted_list: list[Merchant] = Merchant.get_all()
        sorted_list.sort(key=lambda x: str(x))
        self.assertSqlListEqual(sorted_list, self.searchable_combo.display_values)
        self.assertIsNone(self.searchable_combo.selected_value)

        self.close_window()

        # Test searchable combo with a list and default value that is in the list
        self.create_window(
            SearchableCombo(Account.get_all(), default_value=Account.from_id(1))
        )

        self.assertSqlEqual(Account.from_id(1), self.searchable_combo.selected_value)

        self.close_window()

        # Test searchable combo with a list and default value that is not in the list
        with self.assertRaises(ValueError):
            SearchableCombo(Merchant.get_all(), default_value=Account.from_id(1))

    @data(1, 2, 3, 4, 5, 6, 7, 8, 9)
    def test_select_with_input(self, select_merchant_id: int):
        """
        Test the ability to select items by pressing enter while the input is focused.
        """
        select_merchant: Merchant = Merchant.from_id(select_merchant_id)

        # Test with a name that is all upper case
        self.create_window(SearchableCombo(Merchant.get_all()))

        self.searchable_combo.combo_input.update(value=select_merchant.name.upper())
        self.popup.check_event(SearchableCombo.COMBO_INPUT_KEY, {})
        self.popup.check_event(SearchableCombo.COMBO_INPUT_KEY + "ENTER", {})

        self.assertSqlEqual(select_merchant, self.searchable_combo.selected_value)

        self.close_window()

        # Test with a name that is all upper case
        self.create_window(SearchableCombo(Merchant.get_all()))

        self.searchable_combo.combo_input.update(value=select_merchant.name.lower())
        self.popup.check_event(SearchableCombo.COMBO_INPUT_KEY, {})
        self.popup.check_event(SearchableCombo.COMBO_INPUT_KEY + "ENTER", {})

        self.assertSqlEqual(select_merchant, self.searchable_combo.selected_value)

        self.close_window()

    @data(1, 2, 3, 4, 5, 6, 7, 8, 9)
    def test_select_with_listbox(self, select_merchant_id: int):
        """
        Test the ability to select items by using the listbox.
        """
        select_merchant: Merchant = Merchant.from_id(select_merchant_id)

        self.create_window(SearchableCombo(Merchant.get_all()))

        self.assertEqual("", self.searchable_combo.combo_input.get())

        self.popup.check_event(
            self.searchable_combo.combo_listbox_key,
            {self.searchable_combo.combo_listbox_key: [select_merchant]},
        )

        self.assertSqlEqual(select_merchant, self.searchable_combo.selected_value)
        self.assertEqual(select_merchant.name, self.searchable_combo.combo_input.get())

        self.close_window()

    @data(1, 2, 3, 4, 5, 6, 7, 8, 9)
    def test_select_then_edit_input(self, select_merchant_id: int):
        """
        Test selecting an item, then changing the input.
        """
        select_merchant: Merchant = Merchant.from_id(select_merchant_id)
        self.create_window(SearchableCombo(Merchant.get_all()))

        # Ensure the input is cleared and there is no selected value
        self.assertEqual("", self.searchable_combo.combo_input.get())
        self.assertIsNone(self.searchable_combo.selected_value)

        # Select a value using the listbox
        self.popup.check_event(
            self.searchable_combo.combo_listbox_key,
            {self.searchable_combo.combo_listbox_key: [select_merchant]},
        )

        # Check that the correct value is selected
        self.assertSqlEqual(select_merchant, self.searchable_combo.selected_value)

        # Update the input element
        self.searchable_combo.combo_input.update("foobar")
        self.popup.check_event(self.searchable_combo.combo_input_key, {})

        # Ensure that no element is selected
        self.assertIsNone(self.searchable_combo.selected_value)

        self.close_window()

    @skip
    def test_manual(self):
        self.create_window(SearchableCombo(Merchant.get_all()))
        self.popup.event_loop()
        self.close_window()
