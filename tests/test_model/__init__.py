from pathlib import Path

from src.model import root_dir

test_database_path: Path = root_dir / "test_database.db"
"""Path to the active test database."""

test_receipt_folder_path: Path = root_dir / "test_receipt_folder"
"""Path to the active test receipt folder."""

test_data_dir_path: Path = root_dir / "tests" / "test_data"
"""Path to the sample testing databases."""

sample_database_1_path: Path = test_data_dir_path / "sample_database_1.db"
"""Path to sample database 1."""

sample_receipt_folder_1_path: Path = test_data_dir_path / "sample_receipts_1"
"""Path to sample receipt folder 1."""

test_settings_file_path: Path = root_dir / "test_settings.json"
"""Path to the test settings file."""
