from PySimpleGUI import Window

from src.model.Merchant import Merchant
from src.model.Transaction import Transaction
from src.model.Amount import Amount
from src.model.Account import Account
from src.view.TransactionPopup import TransactionPopup
from src.view import full_date_format
from tests.test_model.Sample1TestCase import Sample1TestCase
from unittest import skip


class TestTransactionPopup(Sample1TestCase):

    def test_construction_with_existing_transaction_3(self):
        """
        Ensures the proper fields are filled in when a popup is created from existing transaction 3

        Prerequisites: TestTransaction.test_from_id
        """
        trans: Transaction = Transaction.from_id(3)
        popup: TransactionPopup = TransactionPopup(3)
        popup_window: Window = popup.window
        _, _ = popup.window.read(timeout=0)

        # Validate basic inputs
        self.assertEqual(str(trans.sqlid), popup_window["-TRANS ID TEXT-"].get())
        self.assertSqlEqual(trans.account(), popup_window["-ACCOUNT SELECTOR-"].get())
        self.assertEqual(trans.description, popup_window["-DESCRIPTION INPUT-"].get())
        self.assertEqual(
            str(trans.total_amount()), popup_window["-TOTAL AMOUNT INPUT-"].get()
        )
        self.assertSqlEqual(trans.merchant(), popup_window["-MERCHANT SELECTOR-"].get())
        lat: str = trans.lat if trans.lat is not None else "None"
        long: str = trans.long if trans.long is not None else "None"
        self.assertEqual(f"{lat}, {long}", popup_window["-COORDINATE INPUT-"].get())
        self.assertEqual(
            trans.date.strftime(full_date_format), popup_window["-DATE INPUT-"].get()
        )
        self.assertEqual(str(trans.reconciled), popup_window["-RECONCILED TEXT-"].get())
        self.assertEqual(
            trans.statement().date.strftime(full_date_format),
            popup_window["-STATEMENT TEXT-"].get(),
        )

        # Validate amounts
        self.assertEqual(1, len(popup.amount_rows))

        trans_amount: Amount = trans.amounts()[0]
        self.assertEqual(
            "" if trans_amount.description is None else trans_amount.description,
            popup_window[("-AMOUNT ROW DESCRIPTION-", 0)].get(),
        )
        self.assertEqual(
            str(trans_amount.amount), popup_window[("-AMOUNT ROW AMOUNT-", 0)].get()
        )
        self.assertEqual(
            ",".join(tag.name for tag in trans_amount.tags()),
            popup_window[("-AMOUNT ROW TAG SELECTOR-", 0)].get_text(),
        )

    # TODO Test proper construction of new transaction

    def test_basic_inputs(self):
        """
        Tests the Account, Description, Merchant, Coordinate, and Date inputs.

        Perquisites: test_construction_with_existing_transaction_3
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

    # TODO Test correct amount use with one amount and too many decimal places
    def test_single_amount(self):
        """
        Tests a valid transaction with a single amount.
        :return:
        """

    # TODO Text correct amount use with many amounts and too many decimal places

    # TODO Test incorrect amounts and ensure done button cant be pressed

    # TODO Test setting amounts, then deleting amounts, then changing total amount

    # TODO Test user inputs in combo box

    @skip
    def test_manual(self):
        TransactionPopup(4).event_loop()
