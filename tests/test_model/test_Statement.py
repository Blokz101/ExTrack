import shutil
import os
from datetime import datetime

from model.Account import Account
from model.Statement import Statement
from tests.test_model import test_database, sample_database_1
from src.model import database, date_format
from unittest import TestCase


class TestStatement(TestCase):

    expected_statements: list[Statement] = [
        Statement(1, datetime.strptime("2019-02-14 17:48:20", date_format), None, 1),
        Statement(2, datetime.strptime("2020-07-08 07:12:34", date_format), None, 1),
        Statement(3, datetime.strptime("2023-07-20 05:46:37", date_format), None, 1),
        Statement(4, "2018-12-21 08:21:34", None, 2),
        Statement(5, "2019-08-25 12:58:05", None, 2),
        Statement(6, "2021-04-22 09:01:52", None, 2),
    ]

    def setUp(self):
        """
        Copy sample database file and connect to it.
        """
        shutil.copyfile(sample_database_1, test_database)
        database.connect(test_database)

    def tearDown(self):
        """
        Close database and delete test file.
        """
        database.close()
        os.remove(test_database)

    def test_from_id(self):
        """
        Tests Statement.from_id(sqlid: int)

        Prerequisite: test_get_all()
        """

        # Test valid statements
        expected_statements: list[Statement] = Statement.get_all()

        for expected_statement in expected_statements:
            self.assertEqual(
                expected_statement, Statement.from_id(expected_statement.sqlid)
            )

        # Test invalid statements
        with self.assertRaises(ValueError) as msg:
            Statement.from_id(-1)
        self.assertEqual("No statement with id = -1.", str(msg.exception))

        with self.assertRaises(ValueError) as msg:
            Statement.from_id(7)
        self.assertEqual("No statement with id = 7.", str(msg.exception))

    def test_sync(self):
        """
        Tests Statement.sync()

        Prerequisite: test_get_all() and from_id(sqlid: int)
        """

        expected_statements: list[Statement] = TestStatement.expected_statements.copy()
        expected_statements.append(Statement(7, "2017-07-29 06:05:37", None, 1))

        # Test create new Statement
        statement: Statement = Statement(None, "2017-07-29 06:05:37", None, 1)
        statement.sync()

        actual_statements: list[Statement] = Statement.get_all()
        self.assertEqual(len(expected_statements), len(actual_statements))
        for expected_statement, actual_statement in zip(
            expected_statements, actual_statements
        ):
            self.assertEqual(expected_statement.sqlid, actual_statement.sqlid)
            self.assertEqual(expected_statement, actual_statement)

        # Update existing Statement
        expected_statements[3] = Statement(4, "2018-05-24 11:34:53", None, 2)

        statement = Statement.from_id(4)
        statement.date = datetime.strptime("2018-05-24 11:34:53", date_format)
        statement.path = None
        statement.account_id = 2

        statement.sync()

        actual_statements: list[Statement] = Statement.get_all()
        self.assertEqual(len(expected_statements), len(actual_statements))
        for expected_statement, actual_statement in zip(
            expected_statements, actual_statements
        ):
            self.assertEqual(expected_statement.sqlid, actual_statement.sqlid)
            self.assertEqual(expected_statement, actual_statement)

    def test_get_all(self):
        """
        Tests Statement.get_all()

        Prerequisite: None
        """

        actual_statements: list[Statement] = Statement.get_all()

        self.assertEqual(len(TestStatement.expected_statements), len(actual_statements))
        for expected_statement, actual_statement in zip(
            TestStatement.expected_statements, actual_statements
        ):
            self.assertEqual(expected_statement.sqlid, actual_statement.sqlid)
            self.assertEqual(expected_statement, actual_statement)

    # def test_transactions(self):
    #     """
    #     Tests Statement.transactions()
    #
    #     Prerequisite: test_from_id()
    #     """
    #
    #     self.fail()

    def test_account(self):
        """
        Tests Statement.account()

        Prerequisite:
        """

        self.assertEqual(
            Account(1, "Checking", 2, 3, 7), Statement.from_id(2).account()
        )

        self.assertEqual(Account(2, "Savings", 3, 1, 5), Statement.from_id(5).account())
