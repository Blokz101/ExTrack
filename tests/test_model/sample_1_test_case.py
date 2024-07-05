"""
Contains the Sample1TestCase class which is a base class for all unit tests relating to
sample_database_1.db.
"""

# mypy: ignore-errors
import os
import shutil
from unittest import TestCase

from src.model import database
from src.model.sql_object import SqlObject
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

    # pylint: disable=invalid-name
    def assertSqlEqual(self, expected: SqlObject, actual: SqlObject) -> None:
        """
        Asserts that two SqlObjects are equal and their IDs match.

        :param expected: Expected SqlObject
        :param actual: Actual SqlObjet
        :return: True if the two SqlObjects are equal and their IDs are equal, false if otherwise
        """
        self.assertEqual(expected.sqlid, actual.sqlid)
        self.assertEqual(expected, actual)

    # pylint: disable=invalid-name
    def assertSqlListEqual(
        self,
        expected_list: list[SqlObject],
        actual_list: list[SqlObject],
        strict_order: bool = True,
    ) -> None:
        """
        Asserts that two lists of SqlObjects are equal and their IDs match.
        To use non strict_order each SqlObject must have a sqlid set.

        :param expected_list: Expected list of SqlObject
        :param actual_list: Actual list of SqlObject
        :param strict_order: True if the order of the lists must be the same, false if they can
        be different
        """
        self.assertEqual(len(expected_list), len(actual_list))

        # Ensure order
        if strict_order:
            for expected, actual in zip(expected_list, actual_list):
                self.assertSqlEqual(expected, actual)

        # Sort objects by their sqlid then call this function with strict_order=True
        else:
            sorted_expected_list: list[SqlObject] = expected_list.copy()
            sorted_actual_list: list[SqlObject] = actual_list.copy()

            sorted_expected_list.sort(key=lambda x: x.sqlid)  # type: ignore
            sorted_actual_list.sort(key=lambda x: x.sqlid)  # type: ignore

            self.assertSqlListEqual(
                sorted_expected_list, sorted_actual_list, strict_order=True
            )
