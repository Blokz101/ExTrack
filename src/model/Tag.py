from __future__ import annotations

from typing import Optional

from src.model import Amount
from src.model import Merchant
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
        raise NotImplementedError()

    def sync(self) -> None:
        """
        Syncs this tag to the database by updating the database. If the tag is not in the database it is
        added.
        """
        raise NotImplementedError()

    def default_merchants(self) -> list[Merchant.Merchant]:
        """
        Gets the list of merchants for which this is a default tag.

        :return: List of merchants for which this is a default tag.
        """
        raise NotImplementedError()

    def amounts(self) -> list[Amount.Amount]:
        """
        Gets the list of amounts tagged with this tag.

        :return: List of amounts tagged with this tag.
        """
        raise NotImplementedError()
