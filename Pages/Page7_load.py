from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTableWidget, QTableWidgetItem

from commons.db_connection import DBConnection
from commons.export_pdf_button import ExportPdfButton
from commons.probing_result import ProbingResult


class LoaderProbeReportListPage(QMainWindow):
    return_home_signal = pyqtSignal()
    go_back_signal = pyqtSignal(object)
    go_back_empty_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.probe_result = ProbingResult()

        self.window = uic.loadUi("./forms/Page_7.ui", self)
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.btnGoBack = self.findChild(QPushButton, "btnGoBack")
        self.btnExportAllZip = self.findChild(QPushButton, "btnExportAllZip")
        self.btnGoRemainingPage = self.findChild(QPushButton, "btnGoRemainingPage")
        self.resultTable = self.findChild(QTableWidget, "twdtResultTable")
        style = "::section {""background-color: rgb(0, 90, 226);border: 1px solid rgb(53, 132, 228); }"
        self.resultTable.horizontalHeader().setStyleSheet(style)

    @pyqtSlot()
    def on_clicked_go_back(self):
        if self.probe_result.probe_id == '':
            self.go_back_empty_signal.emit()
        else:
            self.go_back_signal.emit(ProbingResult)

    @pyqtSlot()
    def on_clicked_return_home(self):
        self.return_home_signal.emit()

    def init_actions(self):
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)

    def init_views(self):
        self.init_table()

    def init_table(self):
        db = DBConnection()
        reports = db.get_values()
        row_index = 0
        for report in reports:
            case_info = report.case_info
            datetime_item = QTableWidgetItem(report.created_date)
            case_no = QTableWidgetItem(case_info.case_number)
            ps = QTableWidgetItem(case_info.case_PS)
            probe_id = QTableWidgetItem(report.probe_id)
            exam_no = QTableWidgetItem(case_info.examiner_no)
            exam_name = QTableWidgetItem(case_info.examiner_name)
            export_btn = ExportPdfButton(report)
            export_btn.clicked.connect(self.export_pdf)
            self.resultTable.setItem(row_index, 0, datetime_item)
            self.resultTable.setItem(row_index, 1, case_no)
            self.resultTable.setItem(row_index, 2, ps)
            self.resultTable.setItem(row_index, 3, probe_id)
            self.resultTable.setItem(row_index, 4, exam_name)
            self.resultTable.setItem(row_index, 5, exam_no)
            self.resultTable.setCellWidget(row_index, 6, export_btn)
            row_index += 1

        # QTableWidgetItem * newItem = new
        # QTableWidgetItem(tr("%1").arg(
        #     (row + 1) * (column + 1)));
        # tableWidget->setItem(row, column, newItem);
    @pyqtSlot()
    def export_pdf(self):
        pass
