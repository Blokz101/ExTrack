"""
Tests for the StatementPopup class.
"""

# mypy: ignore-errors
from PySimpleGUI import Window
from ddt import ddt, data

from src.model.account import Account
from src.model.statement import Statement
from src.view import short_date_format
from src.view.statement_popup import StatementPopup
from tests.test_model.sample_1_test_case import Sample1TestCase


@ddt
class TestStatementPopup(Sample1TestCase):
    """
    Tests for the StatementPopup class.
    """

    def test_construction_for_new_statement(self):
        """
        Tests the constructor for a new statement.
        """
        popup: StatementPopup = StatementPopup(None)
        popup_window: Window = popup.window
        _, _ = popup_window.read(timeout=0)

        # Validate basic fields and inputs
        self.assertEqual("", popup_window[StatementPopup.DATE_INPUT_KEY].get())
        self.assertEqual("", popup_window[StatementPopup.ACCOUNT_COMBO_KEY].get())
        self.assertIsNone(popup_window[StatementPopup.STARTING_BALANCE_INPUT_KEY].get())
        self.assertFalse(popup_window[StatementPopup.RECONCILED_CHECKBOX_KEY].get())
        self.assertEqual("", popup_window[StatementPopup.FILE_NAME_INPUT_KEY].get())

        self.assertFalse(popup.inputs_valid())

        popup_window.close()

    @data(1, 2, 3, 4, 5, 6)
    def test_construction_with_existing_statement(self, statement_id: int):
        """
        Tests the construction of a statement popup from an existing statement.
        """
        statement: Statement = Statement.from_id(statement_id)
        popup: StatementPopup = StatementPopup(Statement.from_id(statement_id))
        popup_window: Window = popup.window
        _, _ = popup.window.read(timeout=0)

        # Validate basic inputs
        self.assertEqual(
            statement.date.strftime(short_date_format),
            popup_window[StatementPopup.DATE_INPUT_KEY].get(),
        )
        self.assertSqlEqual(
            statement.account(),
            popup_window[StatementPopup.ACCOUNT_COMBO_KEY].get(),
        )
        self.assertEqual(
            statement.starting_balance,
            popup_window[StatementPopup.STARTING_BALANCE_INPUT_KEY].get(),
        )
        self.assertEqual(
            statement.reconciled,
            popup_window[StatementPopup.RECONCILED_CHECKBOX_KEY].get(),
        )
        self.assertEqual(
            "" if statement.file_name is None else statement.file_name,
            popup_window[StatementPopup.FILE_NAME_INPUT_KEY].get(),
        )

        self.assertTrue(popup.inputs_valid())

        popup_window.close()

    @data(1, 2, 3, 4, 5, 6)
    def test_submit_unchanged_statement(self, statement_id: int):
        """
        Tests database after opening and submitting a popup while making no edits.
        """
        expected_statements: list[Statement] = Statement.get_all()

        popup: StatementPopup = StatementPopup(Statement.from_id(statement_id))
        _, _ = popup.window.read(timeout=0)
        popup.check_event(StatementPopup.DONE_BUTTON_KEY, {})

        self.assertSqlListEqual(expected_statements, Statement.get_all())

        popup.window.close()

    def test_close_after_edits(self):
        """
        Tests making edits to the merchant popup then closing it.
        """
        expected_statements: list[Statement] = Statement.get_all()

        popup: StatementPopup = StatementPopup(Statement.from_id(6))

        # Fake user inputs
        new_date: str = "01/01/2021"
        popup.window[StatementPopup.DATE_INPUT_KEY].update(new_date)
        popup.check_event(
            StatementPopup.DATE_INPUT_KEY, {StatementPopup.DATE_INPUT_KEY: new_date}
        )

        new_account: Account = Account.from_id(1)
        popup.check_event(
            StatementPopup.ACCOUNT_COMBO_KEY,
            {StatementPopup.ACCOUNT_COMBO_KEY: new_account},
        )

        new_starting_balance: float = -3253.25
        popup.window[StatementPopup.STARTING_BALANCE_INPUT_KEY].update(
            new_starting_balance
        )
        popup.check_event(
            StatementPopup.STARTING_BALANCE_INPUT_KEY,
            {StatementPopup.STARTING_BALANCE_INPUT_KEY: new_starting_balance},
        )

        new_reconciled: bool = True
        popup.window[StatementPopup.RECONCILED_CHECKBOX_KEY].update(new_reconciled)
        popup.check_event(
            StatementPopup.RECONCILED_CHECKBOX_KEY,
            {StatementPopup.RECONCILED_CHECKBOX_KEY: new_reconciled},
        )

        new_file_name: str = "NOTDISCOVER.csv"
        popup.window[StatementPopup.FILE_NAME_INPUT_KEY].update(new_file_name)
        popup.check_event(
            StatementPopup.FILE_NAME_INPUT_KEY,
            {StatementPopup.FILE_NAME_INPUT_KEY: new_file_name},
        )

        popup.check_event("Exit", {})

        self.assertSqlListEqual(expected_statements, Statement.get_all())

        popup.window.close()

    def test_submit_edited_statement(self):
        """
        Tests editing the database with the basic input fields.
        """
        expected_statements: list[Statement] = Statement.get_all()
        expected_statements[5] = Statement(
            6,
            "2021-01-01 00:00:00",
            "NOTDISCOVER.csv",
            1,
            -3253.25,
            True,
        )

        popup: StatementPopup = StatementPopup(Statement.from_id(6))

        # Fake user inputs
        new_date: str = "01/01/2021"
        popup.window[StatementPopup.DATE_INPUT_KEY].update(new_date)
        popup.check_event(
            StatementPopup.DATE_INPUT_KEY, {StatementPopup.DATE_INPUT_KEY: new_date}
        )

        new_account: Account = Account.from_id(1)
        popup.window[StatementPopup.ACCOUNT_COMBO_KEY].update(new_account)
        popup.check_event(
            StatementPopup.ACCOUNT_COMBO_KEY,
            {StatementPopup.ACCOUNT_COMBO_KEY: new_account},
        )

        new_starting_balance: float = -3253.25
        popup.window[StatementPopup.STARTING_BALANCE_INPUT_KEY].update(
            new_starting_balance
        )
        popup.check_event(
            StatementPopup.STARTING_BALANCE_INPUT_KEY,
            {StatementPopup.STARTING_BALANCE_INPUT_KEY: new_starting_balance},
        )

        new_reconciled: bool = True
        popup.window[StatementPopup.RECONCILED_CHECKBOX_KEY].update(new_reconciled)
        popup.check_event(
            StatementPopup.RECONCILED_CHECKBOX_KEY,
            {StatementPopup.RECONCILED_CHECKBOX_KEY: new_reconciled},
        )

        new_file_name: str = "NOTDISCOVER.csv"
        popup.window[StatementPopup.FILE_NAME_INPUT_KEY].update(new_file_name)
        popup.check_event(
            StatementPopup.FILE_NAME_INPUT_KEY,
            {StatementPopup.FILE_NAME_INPUT_KEY: new_file_name},
        )

        popup.check_event(StatementPopup.DONE_BUTTON_KEY, {})

        self.assertSqlListEqual(expected_statements, Statement.get_all())

        popup.window.close()
