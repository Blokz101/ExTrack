import math
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image
from PIL.ExifTags import TAGS

from src.model import app_settings
from src.model.location import Location
from src.model.transaction import Transaction


class ReceiptImporter:
    """
    Class that manages the import process of a receipt photo.
    """

    SUPPORTED_FILE_TYPES: list[str] = [".jpg", ".jpeg", ".png"]
    """List of file extensions that are supported for receipt photos."""

    merchant_locations: Optional[list[Location]] = None
    """List of all merchant locations so they are not queried multiple times."""

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
        if not app_settings.receipts_folder().exists():
            app_settings.receipts_folder().mkdir()

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
        return Transaction(
            sqlid=None,
            description=self.description,
            merchant_id=(
                None
                if self.possible_locations is None or len(self.possible_locations) == 0
                else self.possible_locations[0][0].merchant_id
            ),
            reconciled=False,
            date=self.date,
            statement_id=None,
            receipt_file_name=self.receipt_path.name,
            lat=self.lat,
            long=self.long,
            account_id=None,
            transfer_trans_id=None,
        )

    def move_photo(self) -> None:
        """
        Moves the receipt photo to the ExTract storage folder.
        """
        new_path: Path = app_settings.receipts_folder() / self.receipt_path.name
        self.receipt_path.rename(new_path)
        self.receipt_path = new_path

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
    def get_merchant_locations() -> list[Location]:
        """
        Gets all merchant locations that are not online from the database.

        :return: List of merchant locations
        """
        if ReceiptImporter.merchant_locations is not None:
            return ReceiptImporter.merchant_locations

        ReceiptImporter.merchant_locations = Location.get_all()
        return ReceiptImporter.merchant_locations

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
        for location in ReceiptImporter.get_merchant_locations():
            if location.lat is None or location.long is None:
                raise RuntimeError(
                    f"Location id = {location.sqlid} is missing coordinates."
                )
            distance_to_location: float = ReceiptImporter.calculate_distance(
                location.lat, location.long, lat, long
            )
            if distance_to_location <= app_settings.location_scan_radius():
                possible_locations.append((location, distance_to_location))

        possible_locations.sort(key=lambda x: x[1])
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
