import string, os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractScrollArea, \
    QVBoxLayout, QHBoxLayout, QFileDialog, QComboBox, QLineEdit, QMessageBox

from commons.common import Common
from commons.db_connection import DBConnection
from commons.export_pdf_button import ExportPdfButton
from commons.gen_report import create_pdf, gen_pdf_filename
from commons.pagination_layout import PaginationLayout
from commons.probing_result import ProbingResult
from commons.zip_thread import ZipThread, ThreadResult
from datetime import datetime


class LoaderProbeReportListPage(QMainWindow):
    return_home_signal = pyqtSignal()
    go_back_signal = pyqtSignal(object)
    go_back_empty_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.probe_result = ProbingResult()
        self.current_page = 0
        self.number_per_page = 5
        self.search_string = '%'
        self.is_searching_result = False

        self.window = uic.loadUi("./forms/Page_7.ui", self)
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.btnGoBack = self.findChild(QPushButton, "btnGoBack")
        self.btnExportAllZip = self.findChild(QPushButton, "btnExportAllZip")
        self.btnGoRemainingPage = self.findChild(QPushButton, "btnGoRemainingPage")
        self.vlyTableContainer = self.findChild(QVBoxLayout, "vlyTableContainer")
        self.resultTable = self.findChild(QTableWidget, "resultTable")
        style = "::section {background-color: rgb(0, 90, 226);border: 1px solid rgb(53, 132, 228); }"
        self.setStyleSheet(style)
        self.resultTable.setMinimumHeight(0)
        self.hlyPaginationContainer = self.findChild(QHBoxLayout, "hlyPaginationContainer")
        self.combEntriesNumber = self.findChild(QComboBox, "combEntriesNumber")
        self.combEntriesNumber.setCurrentIndex(0)

        self.leditSearchString = self.findChild(QLineEdit, "leditSearchString")
        self.init_actions()

    @pyqtSlot()
    def on_clicked_go_back(self):
        if self.probe_result.probe_id == '':
            self.go_back_empty_signal.emit()
        else:
            self.go_back_signal.emit(self.probe_result)

    @pyqtSlot()
    def on_clicked_return_home(self):
        self.return_home_signal.emit()

    @pyqtSlot(int)
    def changed_entries_number(self, current_index):
        self.number_per_page = int(self.combEntriesNumber.currentText())
        self.init_views()

    @pyqtSlot(str)
    def changed_search_string(self, search_string):
        if not search_string == '':
            self.search_string = search_string
            self.is_searching_result = True
        else:
            self.is_searching_result = False
        self.init_views()

    def init_actions(self):
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)
        self.combEntriesNumber.currentIndexChanged.connect(self.changed_entries_number)
        self.leditSearchString.textChanged.connect(self.changed_search_string)
        self.btnExportAllZip.clicked.connect(self.on_clicked_export_allzip)

    def init_views(self):
        Common.clear_layout(self.hlyPaginationContainer)
        db = DBConnection()
        reports = []
        report_len = 0
        if self.is_searching_result:
            report_len = db.count_search_results(self.search_string)
            reports = db.search_results(self.search_string, report_len, self.current_page, self.number_per_page)
        else:
            report_len = db.count_row_number("cases")
            reports = db.get_pagination_results("cases", report_len, self.current_page, self.number_per_page)
        if report_len:
            hly_pagination = PaginationLayout(report_len, self.number_per_page, self.current_page)
            # connect signals
            hly_pagination.changed_page_signal.connect(self.refresh_table)
            self.hlyPaginationContainer.addLayout(hly_pagination)
        self.init_table(reports)

    def init_table(self, reports):
            row_index = 0
            # set table row and column num
            self.resultTable.setRowCount(len(reports))
            for report in reports:
                case_info = report.case_info
                datetime_item = QTableWidgetItem(report.created_date)
                datetime_item.setSizeHint(QSize(50, 50))
                case_no = QTableWidgetItem(case_info.case_number)
                ps = QTableWidgetItem(case_info.case_PS)
                probe_id = QTableWidgetItem(report.probe_id)
                exam_no = QTableWidgetItem(case_info.examiner_no)
                exam_name = QTableWidgetItem(case_info.examiner_name)
                export_btn = ExportPdfButton(report)
                export_btn.export_pdf_signal.connect(self.export_pdf)
                self.resultTable.setItem(row_index, 0, datetime_item)
                self.resultTable.setItem(row_index, 1, case_no)
                self.resultTable.setItem(row_index, 2, ps)
                self.resultTable.setItem(row_index, 3, probe_id)
                self.resultTable.setItem(row_index, 4, exam_name)
                self.resultTable.setItem(row_index, 5, exam_no)
                self.resultTable.setCellWidget(row_index, 6, export_btn)
                row_index += 1

    @pyqtSlot(int)
    def refresh_table(self, page):
        self.current_page = page
        self.init_views()

    @pyqtSlot(ProbingResult)
    def export_pdf(self, probe_result):
        report_path = Common.get_reg(Common.REG_KEY)
        if report_path:
            report_path = report_path + Common.REPORTS_PATH
        else:
            report_path = Common.STORAGE_PATH + "/" + Common.REPORTS_PATH        
        Common.create_path(report_path)                
        print(probe_result.json_result["faces"])
        filename = gen_pdf_filename(probe_result.probe_id, probe_result.case_info.case_number, probe_result.case_info.case_PS)
        file_location = QFileDialog.getSaveFileName(self, "Save report pdf file", os.path.join(report_path, filename), ".pdf")
        if file_location[0] == "":
            return
        printed = create_pdf(probe_result.probe_id, probe_result, file_location[0] + file_location[1])
        if printed:
            Common.show_message(QMessageBox.Information, "Pdf report was created.", "Report Generation", "Notice", "")
        else:
            Common.show_message(QMessageBox.Information, "Pdf report was not created.", "Report Generation", "Notice", "")

    @pyqtSlot()
    def on_clicked_export_allzip(self):
        report_path = Common.get_reg(Common.REG_KEY)
        if report_path:
            report_path = report_path + Common.REPORTS_PATH
        else:
            report_path = Common.STORAGE_PATH + "/" + Common.REPORTS_PATH        
        Common.create_path(report_path)    

        datestr = datetime.strftime(datetime.now(), "%d_%m_%Y")
        zip_file = "%s/probe_reports_%s"%(report_path, datestr)
        zip_location = QFileDialog.getSaveFileName(self, "Save report zip file", zip_file, ".zip")
        print("end")

        if zip_location[0] == '':
            return

        db = DBConnection()
        reports = db.get_values()
        
        self.zip_thread = ZipThread(reports, zip_location[0] + zip_location[1])
        self.zip_thread.finished_zip_signal.connect(self.finished_zip_slot)
        self.zip_thread.start()

    @pyqtSlot(ThreadResult)
    def finished_zip_slot(self, res):
        self.zip_thread.quit()
        if res.status:
            Common.show_message(QMessageBox.Information, "Zip file included all pdfs was created.", "AllZip Generation", "Notice", "")
        else:
            Common.show_message(QMessageBox.Information, "Zip file included all pdfs was not created. Because %s"%res.message, "AllZip Generation", "Notice", "")
