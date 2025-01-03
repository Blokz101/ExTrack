import math
from datetime import datetime
from pathlib import Path
from typing import Optional
import re

from PIL import Image
from PIL.ExifTags import TAGS

from src import model
from src.model.location import Location
from src.model.transaction import Transaction
from src.view.popup import ClosedStatus
from src.view.transaction_popup import TransactionPopup


class ReceiptImporter:
    """
    Class that manages the import process of a receipt photo.
    """

    SUPPORTED_FILE_TYPES: list[str] = [".jpg", ".jpeg", ".png"]
    """List of file extensions that are supported for receipt photos."""

    merchant_locations: Optional[list[Location]] = None
    """List of all merchant locations, used to reduce the number of database queries."""

    def __init__(self, receipt_path: Path) -> None:

        self.receipt_path = receipt_path
        """Location the receipt photo is stored."""

        self.lat: Optional[float] = None
        self.long: Optional[float] = None
        self.description: Optional[str] = None
        self.date: Optional[datetime] = None
        self.possible_locations: Optional[list[tuple[Location, float]]] = None

        self._read_exif_data()

    def _read_exif_data(self) -> None:
        """
        Reads the exif data from the receipt photo and stores it in instance variables.
        """
        if not model.app_settings.receipts_folder().exists():
            model.app_settings.receipts_folder().mkdir()

        if not self.receipt_path.exists():
            return

        # Parse each receipt photo
        with Image.open(self.receipt_path) as img:
            exif_data: Image.Exif = img.getexif()

            # Get data ids
            gps_id: int = next(tag for tag, name in TAGS.items() if name == "GPSInfo")
            img_desc_id: int = next(
                tag for tag, name in TAGS.items() if name == "ImageDescription"
            )
            date_id: int = next(tag for tag, name in TAGS.items() if name == "DateTime")

            # Get list of possible locations and set merchant id
            try:
                gps_info: dict = exif_data.get_ifd(gps_id)
                self.lat = ReceiptImporter._decimal_coords(gps_info[2], gps_info[1])
                self.long = ReceiptImporter._decimal_coords(gps_info[4], gps_info[3])

                self.possible_locations = ReceiptImporter.nearby_locations(
                    self.lat, self.long  # type: ignore
                )
            except KeyError:
                pass

            # Get date data
            try:
                self.date = datetime.strptime(exif_data[date_id], "%Y:%m:%d %H:%M:%S")
            except KeyError:
                pass

            # Get description data
            try:
                self.description = (
                    exif_data[img_desc_id].strip()
                    if img_desc_id in exif_data.keys()
                    else None
                )
            except KeyError:
                pass

    def create_transaction(self) -> Transaction:
        """
        Creates a transaction from the receipt data.

        :return: Transaction created from the receipt data
        """
        merchant_id: Optional[int] = None
        if self.possible_locations is not None and len(self.possible_locations) > 0:
            nearest_location = self.possible_locations[0]
            if nearest_location[1] <= model.app_settings.location_scan_radius():
                merchant_id = nearest_location[0].merchant_id

        return Transaction(
            sqlid=None,
            description=self.description,
            merchant_id=merchant_id,
            reconciled=False,
            date=self.date,
            statement_id=None,
            receipt_file_name=self.receipt_path.name,
            lat=self.lat,
            long=self.long,
            account_id=None,
            transfer_trans_id=None,
        )

    def move_photo(self, trans: Optional[Transaction] = None) -> None:
        """
        Moves the receipt photo to the ExTract storage folder.

        :param trans: Transaction object that has been synced to the database, used to update the transaction if the photo must be renamed
        """
        new_path: Path = model.app_settings.receipts_folder() / self.receipt_path.name
        new_path_stem: str = new_path.stem

        # Create a unique file name if the file name is taken
        identical_path_index: int = 0
        while new_path.exists():
            if not trans.exists():
                raise ValueError(
                    "Cannot move receipt photo corresponding to a transaction that is not in the database."
                )

            identical_path_index += 1
            new_path = (
                new_path.parent
                / f"{new_path_stem}_{identical_path_index}{new_path.suffix}"
            )

        # Sync the path change to the database if required
        if identical_path_index != 0:
            trans.receipt_file_name = new_path.name
            trans.sync()

        # Move the photo
        self.receipt_path.rename(new_path)
        self.receipt_path = new_path

    @staticmethod
    def batch_import(path_list: list[Path]) -> None:
        """
        Imports a batch of receipt photos.

        :param path_list: List of paths to receipt photos
        """
        for path in path_list:

            importer: ReceiptImporter = ReceiptImporter(path)
            popup: TransactionPopup = TransactionPopup(
                importer.create_transaction(),
                import_folder=path.parent,
                merchant_order=list(
                    x[0].merchant().sqlid for x in importer.possible_locations
                ),
            )
            popup.event_loop()

            if popup.closed_status == ClosedStatus.OPERATION_SUCCESS:
                importer.move_photo(popup.trans)

            if popup.closed_status == ClosedStatus.OPERATION_CANCELED:
                return

    @staticmethod
    def get_importable_photos(folder: Path) -> list[Path]:
        """
        Gets all importable photos from a folder.

        :param folder: Folder to get importable photos from
        :return: List of importable photos
        """
        return [
            file
            for file in folder.iterdir()
            if file.suffix in ReceiptImporter.SUPPORTED_FILE_TYPES
        ]

    @staticmethod
    def nearby_locations(lat: float, long: float) -> list[tuple[Location, float]]:
        """
        Gets all merchant locations near a given location.

        :param lat: Latitude
        :param long: Longitude
        :return: List of merchant locations near the given location and their distances to the
        specified location
        """
        possible_locations: list[tuple[Location, float]] = []

        # Create a list of all locations and their distance to the specified coordinates
        for location in Location.get_all():
            if location.lat is None or location.long is None:
                raise RuntimeError(
                    f"Location id = {location.sqlid} is missing coordinates."
                )
            distance_to_location: float = ReceiptImporter.calculate_distance(
                location.lat, location.long, lat, long
            )
            possible_locations.append((location, distance_to_location))

        # Sort all locations by distance and remove duplicates
        possible_locations.sort(key=lambda x: x[1])
        used_merchant_ids: list[int] = []
        for index, (location, _) in enumerate(possible_locations):
            if location.merchant_id in used_merchant_ids:
                possible_locations.pop(index)
            else:
                used_merchant_ids.append(location.merchant_id)

        return possible_locations

    @staticmethod
    def calculate_distance(
        lat1: float, long1: float, lat2: float, long2: float
    ) -> float:
        """
        Gets the distance between two sets of coordinates.

        :return: Distance between two coordinates in miles
        """

        d_lat: float = (lat2 - lat1) * math.pi / 180.0
        d_lon: float = (long2 - long1) * math.pi / 180.0

        # convert to radians
        lat1_rad: float = lat1 * math.pi / 180.0
        lat2_rad: float = lat2 * math.pi / 180.0

        # apply formulae
        a: float = pow(math.sin(d_lat / 2), 2) + pow(math.sin(d_lon / 2), 2) * math.cos(
            lat1_rad
        ) * math.cos(lat2_rad)
        rad: float = 3958.8
        c: float = 2 * math.asin(math.sqrt(a))
        return rad * c

    @staticmethod
    def _decimal_coords(coords, ref):
        decimal_degrees = (
            float(coords[0]) + float(coords[1]) / 60 + float(coords[2]) / 3600
        )
        if ref in ["S", "W"]:
            decimal_degrees = -1 * decimal_degrees
        return decimal_degrees
