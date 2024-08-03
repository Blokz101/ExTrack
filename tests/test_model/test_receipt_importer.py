"""
Tests the ReceiptImporter class.
"""

# mypy: ignore-errors
import os
import shutil
from pathlib import Path
from unittest import TestCase

from ddt import ddt, data, unpack  # type: ignore

from src import model
from src.model.receipt_importer import ReceiptImporter
from tests.test_model import (
    root_dir,
    sample_receipt_folder_1_path,
    test_receipt_folder_path,
)
from tests.test_model.sample_1_test_case import (
    Sample1TestCase,
    EXPECTED_IMPORTED_TRANSACTIONS,
)


@ddt
class TestReceiptImporter(Sample1TestCase):
    """
    Tests the ReceiptImporter class.
    """

    IMPORT_FOLDER_PATH: Path = root_dir / "temp_import_receipts_folder"
    """Path to folder where receipts are being imported from."""

    @data(
        [35.87278611111111, -78.62358055555555, [12, 11]],
        [35.87272222222222, -78.623825, [12, 11]],
        [35.7898, -78.67783333333334, [1]],
        [35.78339722222222, -78.67076944444445, [14, 5]],
        [34.99378333333333, -78.1388388888889, []],
        [34.56046944444444, -77.91750277777778, []],
        [35.783427777777774, -78.67078333333333, [14, 5]],
        [35.78339444444444, -78.67076944444445, [14, 5]],
        [35.78341666666667, -78.670775, [14, 5]],
        [35.864669444444445, -78.63806111111111, [17]],
        [35.840650000000004, -78.68097777777778, [18, 4]],
        [35.90484722222222, -78.60186666666667, [15]],
        [35.905741666666664, -78.59140833333333, [16, 7, 23]],
        [35.918055555555554, -78.96121111111111, [19]],
        [35.966769444444445, -78.95473611111112, []],
        [35.78478333333333, -78.69306944444445, [13]],
        [35.78346666666666, -78.67082222222223, [14, 5]],
    )
    @unpack
    def test_nearby_locations(self, lat: float, long: float, expected_ids: list[int]):
        """
        Tests ReceiptImporter.nearby_locations
        """
        self.assertEqual(
            expected_ids,
            [
                location[0].merchant_id
                for location in ReceiptImporter.nearby_locations(lat, long)
            ],
        )

    def test_create_transaction(self):
        """
        Tests ReceiptImporter.create_transaction
        """
        model.app_settings.settings["receipts_folder"] = str(
            sample_receipt_folder_1_path.absolute()
        )

        for expected_transaction, receipt_path in zip(
            EXPECTED_IMPORTED_TRANSACTIONS, sample_receipt_folder_1_path.iterdir()
        ):
            self.assertSqlEqual(
                expected_transaction, ReceiptImporter(receipt_path).create_transaction()
            )

    def test_move_photo(self):
        """
        Tests ReceiptImporter.create_transaction
        """
        # Setup
        if test_receipt_folder_path.exists():
            os.remove(test_receipt_folder_path)
        model.app_settings.settings["receipts_folder"] = str(
            test_receipt_folder_path.absolute()
        )

        # Create the folder receipts are being imported from and copy the sample receipts to it
        if not TestReceiptImporter.IMPORT_FOLDER_PATH.exists():
            TestReceiptImporter.IMPORT_FOLDER_PATH.mkdir()
        for file in sample_receipt_folder_1_path.iterdir():
            shutil.copyfile(file, TestReceiptImporter.IMPORT_FOLDER_PATH / file.name)

        # Test each receipt photo
        try:
            for receipt in TestReceiptImporter.IMPORT_FOLDER_PATH.iterdir():

                # Move the photo
                importer: ReceiptImporter = ReceiptImporter(receipt)
                previous_path: Path = importer.receipt_path
                importer.move_photo()

                # Check each photo was moved
                self.assertEqual(
                    model.app_settings.receipts_folder() / previous_path.name,
                    importer.receipt_path,
                )
                self.assertTrue(
                    (model.app_settings.receipts_folder() / previous_path.name).exists()
                )
                self.assertFalse(previous_path.exists())

        # Clean up
        finally:
            shutil.rmtree(TestReceiptImporter.IMPORT_FOLDER_PATH)
            shutil.rmtree(test_receipt_folder_path)


@ddt
class TestMathematicalReceiptImporter(TestCase):
    """
    Tests the math in the ReceiptImporter class.
    """

    @data(
        [
            35.782024162305845,
            -78.6330386592794,
            35.7751506287278,
            -78.61252189185353,
            1.2443,
        ],
        [
            35.792105170392304,
            -78.62127662239067,
            35.7751506287278,
            -78.61252189185353,
            1.2700,
        ],
        [
            35.047482699322934,
            -77.33606942526627,
            35.7751506287278,
            -78.61252189185353,
            87.7175,
        ],
    )
    @unpack
    def test_calculate_distance(
        self, lat1: float, long1: float, lat2: float, long2: float, expected: float
    ):
        """
        Tests the calculate_distance method.
        """
        self.assertAlmostEqual(
            expected,
            ReceiptImporter.calculate_distance(lat1, long1, lat2, long2),
            places=3,
        )
