from src.model.SqlObject import SqlObject


class Amount(SqlObject):
    """
    Represents a amount in the SQL database.
    """

    def sync(self) -> None:
        """
        Syncs this amount to the database by updating the database. If the amount is not in the database it is
        added.
        """
