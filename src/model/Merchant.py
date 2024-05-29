from __future__ import annotations

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
