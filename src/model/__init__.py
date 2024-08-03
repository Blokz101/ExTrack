"""
Constants and global variables used in the model.
"""

from pathlib import Path

from src.model.database import Database
from src.model.user_settings import UserSettings

date_format: str = "%Y-%m-%d %H:%M:%S"
"""SQL Database format for dates."""

root_dir: Path = Path(__file__).parent.parent.parent
"""Path to the root directory of the project."""

database: Database = Database()
"""Database connection that the entire application will use."""

settings_file_path: Path = root_dir / "settings.json"
"""Path to the settings file."""

app_settings: UserSettings = UserSettings(settings_file_path)
"""User settings for the application."""
app_settings.load_settings()
