from pathlib import Path
from typing import Optional

from model.Account import Account
from model.Transaction import Transaction
from src.model.SqlObject import SqlObject


class Statement(SqlObject):
    """
    Represents a statement in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int],
        description: Optional[str],
        path: Optional[Path],
        account_id: int,
    ) -> None:
        """
        :param sqlid: ID of SQL row that this statement belongs to.
        :param description: Description of statement.
        :param path: Path to statement CSV.
        :param account_id: ID of account of this statement.
        """
        super().__init__(sqlid)
        self.description: Optional[str] = None
        self.path: Optional[Path] = None
        self.account_id: int = 0

    def sync(self) -> None:
        """
        Syncs this statement to the database by updating the database. If the statement is not in the database it is
        added.
        """

    def transactions(self) -> list[Transaction]:
        """
        Gets the list of transactions in this statement.

        :return: List of transactions in this statement.
        """

    def account(self) -> Account:
        """
        Gets the account this statement belongs to.

        :return: Account this statement belongs to.
        """
