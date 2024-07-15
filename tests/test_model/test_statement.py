"""
Tests the Statement class.
"""

# mypy: ignore-errors
from datetime import datetime

from src.model import date_format
from src.model.account import Account
from src.model.statement import Statement
from src.model.transaction import Transaction
from tests.test_model.sample_1_test_case import Sample1TestCase


class TestStatement(Sample1TestCase):
    """
    Tests the Statement class.
    """

    expected_statements: list[Statement] = [
        Statement(
            1,
            datetime.strptime("2019-02-14 00:00:00", date_format),
            "BOA.csv",
            1,
            3235.45,
            True,
        ),
        Statement(
            2,
            datetime.strptime("2020-07-08 00:00:00", date_format),
            "BOA1.csv",
            1,
            66.45,
            True,
        ),
        Statement(
            3,
            datetime.strptime("2023-07-20 00:00:00", date_format),
            "NEWBOA.csv",
            1,
            3825.01,
            False,
        ),
        Statement(4, "2018-12-21 00:00:00", "DISCOVER.csv", 2, 517.01, True),
        Statement(5, "2019-08-25 00:00:00", None, 2, 320.93, True),
        Statement(6, "2021-04-22 00:00:00", "NEWDISCOVER.csv", 2, 500.33, False),
    ]

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
        expected_statements.append(
            Statement(
                7,
                "2017-07-29 06:05:37",
                "NEWESTBOA.csv",
                1,
                4323.61,
                False,
            )
        )

        # Test create new Statement
        statement: Statement = Statement(
            None,
            "2017-07-29 06:05:37",
            "NEWESTBOA.csv",
            1,
            4323.61,
            False,
        )
        statement.sync()

        self.assertSqlListEqual(expected_statements, Statement.get_all())
        self.assertEqual(7, statement.sqlid)

        # Update existing Statement
        expected_statements[3] = Statement(
            4, "2018-05-24 11:34:53", None, 2, 517.01, True
        )

        statement = Statement.from_id(4)
        statement.date = datetime.strptime("2018-05-24 11:34:53", date_format)
        statement.file_name = None
        statement.account_id = 2
        statement.starting_balance = 517.01
        statement.reconciled = True

        statement.sync()

        self.assertSqlListEqual(expected_statements, Statement.get_all())
        self.assertEqual(4, statement.sqlid)

    def test_syncable(self):
        """
        Tests Statement.syncable() and Statement.sync()

        Prerequisite: test_get_all() and test_sync()
        """
        statement: Statement = Statement(
            None,
            None,
            "NEWSTATEMENT.csv",
            None,
            None,
            None,
        )

        self.assertEqual(
            [
                "date cannot be None.",
                "account_id cannot be None.",
                "starting_balance cannot be None.",
                "reconciled cannot be None.",
            ],
            statement.syncable(),
        )

        with self.assertRaises(RuntimeError) as msg:
            statement.sync()
        self.assertEqual("date cannot be None.", str(msg.exception))
        self.assertSqlListEqual(TestStatement.expected_statements, Statement.get_all())

        # Try to sync with required fields
        statement = Statement(
            date="2018-05-24 11:34:53",
            account_id=2,
            starting_balance=842.45,
            reconciled=False,
        )

        self.assertIsNone(statement.syncable())

        statement.sync()
        self.assertSqlListEqual(
            TestStatement.expected_statements + [statement], Statement.get_all()
        )

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

    def test_transactions(self):
        """
        Tests Statement.transactions()

        Prerequisite: test_from_id()
        """

        # Test with statement 1
        expected_transactions: list[Transaction] = [
            Transaction(
                3,
                "DND Dice",
                9,
                True,
                datetime.strptime("2023-05-04 23:44:29", date_format),
                1,
                "IMAGE22.png",
                None,
                None,
                1,
                None,
            ),
            Transaction(
                4,
                "Things from Amazon",
                3,
                True,
                datetime.strptime("2020-09-28 19:26:10", date_format),
                1,
                None,
                None,
                None,
                1,
                None,
            ),
        ]
        self.assertSqlListEqual(
            expected_transactions, Statement.from_id(1).transactions()
        )

        # Test with new Statement
        self.assertEqual([], Statement().transactions())

    def test_account(self):
        """
        Tests Statement.account()

        Prerequisite:
        """

        self.assertEqual(
            Account(1, "Checking", 2, 3, 7), Statement.from_id(2).account()
        )

        self.assertEqual(Account(2, "Savings", 3, 1, 5), Statement.from_id(5).account())

        # Test with new Statement
        self.assertEqual(None, Statement().account())
