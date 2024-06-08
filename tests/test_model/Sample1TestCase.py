import os
import shutil
from unittest import TestCase

from src.model import database
from src.model.SqlObject import SqlObject
from tests.test_model import sample_database_1, test_database


class Sample1TestCase(TestCase):
    """
    Base class for all unit tests relating to sample_database_1.db
    """

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

    def assertSqlEqual(self, expected: SqlObject, second: SqlObject) -> None:
        """
        Asserts that two SqlObjects are equal and their IDs match.

        :param expected: First SqlObject to compare
        :param second: Second SqlObject to compare
        :return: True if the two SqlObjects are equal and their IDs are equal, false if otherwise
        """
        self.assertEqual(expected.sqlid, second.sqlid)
        self.assertEqual(expected, second)

    def assertSqlListEqual(
        self, expected_list: list[SqlObject], actual_list: list[SqlObject]
    ) -> None:
        """
        Asserts that two lists of SqlObjects are equal and their IDs match.

        :param expected_list: First list of SqlObject to compare
        :param actual_list: Second list of SqlObject to compare
        """
        self.assertEqual(len(expected_list), len(actual_list))
        for expected, actual in zip(expected_list, actual_list):
            self.assertSqlEqual(expected, actual)
