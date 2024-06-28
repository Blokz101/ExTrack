from __future__ import annotations

from sqlite3 import IntegrityError
from typing import Optional

from src.model import Transaction
from src.model import Amount, database
from src.model import Merchant
from src.model.SqlObject import SqlObject


class Tag(SqlObject):
    """
    Represents a tag in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int] = None,
        name: Optional[str] = None,
        occasional: Optional[bool] = None,
    ) -> None:
        """
        :param sqlid: ID of the SQL row this tag belongs to.
        :param name: Name of the tag.
        :param occasional: True if this tag will not have long term use, false if otherwise.
        """
        super().__init__(sqlid)
        self.name: Optional[str] = name
        """Name of Tag."""
        self.occasional: Optional[bool] = occasional
        """True if this tag is only used for an occasion, False if it is recurring."""

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

        :raise RuntimeError: If this Tag is not syncable
        """
        super().sync()
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
        self.sqlid = cur.lastrowid

    def syncable(self) -> Optional[list[str]]:
        """
        Checks if this Tag has non-null values for all required fields.

        :return: None of this Tag is syncable or a list of error messages if it is not
        """
        if self.name == "":
            self.name = None

        errors: list[str] = []

        if self.name is None:
            errors.append("name cannot be None.")

        if self.occasional is None:
            errors.append("occasional cannot be None.")

        return None if len(errors) == 0 else errors

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

    def transactions(self) -> list[Transaction.Transaction]:
        """
        Gets the list of Transactions this Tag has.

        :return: List of Transactions this Tag has.
        """
        _, cur = database.get_connection()

        cur.execute(
            """
            SELECT transactions. id, transactions. description, transactions. merchant_id, transactions. reconciled, 
            transactions. date, transactions. statement_id, transactions. receipt_file_name, transactions.lat, 
            transactions.long, transactions.account_id, transactions.transfer_trans_id
            FROM tags
            INNER JOIN amount_tags ON tags.id = amount_tags.tag_id
            INNER JOIN amounts ON amount_tags.amount_id = amounts.id
            INNER JOIN transactions ON amounts.transaction_id = transactions.id
            WHERE tags.id = ?
            """,
            (self.sqlid,),
        )

        return list(Transaction.Transaction(*data) for data in cur.fetchall())

    def __str__(self):
        return self.name
