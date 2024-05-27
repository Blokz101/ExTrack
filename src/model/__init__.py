from pathlib import Path

from model.Database import Database

root_dir: Path = Path(__file__).parent.parent.parent
"""Path to the root directory of the project."""

database: Database = Database()
