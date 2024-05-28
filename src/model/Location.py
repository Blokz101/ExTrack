from __future__ import annotations

from typing import Optional

from model import Merchant, database
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
        self.description: Optional[str] = description
        self.merchant_id: int = merchant_id
        self.lat: float = lat
        self.long: float = long

    @classmethod
    def from_id(cls, sqlid: int) -> Location:
        """
        Creates a Location instance from the database.

        :param sqlid: ID of Location.
        :return: Location instance.
        :raises ValueError: If a Location with that ID does not exist.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT id, description, merchant_id, lat, long FROM locations WHERE id = ?",
            (sqlid,),
        )

        data: object = cur.fetchone()

        if data is None:
            raise ValueError(f"No location with id = {sqlid}.")
        else:
            sqlid, description, merchant_id, lat, long = data
            return Location(sqlid, description, merchant_id, lat, long)

    def sync(self) -> None:
        """
        Syncs this location to the database by updating the database. If the location is not in the database it is
        added.
        """
        con, cur = database.get_connection()

        if self.exists():
            cur.execute(
                "UPDATE locations SET description = ?, merchant_id = ?, lat = ?, long = ? WHERE id = ?",
                (self.description, self.merchant_id, self.lat, self.long, self.sqlid),
            )
        else:
            cur.execute(
                "INSERT INTO locations (description, merchant_id, lat, long) VALUES (?, ?, ?, ?)",
                (self.description, self.merchant_id, self.lat, self.long),
            )

        con.commit()

    def merchant(self) -> Merchant.Merchant:
        """
        Gets the merchant this location belongs to.

        :return: The location this merchant belongs to.
        """
        raise NotImplementedError()

    @staticmethod
    def get_all() -> list[Location]:
        """
        Gets a list of locations from all rows in the database.

        :return: List of locations from all rows in the database.
        """

        _, cur = database.get_connection()

        cur.execute("SELECT id, description, merchant_id, lat, long FROM locations")
        return list(Location(*data) for data in cur.fetchall())

    def __eq__(self, other: Location) -> bool:
        """
        Checks if this Location is equal to another Location.

        A Location is equal if all of its fields except the sqlid are equal.

        :param other: The other Location to compare against this one.
        :return: True if the Locations are equal, false if otherwise.
        """
        return (
            self.description == other.description
            and self.merchant_id == other.merchant_id
            and self.lat == other.lat
            and self.long == other.long
        )
