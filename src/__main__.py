from src.model import database, user_settings, settings_file_path
from src.view.MainWindow import MainWindow

user_settings.load_settings(settings_file_path)
database.connect(user_settings.database_path())

MainWindow().event_loop()
