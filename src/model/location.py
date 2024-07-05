"""
Contains the Location class which represents a merchant location in the SQL database.
"""

from __future__ import annotations

from typing import Optional, cast, Any

from src.model import database, merchant
from src.model.sql_object import SqlObject


class Location(SqlObject):
    """
    Represents a merchant location in the SQL database.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        sqlid: Optional[int] = None,
        description: Optional[str] = None,
        merchant_id: Optional[int] = None,
        lat: Optional[float] = None,
        long: Optional[float] = None,
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
        """Description of this merchant location."""
        self.merchant_id: Optional[int] = merchant_id
        """ID of merchant this location belongs to."""
        self.lat: Optional[float] = lat
        """Latitude of this location."""
        self.long: Optional[float] = long
        """Longitude of this location."""

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
        sqlid, description, merchant_id, lat, long = cast(list, data)
        return Location(sqlid, description, merchant_id, lat, long)

    def sync(self) -> None:
        """
        Syncs this location to the database by updating the database. If the location is not in
        the database it is added.

        Syncing only updates edited instance variables. Sync does not need to be called after
        another function that updates the database, that function will sync on its own.
        """
        super().sync()
        con, cur = database.get_connection()

        if self.exists():
            cur.execute(
                """
                UPDATE locations 
                SET description = ?, merchant_id = ?, lat = ?, long = ?
                WHERE id = ?
                """,
                (self.description, self.merchant_id, self.lat, self.long, self.sqlid),
            )
        else:
            cur.execute(
                "INSERT INTO locations (description, merchant_id, lat, long) VALUES (?, ?, ?, ?)",
                (self.description, self.merchant_id, self.lat, self.long),
            )
            self.sqlid = cur.lastrowid

        con.commit()

    def syncable(self) -> Optional[list[str]]:
        """
        Checks if this Location has non-null values for all required fields.

        :return: None if this Location is syncable or a list of error messages if it is not
        """
        if self.description == "":
            self.description = None

        errors: list[str] = []

        if self.merchant_id is None:
            errors.append("merchant_id cannot be None.")

        if self.lat is None:
            errors.append("lat cannot be None.")

        if self.long is None:
            errors.append("long cannot be None.")

        return None if len(errors) == 0 else errors

    @staticmethod
    def get_all() -> list[Location]:
        """
        Gets a list of locations from all rows in the database.

        :return: List of locations from all rows in the database.
        """
        _, cur = database.get_connection()

        cur.execute("SELECT id, description, merchant_id, lat, long FROM locations")
        return list(Location(*data) for data in cur.fetchall())

    def __eq__(self, other: Any) -> bool:
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

    def merchant(self) -> Optional[merchant.Merchant]:
        """
        Gets the merchant this location belongs to.

        :return: The location this merchant belongs to.
        """
        return (
            None
            if self.merchant_id is None
            else merchant.Merchant.from_id(self.merchant_id)
        )
