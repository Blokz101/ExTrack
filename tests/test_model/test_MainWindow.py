from src.view.MainWindow import MainWindow
from tests.test_model.Sample1TestCase import Sample1TestCase
from unittest import TestCase, skip


class TestMainWindow(Sample1TestCase):

    @skip
    def test_manual(self):
        MainWindow().event_loop()
