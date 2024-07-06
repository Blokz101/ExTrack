"""
Script that reads the settings file and starts the application.
"""

from src.model import app_settings
from src.view.main_window import MainWindow

app_settings.load_settings()
MainWindow().event_loop()
