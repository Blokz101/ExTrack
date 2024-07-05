"""
Tests for the TransactionPopup class.
"""

# mypy: ignore-errors
from datetime import datetime
from typing import cast
from unittest import skip

from PySimpleGUI import Window
from ddt import ddt, data

from src.model.account import Account
from src.model.amount import Amount
from src.model.merchant import Merchant
from src.model.tag import Tag
from src.model.transaction import Transaction
from src.view import full_date_format, short_date_format
from src.view.transaction_popup import TransactionPopup
from tests.test_model.sample_1_test_case import Sample1TestCase


@ddt
class TestTransactionPopup(Sample1TestCase):
    """
    Tests for the TransactionPopup class.
    """

    def test_construction_for_new_transaction(self):
        """
        Tests the construction of a new transaction popup for a new transaction.
        """

        popup: TransactionPopup = TransactionPopup(None)
        popup_window: Window = popup.window
        _, _ = popup.window.read(timeout=0)

        # Validate basic fields and inputs
        self.assertEqual("", popup_window["-ACCOUNT SELECTOR-"].get())
        self.assertEqual("", popup_window["-DESCRIPTION INPUT-"].get())
        self.assertEqual(None, popup_window["-TOTAL AMOUNT INPUT-"].get())
        self.assertEqual("", popup_window["-MERCHANT SELECTOR-"].get())
        self.assertEqual("None, None", popup_window["-COORDINATE INPUT-"].get())
        self.assertEqual(
            datetime.now().strftime(short_date_format),
            popup_window["-DATE INPUT-"].get(),
        )
        self.assertEqual("False", popup_window["-RECONCILED TEXT-"].get())
        self.assertEqual("None", popup_window["-STATEMENT TEXT-"].get())
        self.assertEqual("None", popup_window["-TRANSFER TRANSACTION TEXT-"].get())

        # Validate amounts
        self.assertEqual([], popup.amount_rows)

        self.assertFalse(popup.inputs_valid())

    @data(1, 2, 3, 4, 5, 6)
    def test_construction_with_existing_transaction(self, trans_id: int):
        """
        Tests the construction of a transaction popup for an existing transaction.
        """
        trans: Transaction = Transaction.from_id(trans_id)
        popup: TransactionPopup = TransactionPopup(Transaction.from_id(trans_id))
        popup_window: Window = popup.window
        _, _ = popup.window.read(timeout=0)

        # Validate basic inputs
        self.assertEqual(str(trans.sqlid), popup_window["-TRANS ID TEXT-"].get())
        self.assertSqlEqual(trans.account(), popup_window["-ACCOUNT SELECTOR-"].get())
        self.assertEqual(trans.description, popup_window["-DESCRIPTION INPUT-"].get())
        self.assertEqual(
            trans.total_amount(), popup_window["-TOTAL AMOUNT INPUT-"].get()
        )
        # Test merchant differently for the case where the transaction has a merchant and the case where it does not.
        if trans.merchant_id is None:
            self.assertEqual("", popup_window["-MERCHANT SELECTOR-"].get())
        else:
            self.assertSqlEqual(
                trans.merchant(), popup_window["-MERCHANT SELECTOR-"].get()
            )
        lat: str = trans.lat if trans.lat is not None else "None"
        long: str = trans.long if trans.long is not None else "None"
        self.assertEqual(f"{lat}, {long}", popup_window["-COORDINATE INPUT-"].get())
        self.assertEqual(
            trans.date.strftime(full_date_format), popup_window["-DATE INPUT-"].get()
        )
        self.assertEqual(str(trans.reconciled), popup_window["-RECONCILED TEXT-"].get())
        self.assertEqual(
            (
                "None"
                if trans.statement_id is None
                else trans.statement().date.strftime(short_date_format)
            ),
            popup_window["-STATEMENT TEXT-"].get(),
        )

        # Validate amounts
        self.assertEqual(len(trans.amounts()), len(popup.amount_rows))

        for index, trans_amount in enumerate(trans.amounts()):
            self.assertEqual(
                "" if trans_amount.description is None else trans_amount.description,
                popup_window[("-AMOUNT ROW DESCRIPTION-", index)].get(),
            )
            self.assertEqual(
                trans_amount.amount,
                popup_window[("-AMOUNT ROW AMOUNT-", index)].get(),
            )
            # Test tags differently for the case where the amount has tags and the case where it does not.
            if len(trans_amount.tags()) == 0:
                self.assertEqual(
                    "No Tags",
                    popup_window[("-AMOUNT ROW TAG SELECTOR-", index)].get_text(),
                )
            else:
                self.assertEqual(
                    ", ".join(tag.name for tag in trans_amount.tags()),
                    popup_window[("-AMOUNT ROW TAG SELECTOR-", index)].get_text(),
                )

        popup_window.close()

    def test_create_amount_row(self):
        """
        Tests popup behavior while creating new amount rows.
        """
        popup: TransactionPopup = TransactionPopup(Transaction.from_id(4))
        popup.window.read(timeout=0)

        self.assertEqual(
            "Create New Amount ($0.0 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )

        # Create new amount when amounts rows are equal to total amount.
        popup.check_event("-NEW AMOUNT BUTTON-", {})

        self.assertEqual(3, len(popup.amount_rows))
        for row in popup.amount_rows:
            self.assertTrue(row.visible)
        self.assertEqual("", popup.window[("-AMOUNT ROW DESCRIPTION-", 2)].get())
        self.assertEqual(0.0, popup.window[("-AMOUNT ROW AMOUNT-", 2)].get())
        self.assertEqual(
            "No Tags", popup.window[("-AMOUNT ROW TAG SELECTOR-", 2)].get_text()
        )

        # Remove 4.82 from the first amount row and create a new amount
        popup.window[("-AMOUNT ROW AMOUNT-", 0)].update(value=30)
        popup.check_event(("-AMOUNT ROW AMOUNT-", 0), {})

        self.assertEqual(
            "Create New Amount ($4.82 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )

        popup.check_event("-NEW AMOUNT BUTTON-", {})

        self.assertEqual(
            "Create New Amount ($0.0 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )
        self.assertEqual(4, len(popup.amount_rows))
        for row in popup.amount_rows:
            self.assertTrue(row.visible)
        self.assertEqual("", popup.window[("-AMOUNT ROW DESCRIPTION-", 3)].get())
        self.assertEqual(4.82, popup.window[("-AMOUNT ROW AMOUNT-", 3)].get())
        self.assertEqual(
            "No Tags", popup.window[("-AMOUNT ROW TAG SELECTOR-", 3)].get_text()
        )

        # Add an extra 23.56 to the total amount and create a new amount
        popup.window["-TOTAL AMOUNT INPUT-"].update(value="71.01")
        popup.check_event("-TOTAL AMOUNT INPUT-", {})

        self.assertEqual(
            "Create New Amount ($23.56 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )

        popup.check_event("-NEW AMOUNT BUTTON-", {})

        self.assertEqual(
            "Create New Amount ($0.0 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )
        self.assertEqual(5, len(popup.amount_rows))
        for row in popup.amount_rows:
            self.assertTrue(row.visible)
        self.assertEqual("", popup.window[("-AMOUNT ROW DESCRIPTION-", 4)].get())
        self.assertEqual(23.56, popup.window[("-AMOUNT ROW AMOUNT-", 4)].get())
        self.assertEqual(
            "No Tags", popup.window[("-AMOUNT ROW TAG SELECTOR-", 4)].get_text()
        )

        # Change to total amount to gibberish and create a new amount
        popup.window["-TOTAL AMOUNT INPUT-"].update(value="this is not a float")
        popup.check_event("-TOTAL AMOUNT INPUT-", {})

        self.assertEqual(
            "Create New Amount", popup.window["-NEW AMOUNT BUTTON-"].get_text()
        )

        popup.check_event("-NEW AMOUNT BUTTON-", {})

        self.assertEqual(
            "Create New Amount", popup.window["-NEW AMOUNT BUTTON-"].get_text()
        )
        self.assertEqual(6, len(popup.amount_rows))
        for row in popup.amount_rows:
            self.assertTrue(row.visible)
        self.assertEqual("", popup.window[("-AMOUNT ROW DESCRIPTION-", 5)].get())
        self.assertEqual(None, popup.window[("-AMOUNT ROW AMOUNT-", 5)].get())
        self.assertEqual(
            "No Tags", popup.window[("-AMOUNT ROW TAG SELECTOR-", 5)].get_text()
        )

        popup.window.close()

    def test_edit_undo_submit(self):
        """
        Test a simple edit to an amount, undoing the edit, and submitting the transaction.
        """
        expected_transactions: list[Transaction] = Transaction.get_all()
        expected_amounts: list[Amount] = Amount.get_all()

        popup: TransactionPopup = TransactionPopup(Transaction.from_id(2))
        _, _ = popup.window.read(timeout=0)

        popup.window["-TOTAL AMOUNT INPUT-"].update(value="100.0")
        popup.check_event("-TOTAL AMOUNT INPUT-", {})

        popup.window["-TOTAL AMOUNT INPUT-"].update(value="1245.34")
        popup.check_event("-TOTAL AMOUNT INPUT-", {})

        self.assertTrue(popup.inputs_valid())

        popup.check_event("-DONE BUTTON-", {})

        self.assertSqlListEqual(expected_transactions, Transaction.get_all())
        self.assertSqlListEqual(expected_amounts, Amount.get_all())

        popup.window.close()

    def test_edit_amounts_scenario(self):
        """
        Tests popup behavior with the following steps:
        1. Opens transaction id = 4
        2. Set amount row 2 to have an amount of 2.36
        3. Creates a new amount
        4. Edit the new amount to have an amount of $5
        5. Deletes the new amount
        6. Creates a new amount
        """
        # Open a transaction id = 4
        popup: TransactionPopup = TransactionPopup(Transaction.from_id(4))
        popup.window.read(timeout=0)

        # Set amount row 2 to have an amount of 2.63
        popup.window[("-AMOUNT ROW AMOUNT-", 1)].update(value="2.63")
        popup.check_event("-AMOUNT ROW AMOUNT-", {})

        self.assertFalse(popup.inputs_valid())
        self.assertEqual(
            "Create New Amount ($10.0 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )

        # Create a new amount
        popup.check_event("-NEW AMOUNT BUTTON-", {})

        self.assertEqual(
            "Create New Amount ($0.0 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )
        self.assertEqual(3, len(popup.amount_rows))
        self.assertEqual("", popup.window[("-AMOUNT ROW DESCRIPTION-", 2)].get())
        self.assertEqual(10, popup.window[("-AMOUNT ROW AMOUNT-", 2)].get())
        self.assertEqual(
            "No Tags", popup.window[("-AMOUNT ROW TAG SELECTOR-", 2)].get_text()
        )
        for row in popup.amount_rows:
            self.assertTrue(row.visible)
        self.assertTrue(popup.inputs_valid())

        # Edit the new amount to have an amount of $5
        popup.window[("-AMOUNT ROW AMOUNT-", 2)].update("5")
        popup.check_event(("-AMOUNT ROW AMOUNT-", 2), {})

        self.assertEqual(
            "Create New Amount ($5.0 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )
        self.assertFalse(popup.inputs_valid())

        # Delete the new amount
        popup.check_event(("-AMOUNT ROW DELETE-", 2), {})

        self.assertEqual(
            "Create New Amount ($10.0 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )
        self.assertFalse(popup.inputs_valid())
        self.assertEqual(2, len(list(row for row in popup.amount_rows if row.visible)))
        for index, row_visible in enumerate([True, True, False]):
            self.assertEqual(row_visible, popup.window[("-AMOUNT ROW-", index)].visible)

        # Create new amount
        popup.check_event("-NEW AMOUNT BUTTON-", {})

        self.assertEqual(
            "Create New Amount ($0.0 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )
        self.assertEqual(3, len(list(row for row in popup.amount_rows if row.visible)))
        self.assertEqual("", popup.window[("-AMOUNT ROW DESCRIPTION-", 3)].get())
        self.assertEqual(10.0, popup.window[("-AMOUNT ROW AMOUNT-", 3)].get())
        self.assertEqual(
            "No Tags", popup.window[("-AMOUNT ROW TAG SELECTOR-", 3)].get_text()
        )
        for index, row_visible in enumerate([True, True, False, True]):
            self.assertEqual(row_visible, popup.window[("-AMOUNT ROW-", index)].visible)
        self.assertTrue(popup.inputs_valid())

        popup.window.close()

    @data(1, 2, 3, 4, 5, 6)
    def test_submit_unchanged_transaction(self, trans_id: int):
        """
        Tests database after opening and submitting transactions while making no edits.
        """
        expected_transactions: list[Transaction] = Transaction.get_all()
        expected_amounts: list[Amount] = Amount.get_all()

        popup: TransactionPopup = TransactionPopup(Transaction.from_id(trans_id))
        popup.window.read(timeout=0)
        popup.check_event("-DONE BUTTON-", {})

        self.assertSqlListEqual(expected_transactions, Transaction.get_all())
        self.assertSqlListEqual(expected_amounts, Amount.get_all())

        popup.window.close()

    def test_close_after_edits(self):
        """
        Tests making edits to the transaction popup and then closing it.
        """
        expected_transactions: list[Transaction] = Transaction.get_all()
        expected_amounts: list[Amount] = Amount.get_all()

        popup: TransactionPopup = TransactionPopup(Transaction.from_id(3))
        _, _ = popup.window.read(timeout=0)

        # Fake user inputs
        key: str = "-ACCOUNT SELECTOR-"
        new_account_id: int = 2
        popup.window[key].update(value=Account.from_id(new_account_id))
        popup.check_event(key, {key: Account.from_id(new_account_id)})

        key = "-DESCRIPTION INPUT-"
        new_description: str = "This is an edited transaction"
        popup.window[key].update(value=new_description)
        popup.check_event(key, {key: new_description})

        key = "-MERCHANT SELECTOR-"
        new_merchant_id: int = 1
        popup.window[key].update(value=Merchant.from_id(new_merchant_id))
        popup.check_event(key, {key: Merchant.from_id(new_merchant_id)})

        key = "-COORDINATE INPUT-"
        new_lat: float = 35.86351608517815
        new_long: float = -78.64574508597906
        popup.window[key].update(value=f"{new_lat}, {new_long}")
        popup.check_event(key, {key: f"{new_lat}, {new_long}"})

        key = "-DATE INPUT-"
        new_date: str = "07/24/2004 12:45:31"
        popup.window[key].update(value=new_date)
        popup.check_event(key, {key: new_date})

        # Edit amounts
        popup.window[("-AMOUNT ROW DESCRIPTION-", 0)].update(value="Graphics Card")
        popup.check_event(("-AMOUNT ROW DESCRIPTION-", 0), {})
        popup.window["-TOTAL AMOUNT INPUT-"].update(value="803.54")
        popup.check_event("-TOTAL AMOUNT INPUT-", {})
        popup.window[("-AMOUNT ROW AMOUNT-", 0)].update(value="803.54")
        popup.check_event(("-AMOUNT ROW AMOUNT", 0), {})
        popup.amount_rows[0].tag_list = [Tag.from_id(10), Tag.from_id(5)]
        popup.check_event(None, {})

        # Exit the popup
        popup.check_event("Exit", {})

        self.assertSqlListEqual(expected_transactions, Transaction.get_all())
        self.assertSqlListEqual(expected_amounts, Amount.get_all())

        popup.window.close()

    def test_submit_basic_input_edits(self):
        """
        Tests editing the database with the basic input fields.
        """
        popup: TransactionPopup = TransactionPopup(Transaction.from_id(3))
        _, _ = popup.window.read(timeout=0)

        # Fake user inputs
        key: str = "-ACCOUNT SELECTOR-"
        new_account_id: int = 2
        popup.window[key].update(value=Account.from_id(new_account_id))
        popup.check_event(key, {key: Account.from_id(new_account_id)})

        key = "-DESCRIPTION INPUT-"
        new_description: str = "This is an edited transaction"
        popup.window[key].update(value=new_description)
        popup.check_event(key, {key: new_description})

        key = "-MERCHANT SELECTOR-"
        new_merchant_id: int = 1
        popup.window[key].update(value=Merchant.from_id(new_merchant_id))
        popup.check_event(key, {key: Merchant.from_id(new_merchant_id)})

        key = "-COORDINATE INPUT-"
        new_lat: float = 35.86351608517815
        new_long: float = -78.64574508597906
        popup.window[key].update(value=f"{new_lat}, {new_long}")
        popup.check_event(key, {key: f"{new_lat}, {new_long}"})

        key = "-DATE INPUT-"
        new_date: str = "07/24/2004 12:45:31"
        popup.window[key].update(value=new_date)
        popup.check_event(key, {key: new_date})

        # Check changes by getting the transaction from the database again
        popup.check_event("-DONE BUTTON-", {})
        actual_trans: Transaction = Transaction.from_id(3)

        self.assertSqlEqual(Account.from_id(new_account_id), actual_trans.account())
        self.assertEqual(new_description, actual_trans.description)
        self.assertSqlEqual(Merchant.from_id(new_merchant_id), actual_trans.merchant())
        self.assertEqual(new_lat, actual_trans.lat)
        self.assertEqual(new_long, actual_trans.long)
        self.assertEqual(new_date, actual_trans.date.strftime(full_date_format))

        popup.window.close()

    def test_submit_single_amount_edit(self):
        """
        Tests editing the database by editing a single amount of a transaction.
        """
        expected_transactions: list[Transaction] = Transaction.get_all()
        expected_amounts: list[Amount] = Amount.get_all()

        trans_id: int = 3

        expected_amounts[2] = Amount(3, 803.54, trans_id, "Graphics Card")
        expected_amount_tags: list[Tag] = [Tag.from_id(10), Tag.from_id(5)]

        popup: TransactionPopup = TransactionPopup(Transaction.from_id(trans_id))
        popup.window.read(timeout=0)

        popup.window[("-AMOUNT ROW DESCRIPTION-", 0)].update(value="Graphics Card")
        popup.check_event(("-AMOUNT ROW DESCRIPTION-", 0), {})
        popup.window["-TOTAL AMOUNT INPUT-"].update(value="803.54")
        popup.check_event("-TOTAL AMOUNT INPUT-", {})
        popup.window[("-AMOUNT ROW AMOUNT-", 0)].update(value="803.54")
        popup.check_event(("-AMOUNT ROW AMOUNT", 0), {})
        popup.amount_rows[0].tag_list = [Tag.from_id(10), Tag.from_id(5)]
        popup.check_event(None, {})
        popup.check_event("-DONE BUTTON-", {})

        self.assertSqlListEqual(expected_transactions, Transaction.get_all())
        self.assertSqlListEqual(expected_amounts, Amount.get_all())
        self.assertSqlListEqual(
            expected_amount_tags, Transaction.from_id(trans_id).amounts()[0].tags()
        )

        popup.window.close()

    def test_submit_edit_multiple_amounts(self):
        """
        Tests editing the database by editing, creating, or destroying many amounts of a transaction.
        """
        expected_transactions: list[Transaction] = Transaction.get_all()
        expected_amounts: list[Amount] = Amount.get_all()

        trans_id: int = 4

        expected_amounts[3] = Amount(4, 803.21, trans_id, "Graphics Card")
        expected_amount_tags_1: list[Tag] = []
        expected_amounts.pop(4)
        expected_amounts.append(Amount(8, 4.32, trans_id, "Limit Switches"))
        expected_amount_tags_2: list[Tag] = [Tag.from_id(4), Tag.from_id(5)]

        popup: TransactionPopup = TransactionPopup(Transaction.from_id(trans_id))
        popup.window.read(timeout=0)

        # Edit first amount
        popup.window[("-AMOUNT ROW DESCRIPTION-", 0)].update(value="Graphics Card")
        popup.window[("-AMOUNT ROW AMOUNT-", 0)].update(value=803.21)
        cast(TransactionPopup.AmountRow, popup.window[("-AMOUNT ROW-", 0)]).tag_list = (
            []
        )

        # Delete the second amount
        popup.check_event(("-AMOUNT ROW DELETE-", 1), {})

        # Creat the third amount
        popup.check_event("-NEW AMOUNT BUTTON-", {})
        popup.window[("-AMOUNT ROW DESCRIPTION-", 2)].update(value="Limit Switches")
        popup.window[("-AMOUNT ROW AMOUNT-", 2)].update(value="4.32")
        cast(TransactionPopup.AmountRow, popup.window[("-AMOUNT ROW-", 2)]).tag_list = [
            Tag.from_id(4),
            Tag.from_id(5),
        ]

        # Submit popup and check database
        popup.window["-TOTAL AMOUNT INPUT-"].update(value="807.53")
        popup.check_event("-DONE BUTTON-", {})

        self.assertSqlListEqual(expected_transactions, Transaction.get_all())
        self.assertSqlListEqual(expected_amounts, Amount.get_all())
        self.assertSqlListEqual(
            expected_amount_tags_1, Transaction.from_id(trans_id).amounts()[0].tags()
        )
        self.assertSqlListEqual(
            expected_amount_tags_2, Transaction.from_id(trans_id).amounts()[1].tags()
        )

        popup.window.close()

    def test_delete_new_amount(self):
        """
        Create a new transaction, then create a new amount, then delete the new amount.
        """
        expected_transactions: list[Transaction] = Transaction.get_all()
        expected_amounts: list[Amount] = Amount.get_all()

        now: datetime = datetime.now()
        expected_transactions.append(
            Transaction(
                7,
                account_id=1,
                date=datetime(now.year, now.month, now.day, 0, 0, 0),
                reconciled=False,
            )
        )
        expected_amounts.append(Amount(8, 5.0, 7, None))
        expected_amounts.append(Amount(9, 0.91, 7, None))

        popup: TransactionPopup = TransactionPopup(None)
        _, _ = popup.window.read(timeout=0)
        popup.check_event(
            "-ACCOUNT SELECTOR-", {"-ACCOUNT SELECTOR-": Account.from_id(1)}
        )

        # Set the total amount to 0.91 and create a new amount
        popup.window["-TOTAL AMOUNT INPUT-"].update(value="0.91")
        popup.check_event("-TOTAL AMOUNT INPUT-", {})
        popup.check_event("-NEW AMOUNT BUTTON-", {})

        # Set the total amount to 5.91 and create a new amount
        popup.window["-TOTAL AMOUNT INPUT-"].update(value="5.91")
        popup.check_event("-TOTAL AMOUNT INPUT-", {})
        popup.check_event("-NEW AMOUNT BUTTON-", {})

        # Delete the first amount
        popup.check_event(("-AMOUNT ROW DELETE-", 0), {})

        # Ensure the input is not valid
        self.assertFalse(popup.inputs_valid())

        # Create a new amount and submit the popup
        popup.check_event("-NEW AMOUNT BUTTON-", {})
        popup.check_event("-DONE BUTTON-", {})

        self.assertSqlListEqual(expected_transactions, Transaction.get_all())
        self.assertSqlListEqual(expected_amounts, Amount.get_all())

        popup.window.close()

    @skip
    def test_manual(self):
        TransactionPopup(Transaction.from_id(4)).event_loop()
        # TransactionPopup(None).event_loop()
