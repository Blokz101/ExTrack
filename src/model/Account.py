from typing import Optional

from model.Statement import Statement
from src.model.SqlObject import SqlObject
from src.model.Transaction import Transaction as Trans


class Account(SqlObject):
    """
    Represents an account in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int],
        name: str,
        amount_idx: Optional[int],
        description_idx: Optional[int],
        date_idx: Optional[int],
    ) -> None:
        """
        :param sqlid: ID of SQL row that this account belongs to.
        :param name: Name of account.
        :param amount_idx: Index of amount column on each statement for this account.
        :param description_idx: Index of description column on each statement for this account.
        :param date_idx: Index of date column on each statement for this account.
        """
        super().__init__(sqlid)
        self.name: str = ""
        self.amount_idx: Optional[int] = None
        self.description_idx: Optional[int] = None
        self.date_idx: Optional[int] = None

    def sync(self) -> None:
        """
        Syncs this account to the database by updating the database. If the account is not in the database it is
        added.
        """

    def transactions(self) -> list[Trans]:
        """
        Gets the list of transactions for this account.

        :return: List of transactions for this account.
        """

    def statements(self) -> list[Statement]:
        """
        Gets the list of statements that this account is linked to.

        :return: List of statements that this account is linked to.
        """
