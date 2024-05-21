from src.model.SqlObject import SqlObject


class Merchant(SqlObject):
    """
    Represents a merchant in the SQL database.
    """

    def sync(self) -> None:
        """
        Syncs this merchant to the database by updating the database. If the merchant is not in the database it is
        added.
        """
