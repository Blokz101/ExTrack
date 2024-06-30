from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from src.model import Account, database, date_format
from src.model import Transaction
from src.model.SqlObject import SqlObject


class Statement(SqlObject):
    """
    Represents a statement in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int] = None,
        date: Optional[Union[str, datetime]] = None,
        path: Optional[Path] = None,
        account_id: Optional[int] = None,
    ) -> None:
        """
        :param sqlid: ID of SQL row that this statement belongs to.
        :param date: Start date of billing period of statement.
        :param path: Path to statement CSV.
        :param account_id: ID of account of this statement.
        """
        super().__init__(sqlid)
        self.date: Optional[datetime]
        """Start date of billing period of statement."""
        if date is None:
            self.date = None
        else:
            self.date = (
                date
                if isinstance(date, datetime)
                else datetime.strptime(date, date_format)
            )
        self.path: Optional[Path] = path
        """Path to statement CSV."""
        self.account_id: Optional[int] = account_id
        """ID of account of this statement."""

    @classmethod
    def from_id(cls, sqlid: int) -> Statement:
        """
        Creates a Statement instance from the database.

        :param sqlid: ID of the Statement.
        :return: Statement instance.
        :raises ValueError: If a Statement with that ID does not exist.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT id, date, path, account_id FROM statements WHERE id = ?", (sqlid,)
        )

        data: object = cur.fetchone()

        if data is None:
            raise ValueError(f"No statement with id = {sqlid}.")
        else:
            sqlid, date, path, account_id = data
            return Statement(sqlid, date, path, account_id)

    def sync(self) -> None:
        """
        Syncs this statement to the database by updating the database. If the statement is not in the database it is
        added.

        Syncing only updates edited instance variables. Sync does not need to be called after another function that
        updates the database, that function will sync on its own.
        """
        super().sync()
        con, cur = database.get_connection()

        if self.exists():
            cur.execute(
                "UPDATE statements SET date = ?, path = ?, account_id = ? WHERE id = ?",
                (
                    self.date.strftime(date_format),
                    self.path,
                    self.account_id,
                    self.sqlid,
                ),
            )
        else:
            cur.execute(
                "INSERT INTO statements (date, path, account_id) VALUES (?, ?, ?)",
                (
                    self.date.strftime(date_format),
                    self.path,
                    self.account_id,
                ),
            )
            self.sqlid = cur.lastrowid

        con.commit()

    def syncable(self) -> Optional[list[str]]:
        """
        Checks if this Statement has non-null values for all required fields.

        :return: None if this Statement is syncable or a list of error messages if it is not
        """
        errors: list[str] = []

        if self.date is None:
            errors.append("date cannot be None.")

        if self.account_id is None:
            errors.append("account_id cannot be None.")

        return None if len(errors) == 0 else errors

    @staticmethod
    def get_all() -> list[Statement]:
        """
        Gets a list of statements from all rows in the database.

        :return: List of all statements from all rows in the database.
        """
        _, cur = database.get_connection()

        cur.execute("SELECT id, date, path, account_id FROM statements")
        return list(Statement(*data) for data in cur.fetchall())

    def __eq__(self, other: Statement) -> bool:
        """
        Checks if this Statement is equal to another Statement.

        A Statement is equal if all its fields except the sqlid are equal.

        :param other: The other Statement to compare against this one.
        :return: True if the Statements are equal, false if otherwise.
        """
        return (
            self.date == other.date
            and self.path == other.path
            and self.account_id == other.account_id
        )

    def transactions(self) -> list[Transaction.Transaction]:
        """
        Gets the list of transactions in this statement.

        :return: List of transactions in this statement.
        """
        _, cur = database.get_connection()

        cur.execute(
            """SELECT id, description, merchant_id, reconciled, date, statement_id, receipt_file_name, lat, long, 
                account_id, transfer_trans_id FROM transactions WHERE statement_id = ?""",
            (self.sqlid,),
        )
        return list(Transaction.Transaction(*data) for data in cur.fetchall())

    def account(self) -> Account.Account:
        """
        Gets the account this statement belongs to.

        :return: Account this statement belongs to.
        """
        return (
            None
            if self.account_id is None
            else Account.Account.from_id(self.account_id)
        )
