"""
Tests for the AccountPopup class.
"""

# mypy: ignore-errors
from PySimpleGUI import Window
from ddt import ddt, data

from src.model.account import Account
from src.view.account_popup import AccountPopup
from tests.test_model.sample_1_test_case import Sample1TestCase


@ddt
class TestAccountPopup(Sample1TestCase):
    """
    Tests for the AccountPopup class.
    """

    def test_construction_fop_new_account(self):
        """
        Tests the constructor for a new account.
        """
        popup: AccountPopup = AccountPopup(None)
        popup_window: Window = popup.window
        _, _ = popup_window.read(timeout=0)

        # Validate basic fields and inputs
        self.assertEqual("", popup_window[AccountPopup.NAME_INPUT_KEY].get())
        self.assertEqual("", popup_window[AccountPopup.AMOUNT_IDX_INPUT_KEY].get())
        self.assertEqual("", popup_window[AccountPopup.DESCRIPTION_IDX_INPUT_KEY].get())
        self.assertEqual("", popup_window[AccountPopup.DATE_IDX_INPUT_KEY].get())

        self.assertFalse(popup.inputs_valid())

        popup_window.close()

    @data(1, 2)
    def test_construction_with_existing_account(self, account_id: int):
        """
        Tests the construction of an account popup from an existing account.
        """
        account: Account = Account.from_id(account_id)
        popup: AccountPopup = AccountPopup(Account.from_id(account_id))
        popup_window: Window = popup.window
        _, _ = popup.window.read(timeout=0)

        # Validate basic inputs
        self.assertEqual(account.name, popup_window[AccountPopup.NAME_INPUT_KEY].get())
        self.assertEqual(
            str(account.amount_idx),
            popup_window[AccountPopup.AMOUNT_IDX_INPUT_KEY].get(),
        )
        self.assertEqual(
            str(account.description_idx),
            popup_window[AccountPopup.DESCRIPTION_IDX_INPUT_KEY].get(),
        )
        self.assertEqual(
            str(account.date_idx), popup_window[AccountPopup.DATE_IDX_INPUT_KEY].get()
        )

        self.assertTrue(popup.inputs_valid())

        popup_window.close()

    @data(1, 2)
    def test_submit_unchanged_account(self, account_id: int):
        """
        Tests database after opening and submitting popups while making no edits.
        """
        expected_accounts: list[Account] = Account.get_all()

        popup: AccountPopup = AccountPopup(Account.from_id(account_id))
        popup.window.read(timeout=0)
        popup.check_event(AccountPopup.DONE_BUTTON_KEY, {})

        self.assertSqlListEqual(expected_accounts, Account.get_all())

        popup.window.close()

    def test_close_after_edits(self):
        """
        Tests making edits to the account popup then closing it.
        """
        expected_accounts: list[Account] = Account.get_all()

        popup: AccountPopup = AccountPopup(Account.from_id(1))

        # Fake user inputs
        new_name: str = "New Checking"
        popup.window[AccountPopup.NAME_INPUT_KEY].update(new_name)
        popup.check_event(
            AccountPopup.NAME_INPUT_KEY, {AccountPopup.NAME_INPUT_KEY: new_name}
        )

        new_account_idx: str = "9"
        popup.window[AccountPopup.AMOUNT_IDX_INPUT_KEY].update(new_account_idx)
        popup.check_event(
            AccountPopup.AMOUNT_IDX_INPUT_KEY,
            {AccountPopup.AMOUNT_IDX_INPUT_KEY: new_account_idx},
        )

        new_description_index: str = ""
        popup.window[AccountPopup.DESCRIPTION_IDX_INPUT_KEY].update(
            new_description_index
        )
        popup.check_event(
            AccountPopup.DESCRIPTION_IDX_INPUT_KEY,
            {AccountPopup.DESCRIPTION_IDX_INPUT_KEY: new_description_index},
        )

        new_date_index: str = "4"
        popup.window[AccountPopup.DATE_IDX_INPUT_KEY].update(new_date_index)
        popup.check_event(
            AccountPopup.DATE_IDX_INPUT_KEY,
            {AccountPopup.DATE_IDX_INPUT_KEY: new_date_index},
        )

        popup.check_event("Exit", {})

        self.assertSqlListEqual(expected_accounts, Account.get_all())

        popup.window.close()

    def test_submit_edited_account(self):
        """
        Tests editing the database with the basic input fields.
        """
        expected_merchants: list[Account] = Account.get_all()
        expected_merchants[0] = Account(1, "New Checking", 9, None, 4)

        popup: AccountPopup = AccountPopup(Account.from_id(1))
        _, _ = popup.window.read(timeout=0)

        # Fake user inputs
        new_name: str = "New Checking"
        popup.window[AccountPopup.NAME_INPUT_KEY].update(new_name)
        popup.check_event(
            AccountPopup.NAME_INPUT_KEY, {AccountPopup.NAME_INPUT_KEY: new_name}
        )

        new_account_idx: str = "9"
        popup.window[AccountPopup.AMOUNT_IDX_INPUT_KEY].update(new_account_idx)
        popup.check_event(
            AccountPopup.AMOUNT_IDX_INPUT_KEY,
            {AccountPopup.AMOUNT_IDX_INPUT_KEY: new_account_idx},
        )

        new_description_index: str = ""
        popup.window[AccountPopup.DESCRIPTION_IDX_INPUT_KEY].update(
            new_description_index
        )
        popup.check_event(
            AccountPopup.DESCRIPTION_IDX_INPUT_KEY,
            {AccountPopup.DESCRIPTION_IDX_INPUT_KEY: new_description_index},
        )

        new_date_index: str = "4"
        popup.window[AccountPopup.DATE_IDX_INPUT_KEY].update(new_date_index)
        popup.check_event(
            AccountPopup.DATE_IDX_INPUT_KEY,
            {AccountPopup.DATE_IDX_INPUT_KEY: new_date_index},
        )

        popup.check_event(AccountPopup.DONE_BUTTON_KEY, {})

        self.assertSqlListEqual(expected_merchants, Account.get_all())

        popup.window.close()
