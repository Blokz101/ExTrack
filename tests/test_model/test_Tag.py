import os
import shutil
from unittest import TestCase

from model.Merchant import Merchant
from src.model import database
from src.model.Tag import Tag
from tests.test_model import test_database, sample_database_1


class TestTag(TestCase):

    expected_tags: list[Tag] = [
        Tag(1, "Groceries", False),
        Tag(2, "Gas", False),
        Tag(3, "Anarack", True),
        Tag(4, "University", False),
        Tag(5, "Dating", False),
        Tag(6, "Third Party Transaction", False),
        Tag(7, "Eating Out", False),
        Tag(8, "Winter Park Trip", True),
        Tag(9, "The Maze Trip", True),
        Tag(10, "Personal", False),
        Tag(11, "Coffee", False),
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
        Tests Tag.from_id(sqlid: int)

        Prerequisite: test_get_all()
        """

        # Test valid tags
        expected_tags: list[Tag] = Tag.get_all()

        for expected_tag in self.expected_tags:
            self.assertEqual(expected_tag, Tag.from_id(expected_tag.sqlid))

        # Test invalid tags
        with self.assertRaises(ValueError) as msg:
            Tag.from_id(-1)
        self.assertEqual("No tag with id = -1.", str(msg.exception))

        with self.assertRaises(ValueError) as msg:
            Tag.from_id(12)
        self.assertEqual("No tag with id = 12.", str(msg.exception))

    def test_sync(self):
        """
        Tests Tag.sync()

        Prerequisite: test_get_all() and test_from_id()
        """

        expected_tags: list[Tag] = TestTag.expected_tags
        expected_tags.append(Tag(12, "Other", False))

        # Test create new Tag
        tag: Tag = Tag(None, "Other", False)
        tag.sync()

        actual_tags: list[Tag] = Tag.get_all()
        self.assertEqual(len(expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

        # Update existing Merchant
        expected_tags[5] = Tag(6, "Christmas Gifts", True)

        tag = Tag.from_id(6)
        tag.name = "Christmas Gifts"
        tag.occasional = True

        tag.sync()

        actual_tags: list[Tag] = Tag.get_all()
        self.assertEqual(len(expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

    def test_get_all(self):
        """
        Tests Tag.get_all()

        Prerequisite: None
        """

        actual_tags: list[Tag] = Tag.get_all()

        self.assertEqual(len(TestTag.expected_tags), len(actual_tags))
        for expected_tag, actual_tag in zip(TestTag.expected_tags, actual_tags):
            self.assertEqual(expected_tag.sqlid, actual_tag.sqlid)
            self.assertEqual(expected_tag, actual_tag)

    def test_default_merchants(self):
        """
        Tests Tag.default_merchants()

        Prerequisite: test_from_id
        """

        # Test with Personal
        expected_merchants: list[Merchant] = [
            Merchant(4, "Apple", False, None),
            Merchant(8, "Bambu Labs", True, None),
            Merchant(9, "Etsy", True, None),
        ]

        actual_merchants: list[Merchant] = Tag.from_id(10).default_merchants()

        self.assertEqual(len(expected_merchants), len(actual_merchants))
        for expected_merchant, actual_merchant in zip(
            expected_merchants, actual_merchants
        ):
            self.assertEqual(expected_merchant.sqlid, actual_merchant.sqlid)
            self.assertEqual(expected_merchant, actual_merchant)

        # Test with Eating Out
        expected_merchants = [
            Merchant(1, "Penn Station", False, None),
            Merchant(2, "Outback Steak House", False, None),
        ]

        actual_merchants = Tag.from_id(7).default_merchants()

        self.assertEqual(len(expected_merchants), len(actual_merchants))
        for expected_merchant, actual_merchant in zip(
            expected_merchants, actual_merchants
        ):
            self.assertEqual(expected_merchant.sqlid, actual_merchant.sqlid)
            self.assertEqual(expected_merchant, actual_merchant)

        # Test with Coffee
        expected_merchants = [
            Merchant(5, "Port City Java", False, None),
        ]

        actual_merchants = Tag.from_id(11).default_merchants()

        self.assertEqual(len(expected_merchants), len(actual_merchants))
        for expected_merchant, actual_merchant in zip(
            expected_merchants, actual_merchants
        ):
            self.assertEqual(expected_merchant.sqlid, actual_merchant.sqlid)
            self.assertEqual(expected_merchant, actual_merchant)

    # def test_amounts(self):
    #
    #     self.fail()
