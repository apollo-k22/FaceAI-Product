from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget


# start home page for probing
class StartHome(QWidget):
    finished_loading_signal = pyqtSignal()
    update_progress_signal = pyqtSignal(int)
    start_splash_signal = pyqtSignal(QWidget)

    def __init__(self):
        super().__init__()
        self.btnGo2ProbeReport = self.findChild(QPushButton, "btnGo2ProbeReport")
        self.btnCreateCase = self.findChild(QPushButton, "btnCreateCase")
        self.window = uic.loadUi("./forms/Page_1.ui", self)
