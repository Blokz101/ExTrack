"""
Contains the Database class which provides utility for interacting with an SQLite database.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from sqlite3 import Cursor, Connection
from typing import Optional


class Database:
    """
    SQL Database utility.
    """

    def __init__(self, database_path: Optional[Path] = None) -> None:
        """
        :param database_path: Path to the database.
        """
        self._connection: Optional[Connection] = None
        self._cursor: Optional[Cursor] = None
        self.path: Optional[Path] = database_path

        if database_path is not None:
            self.connect(database_path)

    def create_new(self, database_path: Path) -> None:
        """
        Creates a new database.

        :param database_path: Path that the database should be created at.
        :raises FileExistsError: If the database already exists.
        """

        if database_path.exists() and database_path.is_file():
            raise FileExistsError("Database already exists.")

        self.connect(database_path, create=True)
        con, cur = self.get_connection()

        with open(
            Path(__file__).parent / "database_creation_script.sql",
            mode="r",
            encoding="utf-8",
        ) as creation_file:
            creation_script: str = creation_file.read()
            creation_commands: list[str] = creation_script.split(";")

            for command in creation_commands:
                cur.execute(command)

        con.commit()

    def connect(self, database_path: Path, create: bool = False) -> None:
        """
        Attempt to connect to the database to generate the connection and cursor objects.

        :param database_path: Path to the database.
        :param create: When true, allows this method to create a new database.
        :raises FileExistsError: If the database does not exist and create is False.
        """
        if not database_path.exists() and not create:
            raise FileNotFoundError("Database does not exist.")

        self.path = database_path
        self._connection = sqlite3.connect(self.path)
        self._cursor = self._connection.cursor()
        self._cursor.execute("PRAGMA foreign_keys = ON;")

    def is_connected(self) -> bool:
        """
        Checks if the database is connected.

        :return: True if the database is connected, false if otherwise.
        """
        return self._connection is not None and self._cursor is not None

    def get_connection(self) -> tuple[Connection, Cursor]:
        """
        Gets the database connection and cursor.

        :return: Database connection and cursor.
        :raises RuntimeError: If not connected to a database.
        """
        if self._connection is None or self._cursor is None:
            raise RuntimeError("Not connected to a database.")

        return self._connection, self._cursor

    def close(self) -> None:
        """
        Closes the connection.
        """
        if self._connection is not None:
            self._connection.close()
            self.path = None
            self._connection = None
            self._cursor = None

    def __del__(self) -> None:
        """
        Close database connection.
        """

        if self._connection is not None:
            self._connection.close()
