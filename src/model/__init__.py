from pathlib import Path

from model.Database import Database

date_format: str = "%Y-%m-%d %H:%M:%S"
"""SQL Database format for dates."""

root_dir: Path = Path(__file__).parent.parent.parent
"""Path to the root directory of the project."""

database: Database = Database()
