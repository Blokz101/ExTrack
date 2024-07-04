from pathlib import Path
from src.model import root_dir

test_database = root_dir / "test_database.db"
"""Path to the active test database."""

test_data_dir: Path = root_dir / "tests" / "test_data"
"""Path to the sample testing databases."""

sample_database_1 = test_data_dir / "sample_database_1.db"
"""Path to sample database 1."""

test_settings_file_path = root_dir / "test_settings.json"
"""Path to the test settings file."""
