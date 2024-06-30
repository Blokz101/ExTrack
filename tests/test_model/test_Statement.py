from datetime import datetime

from src.model.Transaction import Transaction
from src.model.Account import Account
from src.model.Statement import Statement
from tests.test_model.Sample1TestCase import Sample1TestCase
from src.model import date_format


class TestStatement(Sample1TestCase):

    expected_statements: list[Statement] = [
        Statement(1, datetime.strptime("2019-02-14 17:48:20", date_format), None, 1),
        Statement(2, datetime.strptime("2020-07-08 07:12:34", date_format), None, 1),
        Statement(3, datetime.strptime("2023-07-20 05:46:37", date_format), None, 1),
        Statement(4, "2018-12-21 08:21:34", None, 2),
        Statement(5, "2019-08-25 12:58:05", None, 2),
        Statement(6, "2021-04-22 09:01:52", None, 2),
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
        expected_statements.append(Statement(7, "2017-07-29 06:05:37", None, 1))

        # Test create new Statement
        statement: Statement = Statement(None, "2017-07-29 06:05:37", None, 1)
        statement.sync()

        self.assertSqlListEqual(expected_statements, Statement.get_all())
        self.assertEqual(7, statement.sqlid)

        # Update existing Statement
        expected_statements[3] = Statement(4, "2018-05-24 11:34:53", None, 2)

        statement = Statement.from_id(4)
        statement.date = datetime.strptime("2018-05-24 11:34:53", date_format)
        statement.path = None
        statement.account_id = 2

        statement.sync()

        self.assertSqlListEqual(expected_statements, Statement.get_all())
        self.assertEqual(4, statement.sqlid)

    def test_syncable(self):
        """
        Tests Statement.syncable() and Statement.sync()

        Prerequisite: test_get_all() and test_sync()
        """
        statement: Statement = Statement(None, None, None, None)

        self.assertEqual(
            ["date cannot be None.", "account_id cannot be None."], statement.syncable()
        )

        with self.assertRaises(RuntimeError) as msg:
            statement.sync()
        self.assertEqual("date cannot be None.", str(msg.exception))
        self.assertSqlListEqual(TestStatement.expected_statements, Statement.get_all())

        # Try to sync with required fields
        statement = Statement(date="2018-05-24 11:34:53", account_id=2)

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
                None,
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
