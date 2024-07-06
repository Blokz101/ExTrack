from queue import Queue

full_date_format: str = "%m/%d/%Y %H:%M:%S"
"""Full date format for validation and display."""
short_date_format: str = "%m/%d/%Y"
"""Short date format for validation and display."""
gui_theme: str = "DarkGrey13"
"""Theme all windows in the GUI will use."""
testing_mode: bool = False
"""True if the application is running in testing mode, false otherwise."""
notification_message_queue: Queue = Queue()
"""Queue that will hold notification messages when testing mode is enabled."""
