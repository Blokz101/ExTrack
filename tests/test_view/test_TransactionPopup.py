from PySimpleGUI import Window
from ddt import ddt, data

from src.model.Merchant import Merchant
from src.model.Transaction import Transaction
from src.model.Tag import Tag
from src.model.Amount import Amount
from src.model.Account import Account
from src.view.TransactionPopup import TransactionPopup
from src.view import full_date_format
from tests.test_model.Sample1TestCase import Sample1TestCase
from unittest import skip


@ddt
class TestTransactionPopup(Sample1TestCase):

    @data(1, 2, 3, 4, 5, 6)
    def test_construction_with_existing_transaction(self, trans_id: int):
        """
        Ensures the proper fields are filled in when a popup is created from an existing transaction

        Prerequisites: all of TestTransaction
        """
        trans: Transaction = Transaction.from_id(trans_id)
        popup: TransactionPopup = TransactionPopup(trans_id)
        popup_window: Window = popup.window
        _, _ = popup.window.read(timeout=0)

        # Validate basic inputs
        self.assertEqual(str(trans.sqlid), popup_window["-TRANS ID TEXT-"].get())
        self.assertSqlEqual(trans.account(), popup_window["-ACCOUNT SELECTOR-"].get())
        self.assertEqual(trans.description, popup_window["-DESCRIPTION INPUT-"].get())
        self.assertEqual(
            str(trans.total_amount()), popup_window["-TOTAL AMOUNT INPUT-"].get()
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
                else trans.statement().date.strftime(full_date_format)
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
                str(trans_amount.amount),
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

    # TODO Test proper construction of new transaction

    def test_basic_inputs(self):
        """
        Tests the Account, Description, Merchant, Coordinate, and Date inputs.

        Perquisites: test_construction_with_existing_transaction
        """
        popup: TransactionPopup = TransactionPopup(3)
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

    def test_edit_single_amount(self):
        """
        Tests a valid transaction by editing a single amount.
        """
        expected_transactions: list[Transaction] = Transaction.get_all()
        expected_amounts: list[Amount] = Amount.get_all()

        edited_expected_amount: Amount = expected_amounts[2]
        edited_expected_amount.description = "Graphics Card"
        edited_expected_amount.amount = 803.54
        edited_expected_amount.set_tags([10, 5])

        popup: TransactionPopup = TransactionPopup(3)
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

        popup.window.close()

    def test_create_amount_row(self):
        """
        Tests creating new amount rows with varying total amounts and other amount rows.
        """
        popup: TransactionPopup = TransactionPopup(4)
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
        self.assertEqual("0.0", popup.window[("-AMOUNT ROW AMOUNT-", 2)].get())
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
        self.assertEqual("4.82", popup.window[("-AMOUNT ROW AMOUNT-", 3)].get())
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
        self.assertEqual("23.56", popup.window[("-AMOUNT ROW AMOUNT-", 4)].get())
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
        self.assertEqual("", popup.window[("-AMOUNT ROW AMOUNT-", 5)].get())
        self.assertEqual(
            "No Tags", popup.window[("-AMOUNT ROW TAG SELECTOR-", 5)].get_text()
        )

        popup.window.close()

    def test_edit_amounts_scenario(self):
        """
        Tests a scenario with the following steps:
        1. Opens transaction id = 4
        2. Set amount row 2 to have an amount of 2.36
        3. Creates a new amount
        4. Edit the new amount to have an amount of $5
        5. Deletes the new amount
        6. Creates a new amount
        """
        # Open a transaction id = 4
        popup: TransactionPopup = TransactionPopup(4)
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
        self.assertEqual("10.0", popup.window[("-AMOUNT ROW AMOUNT-", 2)].get())
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
        self.assertEqual(2, len(popup.amount_rows))
        for index, row_visible in enumerate([True, True, False]):
            self.assertEqual(row_visible, popup.window[("-AMOUNT ROW-", index)].visible)

        # Create new amount
        popup.check_event("-NEW AMOUNT BUTTON-", {})

        self.assertEqual(
            "Create New Amount ($0.0 left)",
            popup.window["-NEW AMOUNT BUTTON-"].get_text(),
        )
        self.assertEqual(3, len(popup.amount_rows))
        self.assertEqual("", popup.window[("-AMOUNT ROW DESCRIPTION-", 3)].get())
        self.assertEqual("10.0", popup.window[("-AMOUNT ROW AMOUNT-", 3)].get())
        self.assertEqual(
            "No Tags", popup.window[("-AMOUNT ROW TAG SELECTOR-", 3)].get_text()
        )
        for index, row_visible in enumerate([True, True, False, True]):
            self.assertEqual(row_visible, popup.window[("-AMOUNT ROW-", index)].visible)
        self.assertTrue(popup.inputs_valid())

        popup.window.close()

    # TODO Test deleting amounts and redistributing the lost amount row to make the popup submittable

    @data(1, 2, 3, 4, 5, 6)
    def test_submit_unchanged_transaction(self, trans_id: int):
        """
        Tests opening a transaction popup and clicking done without changing anything.

        Prerequisite: test_construction_with_existing_transaction
        """
        expected_transactions: list[Transaction] = Transaction.get_all()
        expected_amounts: list[Amount] = Amount.get_all()

        popup: TransactionPopup = TransactionPopup(trans_id)
        popup.window.read(timeout=0)
        popup.check_event("-DONE BUTTON-", {})

        self.assertSqlListEqual(expected_transactions, Transaction.get_all())
        self.assertSqlListEqual(expected_amounts, Amount.get_all())

        popup.window.close()

    # TODO Test more then required decimal places for any amount input

    # TODO Test ability to submit transaction while setting amounts, then deleting amounts, then changing total amount

    # TODO Test user inputs in combo box

    @skip
    def test_manual(self):
        TransactionPopup(4).event_loop()
