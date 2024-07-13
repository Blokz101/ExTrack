"""
Contains the Tag class which represents an amount tag in the SQL database.
"""

from __future__ import annotations

from typing import Optional, cast, Any

from src.model import database, amount, merchant, transaction
from src.model.sql_object import SqlObject


class Tag(SqlObject):
    """
    Represents a tag in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int] = None,
        name: Optional[str] = None,
        occasional: Optional[bool] = None,
        rule: Optional[str] = None,
    ) -> None:
        """
        :param sqlid: ID of the SQL row this tag belongs to.
        :param name: Name of the tag.
        :param occasional: True if this tag will not have long term use, false if otherwise.
        :param rule: RegEx string used to identify transactions that should be labeled with this
        tag.
        """
        super().__init__(sqlid)
        self.name: Optional[str] = name
        """Name of Tag."""
        self.occasional: Optional[bool]
        """True if this tag is only used for an occasion, False if it is recurring."""
        if occasional is None:
            self.occasional = None
        else:
            self.occasional = (
                occasional if isinstance(occasional, bool) else occasional == 1
            )
        self.rule: Optional[str] = rule
        """
        RegEx string used to identify transactions that should be labeled with this tag. 
        Searches for tags in the description of a transaction.
        """

    @classmethod
    def from_id(cls, sqlid: int) -> Tag:
        """
        Creates a Tag instance from the database.

        :param sqlid: ID of Tag.
        :return: Tag instance.
        :raises ValueError: If a Tag with that ID does not exist.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT id, name, occasional, rule FROM tags WHERE id = ?", (sqlid,)
        )

        data: object = cur.fetchone()

        if data is None:
            raise ValueError(f"No tag with id = {sqlid}.")
        return Tag(*cast(list, data))

    def sync(self) -> None:
        """
        Syncs this tag to the database by updating the database. If the tag is not in the
        database it is added.

        Syncing only updates edited instance variables. Sync does not need to be called after
        another function that updates the database, that function will sync on its own.

        :raise RuntimeError: If this Tag is not syncable
        """
        super().sync()
        con, cur = database.get_connection()

        if self.exists():
            cur.execute(
                "UPDATE tags SET name = ?, occasional = ?, rule = ? WHERE id = ?",
                (
                    self.name,
                    self.occasional,
                    self.rule,
                    self.sqlid,
                ),
            )
        else:
            cur.execute(
                "INSERT INTO tags (name, occasional, rule) VALUES (?, ?, ?)",
                (self.name, self.occasional, self.rule),
            )
            self.sqlid = cur.lastrowid

        con.commit()

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

        cur.execute("SELECT id, name, occasional, rule FROM tags")
        return list(Tag(*data) for data in cur.fetchall())

    def __eq__(self, other: Any) -> bool:
        """
        Checks if this Tag is equal to another Tag.

        A Tag is equal if all its fields except the sqlid are equal.

        :param other: The other Tag to compare against this one.
        :return: True if the Tags are equal, false if otherwise.
        """
        return (
            self.name == other.name
            and self.occasional == other.occasional
            and self.rule == other.rule
        )

    def default_merchants(self) -> list[merchant.Merchant]:
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
        return list(merchant.Merchant(*data) for data in cur.fetchall())

    def amounts(self) -> list[amount.Amount]:
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
        return list(amount.Amount(*data) for data in cur.fetchall())

    def transactions(self) -> list[transaction.Transaction]:
        """
        Gets the list of Transactions this Tag has.

        :return: List of Transactions this Tag has.
        """
        _, cur = database.get_connection()

        cur.execute(
            """
            SELECT transactions. id, transactions.description, transactions. merchant_id,
            transactions.reconciled, transactions.date, transactions.statement_id,
            transactions.receipt_file_name, transactions.lat, transactions.long, 
            transactions.account_id, transactions.transfer_trans_id
            FROM tags
            INNER JOIN amount_tags ON tags.id = amount_tags.tag_id
            INNER JOIN amounts ON amount_tags.amount_id = amounts.id
            INNER JOIN transactions ON amounts.transaction_id = transactions.id
            WHERE tags.id = ?
            """,
            (self.sqlid,),
        )

        return list(transaction.Transaction(*data) for data in cur.fetchall())

    def __str__(self):
        return self.name
