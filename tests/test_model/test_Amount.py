import os
import shutil
from unittest import TestCase

from model.Amount import Amount
from model.Tag import Tag
from src.model import database
from tests.test_model import test_database, sample_database_1


class TestAmount(TestCase):

    expected_amounts: list[Amount] = [
        Amount(1, 20.54, 1, None),
        Amount(2, 1245.34, 2, None),
        Amount(3, 12.98, 3, None),
        Amount(4, 34.82, 4, "PC Parts"),
        Amount(5, 12.63, 4, "Textbook"),
        Amount(6, -100, 5, None),
        Amount(7, 100, 6, None),
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
        Tests Amount.from_id(sqlid: int)

        Prerequisite: test_get_all()
        """

        # Test valid amounts
        expected_amounts: list[Amount] = Amount.get_all()

        for expected_amount in expected_amounts:
            self.assertEqual(expected_amount, Amount.from_id(expected_amount.sqlid))

        # Test invalid amount
        with self.assertRaises(ValueError) as msg:
            Amount.from_id(-1)
        self.assertEqual("No amount with id = -1.", str(msg.exception))

        with self.assertRaises(ValueError) as msg:
            Amount.from_id(8)
        self.assertEqual("No amount with id = 8.", str(msg.exception))

    def test_sync(self):
        """
        Tests Amount.sync()

        Prerequisite: test_get_all() and test_from_id()
        """

        expected_amounts: list[Amount] = TestAmount.expected_amounts
        expected_amounts.append(Amount(8, 65.48, 4, "Box Fan"))

        # Test create new Amount
        amount: Amount = Amount(None, 65.48, 4, "Box Fan")
        amount.sync()

        actual_amounts: list[Amount] = Amount.get_all()
        self.assertEqual(len(TestAmount.expected_amounts), len(actual_amounts))
        for expected_amount, actual_amount in zip(expected_amounts, actual_amounts):
            self.assertEqual(expected_amount.sqlid, actual_amount.sqlid)
            self.assertEqual(expected_amount, actual_amount)

        # Update existing Amount
        expected_amounts[3] = Amount(4, 2.45, 3, "Gum separate from rest of purchase.")

        amount = Amount.from_id(4)
        amount.amount = 2.45
        amount.transaction_id = 3
        amount.description = "Gum separate from rest of purchase."

        amount.sync()

        actual_amounts: list[Amount] = Amount.get_all()
        self.assertEqual(len(TestAmount.expected_amounts), len(actual_amounts))
        for expected_amount, actual_amount in zip(expected_amounts, actual_amounts):
            self.assertEqual(expected_amount.sqlid, actual_amount.sqlid)
            self.assertEqual(expected_amount, actual_amount)

    def test_get_all(self):
        """
        Test Amount.get_all()

        Prerequisite: None
        """

        actual_amounts: list[Amount] = Amount.get_all()

        self.assertEqual(len(TestAmount.expected_amounts), len(actual_amounts))
        for expected_amount, actual_amount in zip(
            TestAmount.expected_amounts, actual_amounts
        ):
            self.assertEqual(expected_amount.sqlid, actual_amount.sqlid)
            self.assertEqual(expected_amount, actual_amount)

    # def test_transaction(self):
    #
    #     self.fail()

    def test_tags(self):
        """
        Tests Amount.tags()

        Prerequisite: test_from_id()
        """

        # Test with amount 1
        expected_tags: list[Tag] = [
            Tag(5, "Dating", False),
            Tag(7, "Eating Out", False),
        ]

        actual_tags: list[Tag] = Amount.from_id(1).tags()

        self.assertEqual(len(expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

        # Test with amount 2
        expected_tags: list[Tag] = [
            Tag(4, "University", False),
            Tag(10, "Personal", False),
        ]

        actual_tags: list[Tag] = Amount.from_id(2).tags()

        self.assertEqual(len(expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

        # Test with amount 4
        expected_tags: list[Tag] = [
            Tag(3, "Anarack", True),
        ]

        actual_tags: list[Tag] = Amount.from_id(4).tags()

        self.assertEqual(len(expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)
