from typing import Optional

from model.Merchant import Merchant
from src.model.SqlObject import SqlObject


class Location(SqlObject):
    """
    Represents a merchant location in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int],
        description: Optional[str],
        merchant_id: int,
        lat: float,
        long: float,
    ) -> None:
        """
        :param sqlid: ID of SQL row this object belongs to.
        :param description: Description of this merchant location.
        :param merchant_id: ID of merchant this location belongs to.
        :param lat: Latitude of this location.
        :param long: Longitude of this location.
        """
        super().__init__(sqlid)
        self.description: Optional[str] = None
        self.merchant_id: int = 0
        self.lat: float = 0.0
        self.long: float = 0.0

    def sync(self) -> None:
        """
        Syncs this location to the database by updating the database. If the location is not in the database it is
        added.
        """

    def merchant(self) -> Merchant:
        """
        Gets the merchant this location belongs to.

        :return: The location this merchant belongs to.
        """
