import os
from typing import List, Any
from unittest import TestCase

from model import Database
from tests.test_model import test_database, root_dir


class TestDatabase(TestCase):

    def setUp(self):
        """
        Deletes the test database if it exists.
        """

        if test_database.exists():
            os.remove(test_database)

    def tearDown(self):
        """
        Deletes the  test database if it exists.
        """
        if Database().is_connected():
            Database().close()

        if test_database.exists():
            os.remove(test_database)

    def test_database(self):
        """
        Tests the constructor and Database.is_connected().

        Prerequisite: test_create_new()
        """
        # Create database that is not connected.
        database: Database = Database()
        self.assertFalse(database.is_connected())

        # Create database object connected to file that does not exist.
        with self.assertRaises(FileNotFoundError):
            Database().connect(root_dir / "this_database_does_not_exist.db")

        # Create database that is connected
        database = Database()
        database.create_new(test_database)
        self.assertTrue(database.is_connected())

        self.assertTrue(Database(test_database).is_connected())

    def test_create_new(self):
        """
        Test Database.create_new(database_path: Optional[Path])

        Prerequisite: None
        """
        # Database that does not exist
        self.assertFalse(test_database.exists())
        with self.assertRaises(RuntimeError) as msg:
            Database().get_connection()
        self.assertEqual("Not connected to a database.", str(msg.exception))

        # Create database
        database: Database = Database()
        database.create_new(test_database)

        self.assertTrue(test_database.exists())
        con, cur = database.get_connection()
        self.assertTrue(con is not None)
        self.assertTrue(cur is not None)

        # Check that database has the correct structure.
        expected_tables: List[str] = [
            "transactions",
            "amounts",
            "accounts",
            "statements",
            "merchants",
            "locations",
            "tags",
            "amount_tags",
            "mer_tag_defaults",
        ]
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        actual_tables: list[Any] = list([table[0] for table in cur.fetchall()])

        self.assertEqual(1 + len(expected_tables), len(actual_tables))
        for table in expected_tables:
            self.assertTrue(
                table in actual_tables,
                f"Expected table '{table}' not found in the actual tables.",
            )

        # Attempt to create database that already exists
        with self.assertRaises(FileExistsError):
            database.create_new(test_database)
