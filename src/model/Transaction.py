from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from src.model import Account
from src.model import Amount
from src.model import Merchant
from src.model.SqlObject import SqlObject
from src.model import Statement


class Transaction(SqlObject):
    """
    Represents a transaction in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int],
        description: Optional[str],
        merchant_id: Optional[int],
        reconciled: bool,
        date: Optional[Union[str, datetime]],
        statement_id: Optional[int],
        receipt_path: Optional[str],
        account_id: Optional[int],
        transfer_trans_id: Optional[int],
    ):
        """
        :param sqlid: ID of SQL row that this transaction belongs to.
        :param description: Description of the transaction.
        :param merchant_id: ID of transaction merchant
        :param reconciled: Whether this transaction is reconciled.
        :param date: Date of transaction.
        :param statement_id: ID of statement that this transaction belongs to.
        :param receipt_path: Path to photo of receipt.
        :param account_id: ID of account that this transaction belongs to.
        :param transfer_trans_id: ID of transfer transaction that this transaction is linked to.
        """
        super().__init__(sqlid)
        self.description: Optional[str] = None
        self.reconciled: bool = False
        self.date: Optional[datetime] = None
        self.receipt_path: Optional[Path] = None
        self.merchant_id: Optional[int] = None
        self.statement_id: Optional[int] = None
        self.account_id: Optional[int] = None
        self.transfer_trans_id: Optional[int] = None
        raise NotImplementedError()

    def sync(self) -> None:
        """
        Syncs this transaction to the database by updating the database. If the transaction is not in the database it is
        added.
        """
        raise NotImplementedError()

    def merchant(self) -> Merchant.Merchant:
        """
        Gets the merchant of this transaction.

        :return: Merchant of this transaction.
        """
        raise NotImplementedError()

    def statement(self) -> Statement.Statement:
        """
        Gets the statement this transaction belongs to if it exists.

        :return: Statement this transaction belongs to.
        """
        raise NotImplementedError()

    def account(self) -> Account.Account:
        """
        Gets the account this transaction belongs to if it exists.

        :return: Account this transaction belongs to.
        """
        raise NotImplementedError()

    def transfer_trans(self) -> Transaction:
        """
        Gets the transfer transaction this transaction is linked to if it exists.

        :return: Transfer transaction this transaction is linked to.
        """
        raise NotImplementedError()

    def total_amount(self) -> float:
        """
        Gets the combined amounts of this transaction.

        :return: The combined amounts of this transaction.
        """
        raise NotImplementedError()

    def amounts(self) -> list[Amount.Amount]:
        """
        Gets the list of amounts that this transaction has.

        :return: List of amounts that this transaction has.
        """
        raise NotImplementedError()
