from src.model.SqlObject import SqlObject


class Statement(SqlObject):
    """
    Represents a statement in the SQL database.
    """

    def sync(self) -> None:
        """
        Syncs this statement to the database by updating the database. If the statement is not in the database it is
        added.
        """
