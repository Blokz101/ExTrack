from abc import ABC, abstractmethod
from typing import Optional


class SqlObject(ABC):
    """
    Representation of a row in the SQL database.
    """

    def __init__(self, sqlid: Optional[int]) -> None:
        """
        :param sqlid: ID of the corresponding row in the SQL database.
        """
        self.sqlid: Optional[int] = sqlid

    @classmethod
    def from_id(cls, sqlid: int) -> "SqlObject":
        """
        Creates an SqlObject instance from the database.

        :param sqlid: Id of the SqlObject.
        :return: SqlObject instance.
        """

    @abstractmethod
    def sync(self) -> None:
        """
        Syncs this SqlObject to the database by updating the database. If the object is not in the database it is added.
        """

    def exists(self) -> bool:
        """
        Checks if this object exists in the database.

        :return: True if the object has a corresponding row, false otherwise.
        """
