from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from src.model import Tag
from src.model import Account, date_format, database
from src.model import Amount
from src.model import Merchant
from src.model.SqlObject import SqlObject
from src.model import Statement


class Transaction(SqlObject):
    """
    Represents a Transaction in the SQL database.
    """

    def __init__(
        self,
        sqlid: Optional[int],
        description: Optional[str],
        merchant_id: Optional[int],
        reconciled: Union[bool, int],
        date: Optional[Union[str, datetime]],
        statement_id: Optional[int],
        receipt_file_name: Optional[str],
        lat: Optional[float],
        long: Optional[float],
        account_id: Optional[int],
        transfer_trans_id: Optional[int],
    ):
        """
        :param sqlid: ID of SQL row that this Transaction belongs to.
        :param description: Description of the Transaction.
        :param merchant_id: ID of Transaction's Merchant
        :param reconciled: Whether this Transaction is reconciled.
        :param date: Date of Transaction.
        :param statement_id: ID of Statement that this Transaction belongs to.
        :param receipt_file_name: Name of the receipt file this Transaction belongs to.
        :param lat: Latitude of Transaction location.
        :param long: Longitude of Transaction location.
        :param account_id: ID of Account that this Transaction belongs to.
        :param transfer_trans_id: ID of transfer Transaction that this Transaction is linked to.
        """
        super().__init__(sqlid)
        self.description: Optional[str] = description
        """Description of Transaction."""
        self.merchant_id: Optional[int] = merchant_id
        """ID of the Merchant of this Transaction."""
        self.reconciled: bool = (
            reconciled
            if isinstance(reconciled, bool)
            else False if reconciled == 0 else True
        )
        """True if this Transaction has been reconciled, false otherwise."""
        self.date: Optional[datetime] = (
            date
            if isinstance(date, datetime) or date is None
            else datetime.strptime(date, date_format)
        )
        """Date of Transaction."""
        self.statement_id: Optional[int] = statement_id
        """ID of the statement that this Transaction belongs to."""
        self.receipt_file_name: Optional[str] = receipt_file_name
        """Name of receipt file this Transaction belongs to."""
        self.lat: Optional[float] = lat
        """Latitude of Transaction location."""
        self.long: Optional[float] = long
        """Longitude of Transaction location."""
        self.account_id: Optional[int] = account_id
        """ID of the Account that this Transaction belongs to."""
        self.transfer_trans_id: Optional[int] = transfer_trans_id
        """ID of the transfer Transaction that this Transaction is linked to."""

    @classmethod
    def from_id(cls, sqlid: int) -> Transaction:
        """
        Creates a Transaction instance from the database.

        :param sqlid: ID of the Transaction.
        :return: Transaction instance.
        :raises ValueError: If a Transaction with that ID does not exist.
        """
        _, cur = database.get_connection()

        cur.execute(
            """SELECT id, description, merchant_id, reconciled, date, statement_id, receipt_file_name, lat, long, 
            account_id, transfer_trans_id FROM transactions WHERE id = ?""",
            (sqlid,),
        )

        data: object = cur.fetchone()

        if data is None:
            raise ValueError(f"No transaction with id = {sqlid}.")
        else:
            (
                sqlid,
                description,
                merchant_id,
                reconciled,
                date,
                statement_id,
                receipt_file_name,
                lat,
                long,
                account_id,
                transfer_trans_id,
            ) = data
            return Transaction(
                sqlid,
                description,
                merchant_id,
                reconciled,
                date,
                statement_id,
                receipt_file_name,
                lat,
                long,
                account_id,
                transfer_trans_id,
            )

    def sync(self) -> None:
        """
        Syncs this Transaction to the database by updating the database. If the Transaction is not in the database it is
        added.

        Syncing only updates edited instance variables. Sync does not need to be called after another function that
        updates the database, that function will sync on its own.
        """
        con, cur = database.get_connection()

        if self.exists():
            cur.execute(
                """
                UPDATE transactions SET description = ?, merchant_id = ?, reconciled = ?, date = ?, statement_id = ?, 
                receipt_file_name = ?, lat = ?, long = ?, account_id = ?, transfer_trans_id = ? WHERE id = ?
                """,
                (
                    self.description,
                    self.merchant_id,
                    self.reconciled,
                    None if self.date is None else self.date.strftime(date_format),
                    self.statement_id,
                    self.receipt_file_name,
                    self.lat,
                    self.long,
                    self.account_id,
                    self.transfer_trans_id,
                    self.sqlid,
                ),
            )
        else:
            cur.execute(
                """
                INSERT INTO transactions (description, merchant_id, reconciled, date, statement_id, receipt_file_name, 
                lat, long, account_id, transfer_trans_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.description,
                    self.merchant_id,
                    self.reconciled,
                    None if self.date is None else self.date.strftime(date_format),
                    self.statement_id,
                    self.receipt_file_name,
                    self.lat,
                    self.long,
                    self.account_id,
                    self.transfer_trans_id,
                ),
            )

        con.commit()

    @staticmethod
    def get_all() -> list[Transaction]:
        """
        Gets a list of Transactions from all rows in the database.

        :return: A list of Transactions from all rows in the database.
        """
        _, cur = database.get_connection()

        cur.execute(
            """
            SELECT id, description, merchant_id, reconciled, date, statement_id, receipt_file_name, lat, long, 
                account_id, transfer_trans_id FROM transactions
            """
        )
        return list(Transaction(*data) for data in cur.fetchall())

    def __eq__(self, other: Transaction) -> bool:
        """
        Checks if this Transaction is equal to another Transaction.

        A Transaction is equal if all its fields except the sqlid are equal.

        :param other: The other Transaction to compare against this one.
        :return: True if the Transactions are equal, false if otherwise.
        """
        return (
            self.description == other.description
            and self.merchant_id == other.merchant_id
            and self.reconciled == other.reconciled
            and self.date == other.date
            and self.statement_id == other.statement_id
            and self.receipt_file_name == other.receipt_file_name
            and self.lat == other.lat
            and self.long == other.long
            and self.account_id == other.account_id
            and self.transfer_trans_id == other.transfer_trans_id
        )

    def merchant(self) -> Optional[Merchant.Merchant]:
        """
        Gets the Merchant of this Transaction.

        :return: Merchant of this Transaction.
        """
        try:
            return Merchant.Merchant.from_id(self.merchant_id)
        except ValueError:
            return None

    def statement(self) -> Optional[Statement.Statement]:
        """
        Gets the Statement this Transaction belongs to if it exists.

        :return: Statement this Transaction belongs to.
        """
        try:
            return Statement.Statement.from_id(self.statement_id)
        except ValueError:
            return None

    def account(self) -> Optional[Account.Account]:
        """
        Gets the Account this Transaction belongs to if it exists.

        :return: Account this Transaction belongs to.
        """
        try:
            return Account.Account.from_id(self.account_id)
        except ValueError:
            return None

    def transfer_trans(self) -> Optional[Transaction]:
        """
        Gets the transfer Transaction this Transaction is linked to if it exists.

        :return: Transfer Transaction this Transaction is linked to.
        """
        try:
            return Transaction.from_id(self.transfer_trans_id)
        except ValueError:
            return None

    def total_amount(self) -> float:
        """
        Gets the combined Amounts of this Transaction.

        :return: The combined Amounts of this Transaction.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT SUM(amount) FROM amounts WHERE transaction_id = ?", (self.sqlid,)
        )

        return cur.fetchone()[0]

    def amounts(self) -> list[Amount.Amount]:
        """
        Gets the list of Amounts that this Transaction has.

        :return: List of Amounts that this Transaction has.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT id, amount, description FROM amounts WHERE transaction_id = ?",
            (self.sqlid,),
        )

        query_results: list[tuple[int, float, str]] = cur.fetchall()
        amount_list: list[Amount.Amount] = []

        for sqlid, amount, description in query_results:
            amount_list.append(Amount.Amount(sqlid, amount, self.sqlid, description))

        return amount_list

    def split_amount(
        self,
        existing_amount_id: int,
        new_amount: float,
        description: Optional[str] = None,
    ) -> None:
        """
        Splits the new_amount from an existing Amount.

        :param existing_amount_id: ID of the existing Amount
        :param new_amount: New amount to split from the existing Amount
        :param description: Description of the new amount
        :raises ValueError: If the amount_id is invalid
        :raises ValueError: If the new_amount is greater or equal to the existing amount
        """
        con, cur = database.get_connection()

        # Get existing amount and ensure the new amount can be created.
        existing_amount: Amount.Amount = Amount.Amount.from_id(existing_amount_id)

        if existing_amount.transaction_id != self.sqlid:
            raise ValueError(
                f"This transaction does not have an amount with id = {existing_amount_id}."
            )

        if new_amount >= existing_amount.amount:
            raise ValueError(
                f"Cannot split ${new_amount} from existing amount ${existing_amount.amount}."
            )

        existing_amount.amount = existing_amount.amount - new_amount
        created_amount: Amount.Amount = Amount.Amount(
            None, new_amount, self.sqlid, description
        )

        existing_amount.sync()
        created_amount.sync()

    def combine_amount(
        self,
        first_amount_id: int,
        second_amount_id: int,
        new_description: Optional[str] = None,
    ) -> None:
        """
        Combines two amounts into one.

        :param first_amount_id: ID of the first Amount.
        :param second_amount_id: ID of the second Amount
        :param new_description: Description of the new Amount, if left blank the first amount description will be used.
        """

        first_amount: Amount.Amount = Amount.Amount.from_id(first_amount_id)
        second_amount: Amount.Amount = Amount.Amount.from_id(second_amount_id)

        if first_amount.transaction_id != self.sqlid:
            raise ValueError(
                f"Transaction with id = {self.sqlid} has no amount with id = {first_amount_id}."
            )

        if second_amount.transaction_id != self.sqlid:
            raise ValueError(
                f"Transaction with id = {self.sqlid} has no amount with id = {second_amount_id}."
            )

        first_amount.amount = first_amount.amount + second_amount.amount
        if new_description is not None:
            first_amount.description = new_description

        first_amount.sync()
        second_amount.delete()

    def tags(self) -> list[Tag.Tag]:
        """
        Gets the list of Tags that this Transaction has.

        :return: List of Tags that this Transaction has.
        """
        _, cur = database.get_connection()

        cur.execute(
            """
            SELECT tags.id, tags.name, tags.occasional
            FROM tags
            INNER JOIN amount_tags ON tags.id = amount_tags.tag_id
            INNER JOIN amounts ON amount_tags.amount_id = amounts.id
            INNER JOIN transactions ON amounts.transaction_id = transactions.id
            WHERE transactions.id = ?
            """,
            (self.sqlid,),
        )

        return list(Tag.Tag(*data) for data in cur.fetchall())
