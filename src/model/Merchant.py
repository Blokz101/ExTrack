from __future__ import annotations

from sqlite3 import IntegrityError
from typing import Optional

from src.model import database
from src.model import Location
from src.model import Tag
from src.model import Transaction
from src.model.SqlObject import SqlObject


class Merchant(SqlObject):
    """
    Represents a merchant in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int],
        name: str,
        online: bool,
        rule: Optional[str],
    ) -> None:
        """
        :param sqlid: ID of SQL row that this merchant belongs to.
        :param name: Name of the merchant.
        :param online: True if the merchant has no physical locations, false if otherwise.
        :param rule: RegEx string used to identify transactions made at this merchant.
        """
        super().__init__(sqlid)
        self.name: str = name
        """Name of the merchant."""
        self.online: bool = online
        """True if the merchant has no physical locations, false if otherwise."""
        self.rule: Optional[str] = rule
        """RegEx string used to identify transactions made at this merchant."""

    @classmethod
    def from_id(cls, sqlid: int) -> Merchant:
        """
        Creates a Merchant instance from the database.

        :param sqlid: ID of the Merchant.
        :return: Merchant instance.
        :raises ValueError: If a Merchant with that ID does not exist.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT id, name, online, rule FROM merchants WHERE id = ?", (sqlid,)
        )

        data: object = cur.fetchone()

        if data is None:
            raise ValueError(f"No merchant with id = {sqlid}.")
        else:
            sqlid, name, online, rule = data
            return Merchant(sqlid, name, online, rule)

    def sync(self) -> None:
        """
        Syncs this merchant to the database by updating the database. If the merchant is not in the database it is
        added.

        Syncing only updates edited instance variables. Sync does not need to be called after another function that
        updates the database, that function will sync on its own.
        """
        con, cur = database.get_connection()

        if self.exists():
            cur.execute(
                "UPDATE merchants SET name = ?, online = ?, rule = ? WHERE id = ?",
                (self.name, self.online, self.rule, self.sqlid),
            )
        else:
            cur.execute(
                "INSERT INTO merchants (name, online, rule) VALUES (?, ?, ?)",
                (self.name, self.online, self.rule),
            )

        con.commit()

    @staticmethod
    def get_all() -> list[Merchant]:
        """
        Gets a list of merchants from all rows in the database.

        :return: List of merchants from all rows in the database.
        """
        _, cur = database.get_connection()

        cur.execute("SELECT id, name, online, rule FROM merchants")
        return list(Merchant(*data) for data in cur.fetchall())

    def __eq__(self, other) -> bool:
        """
        Checks if this Merchant is equal to another Merchant.

        A Merchant is equal if all its fields except the sqlid are equal.

        :param other: The other Merchant to compare against this one.
        :return: True if the Merchants are equal, false if otherwise.
        """
        return (
            self.name == other.name
            and self.online == other.online
            and self.rule == other.rule
        )

    def transactions(self) -> list[Transaction.Transaction]:
        """
        Gets the list of transactions made at this merchant.

        :return: List of transactions made at this merchant.
        """
        raise NotImplementedError()

    def locations(self) -> list[Location.Location]:
        """
        Gets a list of physical locations this merchant has.

        :return: List of physical locations this merchant has.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT id, description, merchant_id, lat, long FROM locations WHERE merchant_id = ?",
            (self.sqlid,),
        )
        return list(Location.Location(*data) for data in cur.fetchall())

    def default_tags(self) -> list[Tag.Tag]:
        """
        List of tags a transaction made with this merchant get by default.

        :return: List of default tags.
        """
        _, cur = database.get_connection()

        cur.execute(
            """
            SELECT tags.id, tags.name, tags.occasional
            FROM merchants
            INNER JOIN mer_tag_defaults ON merchants.id = mer_tag_defaults.merchant_id
            INNER JOIN tags ON mer_tag_defaults.tag_id = tags.id
            WHERE merchants.id = ?
            """,
            (self.sqlid,),
        )
        return list(Tag.Tag(*data) for data in cur.fetchall())

    def add_default_tag(self, tag: Tag.Tag) -> None:
        """
        Adds a default tag.

        :param tag: Tag to be added
        :raises ValueError: If the tag is a duplicate.
        """
        con, cur = database.get_connection()

        try:
            cur.execute(
                "INSERT INTO mer_tag_defaults (merchant_id, tag_id) VALUES (?, ?)",
                (self.sqlid, tag.sqlid),
            )
        except IntegrityError:
            raise ValueError(f"Cannot add duplicate default tag '{tag.name}'.")

        con.commit()

    def remove_default_tag(self, tag_id: int) -> None:
        """
        Removes a default tag.

        :param tag_id: ID of tag to be removed.
        :raises KeyError: If tag does not exist.
        """
        con, cur = database.get_connection()

        # If the merchant tag pair does not exist throw error
        cur.execute(
            "SELECT 1 FROM mer_tag_defaults WHERE merchant_id = ? AND tag_id = ?",
            (self.sqlid, tag_id),
        )
        if cur.fetchone() is None:
            raise KeyError(
                f"Merchant '{self.name}' does not have a default tag '{Tag.Tag.from_id(tag_id).name}'."
            )

        # Delete the merchant tag pair
        cur.execute(
            "DELETE FROM mer_tag_defaults WHERE merchant_id = ? AND tag_id = ?",
            (self.sqlid, tag_id),
        )

        con.commit()
