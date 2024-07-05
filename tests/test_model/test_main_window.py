"""
Tests the MainWindow class.
"""

from unittest import skip

from src.view.main_window import MainWindow
from tests.test_model.sample_1_test_case import Sample1TestCase


class TestMainWindow(Sample1TestCase):
    """Tests the MainWindow class."""

    @skip("Manual test")
    def test_manual(self):
        """
        Manual test for MainWindow.event_loop() for debugging purposes.
        """
        MainWindow().event_loop()
