from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout

from commons.probing_result import ProbingResult


class LoaderProbeReportPage(QMainWindow):
    return_home_signal = pyqtSignal()
    go_back_signal = pyqtSignal(object)
    export_pdf_signal = pyqtSignal()
    go_remaining_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.window = uic.loadUi("./forms/Page_6.ui", self)
        self.probe_result = ProbingResult()
        self.btnGoBack = self.findChild(QPushButton, "btnGoBack")
        self.btnExportPdf = self.findChild(QPushButton, "btnExportPdf")
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.btnGoRemaining = self.findChild(QPushButton, "btnGoRemaining")
        self.lblCaseNumber = self.findChild(QLabel, "lblCaseNumber")
        self.lblExaminerNo = self.findChild(QLabel, "lblExaminerNo")
        self.lblExaminerName = self.findChild(QLabel, "lblExaminerName")
        self.lblProbeId = self.findChild(QLabel, "lblProbeId")
        self.lblProbeResult = self.findChild(QLabel, "lblProbeResult")
        self.lblRemarks = self.findChild(QLabel, "lblRemarks")
        self.lblTimeOfReportGeneration = self.findChild(QLabel, "lblTimeOfReportGeneration")
        self.lbeSubjectImage = self.findChild(QLabel, "lblSubjectImage")
        self.leditRemainingPhotoNumber = self.findChild(QLineEdit, "leditRemainingPhotoNumber")
        self.vlyReportResultLayout = self.findChild(QVBoxLayout, "report_result_layout")

        self.init_actions()
        self.set_validate_input_data()

    @pyqtSlot()
    def on_clicked_export_pdf(self):
        self.export_pdf_signal.emit()

    @pyqtSlot()
    def on_clicked_return_home(self):
        self.return_home_signal.emit()

    @pyqtSlot()
    def on_clicked_go_back(self):
        self.go_back_signal.emit(self.probe_result)

    @pyqtSlot()
    def on_clicked_go_remaining(self):
        remaining_number = self.leditRemainingPhotoNumber.text()

    # set validator to input box
    def set_validate_input_data(self):
        remaining_number_validator = QIntValidator(self.leditRemainingPhotoNumber)
        self.leditRemainingPhotoNumber.setValidator(remaining_number_validator)

    def init_actions(self):
        self.btnExportPdf.clicked.connect(self.on_clicked_export_pdf)
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)
        self.btnGoRemaining.clicked.connect(self.on_clicked_go_remaining)
