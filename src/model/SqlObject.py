from __future__ import annotations

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
        """ID of the corresponding row in the SQL database."""

    @classmethod
    @abstractmethod
    def from_id(cls, sqlid: int) -> SqlObject:
        """
        Creates an SqlObject instance from the database.

        :param sqlid: ID of the SqlObject.
        :return: SqlObject instance.
        """
        raise NotImplementedError()

    @abstractmethod
    def sync(self) -> None:
        """
        Syncs this SqlObject to the database by updating the database. If the object is not in the database it is added.
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_all() -> list[SqlObject]:
        """
        Gets a list of SqlObjects from all rows in the database.

        :return: List of SqlObjects from all rows in the database.
        """
        raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other) -> bool:
        """
        Checks if this object is equal to other object.

        Two SqlObjects are equal if all their fields excluding ID are equal.

        :param other: Object to compare this object to.
        :return: True if the objects are equal, false if otherwise.
        """

    def exists(self) -> bool:
        """
        Checks if this object exists in the database.

        :return: True if the object has a corresponding row, false otherwise.
        """
        return self.sqlid is not None
