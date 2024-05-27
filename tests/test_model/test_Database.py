import os
from unittest import TestCase

from model import Database
from tests.test_model import test_database, root_dir


class TestDatabase(TestCase):

    def setUp(self):
        if test_database.exists():
            os.remove(test_database)

    def tearDown(self):
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
        # Create database
        self.assertFalse(test_database.exists())

        database: Database = Database()
        database.create_new(test_database)

        self.assertTrue(test_database.exists())

        # Attempt to create database that already exists
        with self.assertRaises(FileExistsError):
            database.create_new(test_database)

    def test_get_connection(self):
        """
        Tests Database.get_connection()

        Prerequisite: test_create_new and test_database
        """

        database: Database = Database()

        # Test get_connection without a connection
        self.assertFalse(database.is_connected())
        with self.assertRaises(RuntimeError):
            database.get_connection()

        # Test get_connection with connection
        database = Database()

        database.create_new(test_database)

        self.assertTrue(database.is_connected())
        con, cur = database.get_connection()
        self.assertTrue(con is not None)
        self.assertTrue(cur is not None)
