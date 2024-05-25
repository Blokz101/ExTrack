from typing import Optional

from model.Amount import Amount
from model.Merchant import Merchant
from src.model.SqlObject import SqlObject


class Tag(SqlObject):
    """
    Represents a tag in the SQL database.
    """

    def __init__(self, sqlid: Optional[int], name: str, occasional: bool) -> None:
        """
        :param sqlid: ID of the SQL row this tag belongs to.
        :param name: Name of the tag.
        :param occasional: True if this tag will not have long term use, false if otherwise.
        """
        super().__init__(sqlid)
        self.name: str = ""
        self.occasional: bool = False

    def sync(self) -> None:
        """
        Syncs this tag to the database by updating the database. If the tag is not in the database it is
        added.
        """

    def default_merchants(self) -> list[Merchant]:
        """
        Gets the list of merchants for which this is a default tag.

        :return: List of merchants for which this is a default tag.
        """

    def amounts(self) -> list[Amount]:
        """
        Gets the list of amounts tagged with this tag.

        :return: List of amounts tagged with this tag.
        """
