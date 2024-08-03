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

    merchant_locations: Optional[list[Location]] = None

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
    def import_receipt(
        receipt_path: Path,
    ) -> Optional[tuple[Transaction, list[Optional[int]]]]:
        """
        Creates a transaction object from a photo of a receipt.

        :param receipt_path: Path to the receipt photo
        :return: Transaction representation of the receipt and a list of ids for possible location
        """
        if not app_settings.receipts_folder().exists():
            app_settings.receipts_folder().mkdir()

        if not receipt_path.exists():
            return None

        # Parse each receipt photo
        with Image.open(receipt_path) as img:
            exif_data: Image.Exif = img.getexif()

            # Get data ids
            gps_id: int = next(tag for tag, name in TAGS.items() if name == "GPSInfo")
            img_desc_id: int = next(
                tag for tag, name in TAGS.items() if name == "ImageDescription"
            )
            date_id: int = next(tag for tag, name in TAGS.items() if name == "DateTime")

            # Get list of possible locations and set merchant id
            merchant_id: Optional[int] = None
            locations: Optional[list[tuple[Location, float]]] = None
            try:
                gps_info: dict = exif_data.get_ifd(gps_id)
                lat: float = ReceiptImporter._decimal_coords(gps_info[2], gps_info[1])
                long: float = ReceiptImporter._decimal_coords(gps_info[4], gps_info[3])

                locations = ReceiptImporter.nearby_locations(lat, long)
                if len(locations) > 0:
                    merchant_id = locations[0][0].merchant_id
            except KeyError:
                pass

            # Get date
            date: Optional[datetime] = None
            try:
                date = datetime.strptime(exif_data[date_id], "%Y:%m:%d %H:%M:%S")
            except KeyError:
                pass

            # Get description
            desc: Optional[str] = None
            try:
                desc = (
                    exif_data[img_desc_id].strip()
                    if img_desc_id in exif_data.keys()
                    else None
                )
            except KeyError:
                pass

            # Create and return transaction
            return (
                Transaction(
                    None,
                    desc,
                    merchant_id,
                    False,
                    date,
                    None,
                    receipt_path.name,
                    lat,
                    long,
                    None,
                    None,
                ),
                (
                    []
                    if locations is None
                    else [loc_data[0].merchant_id for loc_data in locations]
                ),
            )

    @staticmethod
    def _decimal_coords(coords, ref):
        decimal_degrees = (
            float(coords[0]) + float(coords[1]) / 60 + float(coords[2]) / 3600
        )
        if ref in ["S", "W"]:
            decimal_degrees = -1 * decimal_degrees
        return decimal_degrees
