from __future__ import annotations

from sqlite3 import IntegrityError
from typing import Optional

from src.model import Amount, database
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
        self.name: str = name
        self.occasional: bool = occasional

    @classmethod
    def from_id(cls, sqlid: int) -> Tag:
        """
        Creates a Tag instance from the database.

        :param sqlid: ID of Tag.
        :return: Tag instance.
        :raises ValueError: If a Tag with that ID does not exist.
        """
        _, cur = database.get_connection()

        cur.execute("SELECT id, name, occasional FROM tags WHERE id = ?", (sqlid,))

        data: object = cur.fetchone()

        if data is None:
            raise ValueError(f"No tag with id = {sqlid}.")
        else:
            sqlid, name, occasional = data
            return Tag(sqlid, name, occasional)

    def sync(self) -> None:
        """
        Syncs this tag to the database by updating the database. If the tag is not in the database it is
        added.

        Syncing only updates edited instance variables. Sync does not need to be called after another function that
        updates the database, that function will sync on its own.
        """
        con, cur = database.get_connection()

        if self.exists():
            cur.execute(
                "UPDATE tags SET name = ?, occasional = ? WHERE id = ?",
                (
                    self.name,
                    self.occasional,
                    self.sqlid,
                ),
            )
        else:
            cur.execute(
                "INSERT INTO tags (name, occasional) VALUES (?, ?)",
                (self.name, self.occasional),
            )

        con.commit()

    @staticmethod
    def get_all() -> list[Tag]:
        """
        Gets a list of tags from all rows in the database.

        :return: List of tags from all rows in the database.
        """
        _, cur = database.get_connection()

        cur.execute("SELECT id, name, occasional FROM tags")
        return list(Tag(*data) for data in cur.fetchall())

    def __eq__(self, other: Tag) -> bool:
        """
        Checks if this Tag is equal to another Tag.

        A Tag is equal if all its fields except the sqlid are equal.

        :param other: The other Tag to compare against this one.
        :return: True if the Tags are equal, false if otherwise.
        """
        return self.name == other.name and self.occasional == other.occasional

    def default_merchants(self) -> list[Merchant.Merchant]:
        """
        Gets the list of merchants for which this is a default tag.

        :return: List of merchants for which this is a default tag.
        """
        _, cur = database.get_connection()

        cur.execute(
            """
                SELECT merchants.id, merchants.name, merchants.online, merchants.rule
                FROM tags
                INNER JOIN mer_tag_defaults ON tags.id = mer_tag_defaults.tag_id
                INNER JOIN merchants ON mer_tag_defaults.merchant_id = merchants.id
                WHERE tags.id = ?
                """,
            (self.sqlid,),
        )
        return list(Merchant.Merchant(*data) for data in cur.fetchall())

    def add_default_merchant(self, merchant: Merchant.Merchant) -> None:
        """
        Adds a default merchant.

        :param merchant: Merchant to be added
        :raises ValueError: If the merchant is a duplicate.
        """
        con, cur = database.get_connection()

        try:
            cur.execute(
                "INSERT INTO mer_tag_defaults (tag_id, merchant_id) VALUES (?, ?)",
                (self.sqlid, merchant.sqlid),
            )
        except IntegrityError:
            raise ValueError(
                f"Cannot add duplicate default merchant '{merchant.name}'."
            )

        con.commit()

    def remove_default_merchant(self, merchant_id: int) -> None:
        """
        Removes a default merchant.

        :param merchant_id: ID of merchant to be removed.
        :raises KeyError: If merchant does not exist.
        """
        con, cur = database.get_connection()

        # If the merchant tag pair does not exist throw error
        cur.execute(
            "SELECT 1 FROM mer_tag_defaults WHERE tag_id = ? AND merchant_id = ?",
            (self.sqlid, merchant_id),
        )
        if cur.fetchone() is None:
            raise KeyError(
                f"Tag '{self.name}' does not have a default merchant '{Merchant.Merchant.from_id(merchant_id).name}'."
            )

        # Delete the merchant tag pair
        cur.execute(
            "DELETE FROM mer_tag_defaults WHERE tag_id = ? AND merchant_id = ?",
            (self.sqlid, merchant_id),
        )

        con.commit()

    def amounts(self) -> list[Amount.Amount]:
        """
        Gets the list of amounts tagged with this tag.

        :return: List of amounts tagged with this tag.
        """
        _, cur = database.get_connection()

        cur.execute(
            """
            SELECT amounts.id, amounts.amount, amounts.transaction_id, amounts.description
            FROM tags
            INNER JOIN amount_tags ON tags.id = amount_tags.tag_id
            INNER JOIN amounts ON amount_tags.amount_id = amounts.id
            WHERE tags.id = ?
            """,
            (self.sqlid,),
        )
        return list(Amount.Amount(*data) for data in cur.fetchall())
