from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTableWidget


class LoaderProbeReportListPage(QMainWindow):
    return_home_signal = pyqtSignal()
    go_back_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.window = uic.loadUi("./forms/Page_7.ui", self)
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.btnGoBack = self.findChild(QPushButton, "btnGoBack")
        self.btnExportAllZip = self.findChild(QPushButton, "btnExportAllZip")
        self.btnGoRemainingPage = self.findChild(QPushButton, "btnGoRemainingPage")
        self.resultTable = self.findChild(QTableWidget, "twdtResultTable")
        style = "::section {""background-color: rgb(0, 90, 226);border: 1px solid rgb(53, 132, 228); }"
        self.resultTable.horizontalHeader().setStyleSheet(style)

        self.init_actions()

    @pyqtSlot()
    def on_clicked_go_back(self):
        self.go_back_signal.emit()

    @pyqtSlot()
    def on_clicked_return_home(self):
        self.return_home_signal.emit()

    def init_actions(self):
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)

