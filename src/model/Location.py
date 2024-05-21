from src.model.SqlObject import SqlObject


class Location(SqlObject):
    """
    Represents a location in the SQL database.
    """

    def sync(self) -> None:
        """
        Syncs this location to the database by updating the database. If the location is not in the database it is
        added.
        """
