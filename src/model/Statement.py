from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.model import Account
from src.model import Transaction
from src.model.SqlObject import SqlObject


class Statement(SqlObject):
    """
    Represents a statement in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int],
        date: str,
        path: Optional[Path],
        account_id: int,
    ) -> None:
        """
        :param sqlid: ID of SQL row that this statement belongs to.
        :param date: Start date of billing period of statement.
        :param path: Path to statement CSV.
        :param account_id: ID of account of this statement.
        """
        super().__init__(sqlid)
        self.date: str = ""
        self.path: Optional[Path] = None
        self.account_id: int = 0
        raise NotImplementedError()

    def sync(self) -> None:
        """
        Syncs this statement to the database by updating the database. If the statement is not in the database it is
        added.
        """
        raise NotImplementedError()

    def transactions(self) -> list[Transaction.Transaction]:
        """
        Gets the list of transactions in this statement.

        :return: List of transactions in this statement.
        """
        raise NotImplementedError()

    def account(self) -> Account.Account:
        """
        Gets the account this statement belongs to.

        :return: Account this statement belongs to.
        """
        raise NotImplementedError()
