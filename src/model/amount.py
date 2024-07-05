"""
Contains the Amount class which represents an amount of money for a transaction in the SQL database.
"""

from __future__ import annotations

from typing import Optional, cast, Any

from src.model import database, transaction, tag
from src.model.sql_object import SqlObject


class Amount(SqlObject):
    """
    Represents an amount of money for a transaction in the SQL database. Each transaction may
    have multiple amounts so that multiple items in one transaction may have different tags.
    """

    def __init__(
        self,
        sqlid: Optional[int] = None,
        amount: Optional[float] = None,
        transaction_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        :param sqlid: ID of SQL row that this amount belongs to.
        :param amount: Amount of money this amount represents.
        :param transaction_id: Transaction this amount belongs to.
        :param description: Description of this amount.
        """
        super().__init__(sqlid)
        self.amount: Optional[float] = amount
        self.transaction_id: Optional[int] = transaction_id
        self.description: Optional[str] = description

    @classmethod
    def from_id(cls, sqlid: int) -> Amount:
        """
        Creates an Amount instance from the database.

        :param sqlid: ID of the Amount.
        :return: Amount instance.
        :raises ValueError: If an Amount with that ID does not exist.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT id, amount, transaction_id, description FROM amounts WHERE id = ?",
            (sqlid,),
        )

        data: object = cur.fetchone()

        if data is None:
            raise ValueError(f"No amount with id = {sqlid}.")
        sqlid, amount, transaction_id, description = cast(list, data)
        return Amount(sqlid, amount, transaction_id, description)

    def sync(self) -> None:
        """
        Syncs this amount to the database by updating the database. If the amount is not in the
        database it is added.

        Syncing only updates edited instance variables. Sync does not need to be called after
        another function that updates the database, that function will sync on its own.

        :raises RuntimeError: If this Amount is not syncable
        """
        super().sync()
        con, cur = database.get_connection()

        if self.exists():
            cur.execute(
                "UPDATE amounts SET amount = ?, transaction_id = ?, description = ? WHERE id = ?",
                (self.amount, self.transaction_id, self.description, self.sqlid),
            )
        else:
            cur.execute(
                "INSERT INTO amounts (amount, transaction_id, description) VALUES (?, ?, ?)",
                (self.amount, self.transaction_id, self.description),
            )
            self.sqlid = cur.lastrowid

        con.commit()

    def syncable(self) -> Optional[list[str]]:
        """
        Checks if this Amount has non-null values for all required fields.

        :return: None if this Amount is syncable or a list of error messages if it is not
        """
        if self.description == "":
            self.description = None

        errors: list[str] = []

        if self.amount is None:
            errors.append("amount cannot be None.")

        if self.transaction_id is None:
            errors.append("transaction_id cannot be None.")

        return None if len(errors) == 0 else errors

    @staticmethod
    def get_all() -> list[Amount]:
        """
        Gets a list of amounts from all rows in the database.

        :return: List of amounts from all rows in the database.
        """
        _, cur = database.get_connection()

        cur.execute("SELECT id, amount, transaction_id, description FROM amounts")
        return list(Amount(*data) for data in cur.fetchall())

    def delete(self) -> None:
        """
        Deletes this Amount.
        """
        if not self.exists():
            raise RuntimeError(
                "Cannot delete amount because it does not exist in the database"
            )

        # Ensure that the transaction this amount is linked to has more than one amount.
        trans: transaction.Transaction = transaction.Transaction.from_id(
            self.transaction_id  # type: ignore
        )
        if len(trans.amounts()) <= 1:
            raise RuntimeError(
                f"Cannot delete amount with id = {self.sqlid} because transaction with id = "
                f"{trans.sqlid} would "
                "be left without an amount."
            )

        # Delete this amount
        con, cur = database.get_connection()

        cur.execute("DELETE FROM amounts WHERE id = ?", (self.sqlid,))
        con.commit()

        del self

    def __eq__(self, other: Any) -> bool:
        """
        Checks if this Amount is equal to another Amount.

        An Amount is equal to another Amount if all its fields except the sqlid are equal.

        :param other: The other Amount to compare against this one.
        :return: True if the Amounts are equal, false if otherwise.
        """
        return (
            self.amount == other.amount
            and self.transaction_id == other.transaction_id
            and self.description == other.description
        )

    def transaction(self) -> Optional[transaction.Transaction]:
        """
        Get the transaction that this amount belongs to.

        :return: Transaction this amount belongs to.
        """
        return (
            None
            if self.transaction_id is None
            else transaction.Transaction.from_id(self.transaction_id)
        )

    def tags(self) -> list[tag.Tag]:
        """
        Gets the list of tags that this amount is tagged with.

        :return: List of tags that this amount is tagged with.
        """
        _, cur = database.get_connection()

        cur.execute(
            """
            SELECT tags.id, tags.name, tags.occasional
            FROM amounts
            INNER JOIN amount_tags ON amounts.id = amount_tags.amount_id
            INNER JOIN tags ON amount_tags.tag_id = tags.id
            WHERE amounts.id = ?
            """,
            (self.sqlid,),
        )
        return list(tag.Tag(*data) for data in cur.fetchall())

    def set_tags(self, tag_id_list: list[int]) -> None:
        """
        Sets the tags that this amount is tagged with.

        :param tag_id_list: List of tags to set for this amount
        :raise RuntimeError: If the amount does not exist in the database
        """
        if not self.exists():
            raise RuntimeError(
                "Cannot set tags of an amount that does not exist in the database."
            )

        con, cur = database.get_connection()

        cur.execute("DELETE FROM amount_tags WHERE amount_id = ?", (self.sqlid,))

        for tag_id in tag_id_list:
            cur.execute(
                "INSERT INTO amount_tags (amount_id, tag_id) VALUES (?, ?)",
                (
                    self.sqlid,
                    tag_id,
                ),
            )

        con.commit()
