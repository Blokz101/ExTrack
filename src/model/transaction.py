"""
Contains the Transaction class which represents a transaction in the SQL database.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Union, cast, Any

from src.model import date_format, database, account, merchant, statement, tag, amount
from src.model.sql_object import SqlObject


# pylint: disable=too-many-instance-attributes
class Transaction(SqlObject):
    """
    Represents a Transaction in the SQL database.
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        sqlid: Optional[int] = None,
        description: Optional[str] = None,
        merchant_id: Optional[int] = None,
        reconciled: Optional[Union[bool, int]] = None,
        date: Optional[Union[str, datetime]] = None,
        statement_id: Optional[int] = None,
        receipt_file_name: Optional[str] = None,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        account_id: Optional[int] = None,
        transfer_trans_id: Optional[int] = None,
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
        self.reconciled: Optional[bool]
        """True if this Transaction has been reconciled, false otherwise."""
        if reconciled is not None:
            self.reconciled = (
                reconciled if isinstance(reconciled, bool) else reconciled == 1
            )
        else:
            self.reconciled = None
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
            """
            SELECT id, description, merchant_id, reconciled, date, statement_id,
            receipt_file_name, lat, long,  account_id, transfer_trans_id
            FROM transactions
            WHERE id = ?""",
            (sqlid,),
        )

        data: object = cur.fetchone()

        if data is None:
            raise ValueError(f"No transaction with id = {sqlid}.")
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
        ) = cast(list, data)
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
        Syncs this Transaction to the database by updating the database. If the Transaction is
        not in the database it is added.

        Syncing only updates edited instance variables. Sync does not need to be called after
        another function that updates the database, that function will sync on its own.

        :raises RuntimeError: If this Transaction is not syncable
        """
        super().sync()
        con, cur = database.get_connection()

        if self.exists():
            cur.execute(
                """
                UPDATE transactions
                SET description = ?, merchant_id = ?, reconciled = ?, date = ?, statement_id = ?,
                receipt_file_name = ?, lat = ?, long = ?, account_id = ?, transfer_trans_id = ?
                WHERE id = ?
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
                INSERT INTO transactions (description, merchant_id, reconciled, date, 
                statement_id, receipt_file_name, lat, long, account_id, transfer_trans_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            self.sqlid = cur.lastrowid

        con.commit()

    def syncable(self) -> Optional[list[str]]:
        """
        Checks if this Transaction has non-null values for all required fields.

        :return: None if this Transaction is syncable or a list of error messages if it is not.
        """
        if self.description == "":
            self.description = None

        if self.receipt_file_name == "":
            self.receipt_file_name = None

        errors: list[str] = []

        if self.reconciled is None:
            errors.append("reconciled cannot be None.")

        if self.account_id is None:
            errors.append("account_id cannot be None.")

        return None if len(errors) == 0 else errors

    @staticmethod
    def get_all() -> list[Transaction]:
        """
        Gets a list of Transactions from all rows in the database.

        :return: A list of Transactions from all rows in the database.
        """
        _, cur = database.get_connection()

        cur.execute(
            """
            SELECT id, description, merchant_id, reconciled, date, statement_id, 
            receipt_file_name, lat, long, account_id, transfer_trans_id
            FROM transactions
            """
        )
        return list(Transaction(*data) for data in cur.fetchall())

    def __eq__(self, other: Any) -> bool:
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

    def merchant(self) -> Optional[merchant.Merchant]:
        """
        Gets the Merchant of this Transaction.

        :return: Merchant of this Transaction.
        """
        if not self.merchant_id:
            return None
        return merchant.Merchant.from_id(self.merchant_id)

    def statement(self) -> Optional[statement.Statement]:
        """
        Gets the Statement this Transaction belongs to if it exists.

        :return: Statement this Transaction belongs to.
        """
        if self.statement_id is None:
            return None
        return statement.Statement.from_id(self.statement_id)

    def account(self) -> Optional[account.Account]:
        """
        Gets the Account this Transaction belongs to if it exists.

        :return: Account this Transaction belongs to.
        """
        if self.account_id is None:
            return None
        return account.Account.from_id(self.account_id)

    def transfer_trans(self) -> Optional[Transaction]:
        """
        Gets the transfer Transaction this Transaction is linked to if it exists.

        :return: Transfer Transaction this Transaction is linked to.
        """
        if self.transfer_trans_id is None:
            return None
        return Transaction.from_id(self.transfer_trans_id)

    def total_amount(self) -> float:
        """
        Gets the combined Amounts of this Transaction.

        :return: The combined Amounts of this Transaction.
        """
        _, cur = database.get_connection()

        cur.execute(
            "SELECT SUM(amount) FROM amounts WHERE transaction_id = ?", (self.sqlid,)
        )

        result: Optional[float] = cur.fetchone()[0]
        return 0 if result is None else result

    def amounts(self) -> list[amount.Amount]:
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
        amount_list: list[amount.Amount] = []

        for sqlid, amount_value, description in query_results:
            amount_list.append(
                amount.Amount(sqlid, amount_value, self.sqlid, description)
            )

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
        # Get existing amount and ensure the new amount can be created.
        existing_amount: amount.Amount = amount.Amount.from_id(existing_amount_id)

        if existing_amount.transaction_id != self.sqlid:
            raise ValueError(
                f"This transaction does not have an amount with id = {existing_amount_id}."
            )

        if new_amount >= existing_amount.amount:  # type: ignore
            raise ValueError(
                f"Cannot split ${new_amount} from existing amount ${existing_amount.amount}."
            )

        existing_amount.amount = existing_amount.amount - new_amount  # type: ignore
        created_amount: amount.Amount = amount.Amount(
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
        :param new_description: Description of the new Amount, if left blank the first amount
        description will be used.
        """

        first_amount: amount.Amount = amount.Amount.from_id(first_amount_id)
        second_amount: amount.Amount = amount.Amount.from_id(second_amount_id)

        if first_amount.transaction_id != self.sqlid:
            raise ValueError(
                f"Transaction with id = {self.sqlid} has no amount with id = {first_amount_id}."
            )

        if second_amount.transaction_id != self.sqlid:
            raise ValueError(
                f"Transaction with id = {self.sqlid} has no amount with id = {second_amount_id}."
            )

        first_amount.amount = first_amount.amount + second_amount.amount  # type: ignore
        if new_description is not None:
            first_amount.description = new_description

        first_amount.sync()
        second_amount.delete()

    def tags(self) -> list[tag.Tag]:
        """
        Gets the list of Tags that this Transaction has.

        :return: List of Tags that this Transaction has.
        """
        _, cur = database.get_connection()

        cur.execute(
            """
            SELECT tags.id, tags.name, tags.occasional, tags.rule
            FROM tags
            INNER JOIN amount_tags ON tags.id = amount_tags.tag_id
            INNER JOIN amounts ON amount_tags.amount_id = amounts.id
            INNER JOIN transactions ON amounts.transaction_id = transactions.id
            WHERE transactions.id = ?
            """,
            (self.sqlid,),
        )

        return list(tag.Tag(*data) for data in cur.fetchall())

    def delete(self) -> None:
        """
        Deletes this transaction.
        """
        if not self.exists():
            raise RuntimeError("Cannot delete a transaction that does not exist.")

        transfer_trans: Optional[Transaction] = self.transfer_trans()
        if transfer_trans is not None:
            transfer_trans.transfer_trans_id = None
            transfer_trans.sync()

        con, cur = database.get_connection()

        cur.execute("DELETE FROM transactions WHERE id = ?", (self.sqlid,))

        con.commit()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({", ".join(str(x) for x in [
            self.sqlid,
            self.description,
            self.merchant_id,
            self.reconciled,
            self.date,
            self.statement_id,
            self.receipt_file_name,
            self.lat,
            self.long,
            self.account_id,
            self.transfer_trans_id
        ])})"
