"""
Script that reads the settings file and starts the application.
"""

from src.model import user_settings, settings_file_path
from src.view.main_window import MainWindow

user_settings.load_settings(settings_file_path)

MainWindow().event_loop()
