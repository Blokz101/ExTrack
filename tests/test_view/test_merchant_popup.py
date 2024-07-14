"""
Tests for the MerchantPopup class.
"""

# mypy: ignore-errors
from PySimpleGUI import Window
from ddt import ddt, data

from src.model.merchant import Merchant
from src.view.merchant_popup import MerchantPopup
from tests.test_model.sample_1_test_case import Sample1TestCase


@ddt
class TestMerchantPopup(Sample1TestCase):
    """
    Tests for the MerchantPopup class.
    """

    def test_construction_for_new_merchant(self):
        """
        Tests the constructor for a new merchant.
        """
        popup: MerchantPopup = MerchantPopup(None)
        popup_window: Window = popup.window
        _, _ = popup_window.read(timeout=0)

        # Validate basic fields and inputs
        self.assertEqual("", popup_window[MerchantPopup.NAME_INPUT_KEY].get())
        self.assertFalse(popup_window[MerchantPopup.ONLINE_CHECKBOX_KEY].get())
        self.assertEqual("", popup_window[MerchantPopup.RULE_INPUT_KEY].get())

        self.assertFalse(popup.inputs_valid())

        popup_window.close()

    @data(1, 2, 3, 4, 5, 6, 7, 8, 9)
    def test_construction_with_existing_merchant(self, merchant_id: int):
        """
        Tests the construction of a merchant popup from an existing merchant.
        """
        merchant: Merchant = Merchant.from_id(merchant_id)
        popup: MerchantPopup = MerchantPopup(Merchant.from_id(merchant_id))
        popup_window: Window = popup.window
        _, _ = popup.window.read(timeout=0)

        # Validate basic inputs
        self.assertEqual(
            merchant.name, popup_window[MerchantPopup.NAME_INPUT_KEY].get()
        )
        self.assertEqual(
            merchant.online, popup_window[MerchantPopup.ONLINE_CHECKBOX_KEY].get()
        )
        self.assertEqual(
            "" if merchant.rule is None else merchant.rule,
            popup_window[MerchantPopup.RULE_INPUT_KEY].get(),
        )

        self.assertTrue(popup.inputs_valid())

        popup_window.close()

    @data(1, 2, 3, 4, 5, 6, 7, 8, 9)
    def test_submit_unchanged_merchant(self, merchant_id: int):
        """
        Tests database after opening and submitting popup while making no edits.
        """
        expected_merchants: list[Merchant] = Merchant.get_all()

        popup: MerchantPopup = MerchantPopup(Merchant.from_id(merchant_id))
        _, _ = popup.window.read(timeout=0)
        popup.check_event(MerchantPopup.DONE_BUTTON_KEY, {})

        self.assertSqlListEqual(expected_merchants, Merchant.get_all())

        popup.window.close()

    def test_close_after_edits(self):
        """
        Tests making edits to the merchant popup then closing it.
        """
        expected_merchants: list[Merchant] = Merchant.get_all()

        popup: MerchantPopup = MerchantPopup(Merchant.from_id(4))

        # Fake user inputs
        new_name: str = "Android"
        popup.window[MerchantPopup.NAME_INPUT_KEY].update(new_name)
        popup.check_event(
            MerchantPopup.NAME_INPUT_KEY, {MerchantPopup.NAME_INPUT_KEY: new_name}
        )

        new_online_status: bool = False
        popup.window[MerchantPopup.ONLINE_CHECKBOX_KEY].update(new_online_status)
        popup.check_event(
            MerchantPopup.ONLINE_CHECKBOX_KEY,
            {MerchantPopup.ONLINE_CHECKBOX_KEY: new_online_status},
        )

        new_rule: str = "ANDROID STORE"
        popup.window[MerchantPopup.RULE_INPUT_KEY].update(new_rule)
        popup.check_event(
            MerchantPopup.RULE_INPUT_KEY, {MerchantPopup.RULE_INPUT_KEY: new_rule}
        )

        popup.check_event("Exit", {})

        self.assertSqlListEqual(expected_merchants, Merchant.get_all())

        popup.window.close()

    def test_submit_edited_merchant(self):
        """
        Tests editing the database with the basic input fields.
        """
        expected_merchants: list[Merchant] = Merchant.get_all()
        expected_merchants[6] = Merchant(
            7, "Online Dollar Tree", True, "DOLLAR TREE ONLINE"
        )

        popup: MerchantPopup = MerchantPopup(Merchant.from_id(7))
        _, _ = popup.window.read(timeout=0)

        # Fake user inputs
        popup.window[MerchantPopup.NAME_INPUT_KEY].update(value="Online Dollar Tree")
        popup.check_event(
            MerchantPopup.NAME_INPUT_KEY,
            {MerchantPopup.NAME_INPUT_KEY: "Online Dollar Tree"},
        )

        popup.window[MerchantPopup.ONLINE_CHECKBOX_KEY].update(value=True)
        popup.check_event(
            MerchantPopup.ONLINE_CHECKBOX_KEY,
            {MerchantPopup.ONLINE_CHECKBOX_KEY: True},
        )

        popup.window[MerchantPopup.RULE_INPUT_KEY].update(value="DOLLAR TREE ONLINE")
        popup.check_event(
            MerchantPopup.RULE_INPUT_KEY,
            {MerchantPopup.RULE_INPUT_KEY: "DOLLAR TREE ONLINE"},
        )

        popup.check_event(MerchantPopup.DONE_BUTTON_KEY, {})

        self.assertSqlListEqual(expected_merchants, Merchant.get_all())

        popup.window.close()
