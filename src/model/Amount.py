from typing import Optional

from model.Tag import Tag
from model.Transaction import Transaction
from src.model.SqlObject import SqlObject


class Amount(SqlObject):
    """
    Represents an amount of money for a transaction in the SQL database. Each transaction may have multiple amounts so
    that multiple items in one transaction may have different tags.
    """

    def __init__(
        self,
        sqlid: Optional[int],
        amount: float,
        transaction_id: int,
        description: Optional[str],
    ) -> None:
        """
        :param sqlid: ID of SQL row that this amount belongs to.
        :param amount: Amount of money this amount represents.
        :param transaction_id: Transaction this amount belongs to.
        :param description: Description of this amount.
        """
        super().__init__(sqlid)
        self.amount: float = 0.0
        self.transaction_id: int = 0
        self.description: Optional[str] = None

    def sync(self) -> None:
        """
        Syncs this amount to the database by updating the database. If the amount is not in the database it is
        added.
        """

    def transaction(self) -> Transaction:
        """
        Get the transaction that this amount belongs to.

        :return: Transaction this amount belongs to.
        """

    def tags(self) -> list[Tag]:
        """
        Gets the list of tags that this amount is tagged with.

        :return: List of tags that this amount is tagged with.
        """
