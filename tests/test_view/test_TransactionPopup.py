from src.model.Merchant import Merchant
from src.model.Transaction import Transaction
from src.model.Account import Account
from src.view.TransactionPopup import TransactionPopup
from src.view import full_date_format
from tests.test_model.Sample1TestCase import Sample1TestCase
from unittest import skip


class TestTransactionPopup(Sample1TestCase):

    def test_basic_inputs(self):
        """
        Tests the Account, Description, Merchant, Coordinate, and Date inputs.

        Perquisites: None
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

    def test_manual(self):
        TransactionPopup(4).event_loop()
