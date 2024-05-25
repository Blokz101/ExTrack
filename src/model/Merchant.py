from typing import Optional

from model.Location import Location
from model.Tag import Tag
from model.Transaction import Transaction
from src.model.SqlObject import SqlObject


class Merchant(SqlObject):
    """
    Represents a merchant in the SQL database.
    """

    def __init__(
        self,
        sqlite: Optional[int],
        name: str,
        online: bool,
        rule: Optional[str],
        sqlid: Optional[int],
    ) -> None:
        """
        :param sqlite: ID of SQL row that this merchant belongs to.
        :param name: Name of the merchant.
        :param online: True if the merchant has no physical locations, false if otherwise.
        :param rule: RegEx string used to identify transactions made at this merchant.
        """
        super().__init__(sqlid)
        self.name: str = ""
        self.online: bool = False
        self.rule: Optional[str] = None

    def sync(self) -> None:
        """
        Syncs this merchant to the database by updating the database. If the merchant is not in the database it is
        added.
        """

    def transactions(self) -> list[Transaction]:
        """
        Gets the list of transactions made at this merchant.

        :return: List of transactions made at this merchant.
        """

    def locations(self) -> list[Location]:
        """
        Gets a list of physical locations this merchant has.

        :return: List of physical locations this merchant has.
        """

    def default_tags(self) -> list[Tag]:
        """
        List of tags a transaction made with this merchant get by default.

        :return: List of default tags.
        """
