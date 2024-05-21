from src.model.SqlObject import SqlObject


class Tag(SqlObject):
    """
    Represents a tag in the SQL database.
    """

    def sync(self) -> None:
        """
        Syncs this tag to the database by updating the database. If the tag is not in the database it is
        added.
        """
