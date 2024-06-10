from __future__ import annotations

from typing import Optional

from src.model import Statement, database
from src.model.SqlObject import SqlObject
from src.model import Transaction


class Account(SqlObject):
    """
    Represents an account in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int],
        name: str,
        amount_idx: Optional[int],
        description_idx: Optional[int],
        date_idx: Optional[int],
    ) -> None:
        """
        :param sqlid: ID of SQL row that this account belongs to.
        :param name: Name of account.
        :param amount_idx: Index of amount column on each statement for this account.
        :param description_idx: Index of description column on each statement for this account.
        :param date_idx: Index of date column on each statement for this account.
        """
        super().__init__(sqlid)
        self.name: str = name
        """Name of account."""
        self.amount_idx: Optional[int] = amount_idx
        """Index of amount column on each statement for this account."""
        self.description_idx: Optional[int] = description_idx
        """Index of description column on each statement for this account."""
        self.date_idx: Optional[int] = date_idx
        """Index of date column on each statement for this account."""

    @classmethod
    def from_id(cls, sqlid: int) -> Account:
        """
        Creates an Account instance from the database.

        :param sqlid: ID of Account.
        :return: Account instance.
        :raises ValueError: If an Account with that ID does not exist.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT id, name, amount_index, description_index, date_index FROM accounts WHERE id = ?",
            (sqlid,),
        )
        data: object = cur.fetchone()

        if data is None:
            raise ValueError(f"No account with id = {sqlid}.")
        else:
            sqlid, name, amount_idx, description_idx, date_idx = data
            return Account(sqlid, name, amount_idx, description_idx, date_idx)

    def sync(self) -> None:
        """
        Syncs this account to the database by updating the database. If the account is not in the database it is
        added.

        Syncing only updates edited instance variables. Sync does not need to be called after another function that
        updates the database, that function will sync on its own.
        """
        con, cur = database.get_connection()

        if self.exists():
            cur.execute(
                "UPDATE accounts SET name = ?, amount_index = ?, description_index = ?, date_index = ? WHERE id = ?",
                (
                    self.name,
                    self.amount_idx,
                    self.description_idx,
                    self.date_idx,
                    self.sqlid,
                ),
            )
        else:
            cur.execute(
                "INSERT INTO accounts (name, amount_index, description_index, date_index) VALUES (?, ?, ?, ?)",
                (
                    self.name,
                    self.amount_idx,
                    self.description_idx,
                    self.date_idx,
                ),
            )

        con.commit()

    @staticmethod
    def get_all() -> list[Account]:
        """
        Gets a list of accounts from all rows in the database.

        :return: List of accounts from all rows in the database.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT id, name, amount_index, description_index, date_index FROM accounts"
        )
        return list(Account(*data) for data in cur.fetchall())

    def __eq__(self, other: Account) -> bool:
        """
        Checks if this Account is equal to another Account.

        A Account is equal if all its fields except the sqlid are equal.

        :param other: The other Account to compare against this one.
        :return: True if the Accounts are equal, false if otherwise.
        """
        return (
            self.name == other.name
            and self.amount_idx == other.amount_idx
            and self.description_idx == other.description_idx
            and self.date_idx == other.date_idx
        )

    def transactions(self) -> list[Transaction.Transaction]:
        """
        Gets the list of transactions for this account.

        :return: List of transactions for this account.
        """
        raise NotImplementedError()

    def statements(self) -> list[Statement.Statement]:
        """
        Gets the list of statements that this account is linked to.

        :return: List of statements that this account is linked to.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT id, date, path, account_id FROM statements WHERE account_id = ?",
            (self.sqlid,),
        )
        return list(Statement.Statement(*data) for data in cur.fetchall())
