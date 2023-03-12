import string, os, time

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QSize
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QTableWidget, QHBoxLayout, QLineEdit, QComboBox, QTableWidgetItem, \
    QFileDialog, QMessageBox, QWidget

from commons.common import Common
from commons.db_connection import DBConnection
from commons.export_pdf_button import ExportPdfButton
from commons.gen_report import export_report_pdf, gen_pdf_filename
from commons.get_reports_thread import GetReportsThread
from commons.pagination_layout import PaginationLayout
from commons.probing_result import ProbingResult
from commons.zip_thread import ZipThread, ThreadResult
from datetime import datetime


class LoaderProbeReportListPage(QWidget):
    return_home_signal = pyqtSignal(str)
    go_back_signal = pyqtSignal(object)
    go_back_empty_signal = pyqtSignal()
    start_splash_signal = pyqtSignal(str)
    stop_splash_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.zip_thread = None
        self.probe_result = ProbingResult()
        self.current_page = 0
        self.number_per_page = 5
        self.search_string = '%'
        self.is_searching_result = False
        self.reports = []
        self.shown_reports = []  # current shown reports on table
        self.get_reports_thread = GetReportsThread()

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
        self.zip_time = time.time()
        self.init_actions()

    @pyqtSlot()
    def on_clicked_go_back(self):
        if self.probe_result.probe_id == '':
            self.go_back_empty_signal.emit()
        else:
            self.go_back_signal.emit(self.probe_result)

    @pyqtSlot()
    def on_clicked_return_home(self):
        self.return_home_signal.emit("")

    @pyqtSlot(int)
    def changed_entries_number(self, current_index):
        self.number_per_page = int(self.combEntriesNumber.currentText())
        self.current_page = 0
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
        self.get_reports_thread.finished_reports_signal.connect(
            lambda reports: self.finished_get_reports_slot(reports)
        )

    @pyqtSlot(list)
    def finished_get_reports_slot(self, reports):
        self.reports = reports
        self.init_views()
        self.setEnabled(True)
        self.stop_splash_signal.emit(None)

    def refresh_view(self):
        self.get_reports_thread.start()
        self.setEnabled(False)
        self.start_splash_signal.emit("data")

    def init_views(self):
        Common.clear_layout(self.hlyPaginationContainer)
        # if self.is_searching_result:
        #     report_len = db.count_search_results(self.search_string)
        #     reports = db.search_results(self.search_string, report_len, self.current_page, self.number_per_page)
        # else:
        #     report_len = db.count_row_number("cases")
        #     reports = db.get_pagination_results("cases", report_len, self.current_page, self.number_per_page)
        # if report_len:
        #     hly_pagination = PaginationLayout(report_len, self.number_per_page, self.current_page)
        #     # connect signals
        #     hly_pagination.changed_page_signal.connect(self.refresh_table)
        #     self.hlyPaginationContainer.addLayout(hly_pagination)
        report_len = len(self.reports)
        if self.is_searching_result:
            self.shown_reports = self.get_search_results(self.search_string, report_len, self.current_page, self.number_per_page)

        else:
            self.shown_reports = self.get_pagination_results(report_len, self.current_page, self.number_per_page)
        if report_len:
            hly_pagination = PaginationLayout(report_len, self.number_per_page, self.current_page)
            # connect signals
            hly_pagination.changed_page_signal.connect(self.refresh_table)
            self.hlyPaginationContainer.addLayout(hly_pagination)
        self.init_table(self.shown_reports)

    def get_search_results(self, search_string, report_len, current_page, number_per_page):
        searched = []
        paginated = []
        for item in self.reports:
            case_info = item.case_info
            probe_id = item.probe_id
            created_date = item.created_date
            if case_info.case_number.count(search_string) > 0 \
                    or case_info.case_PS.count(search_string) > 0 \
                    or case_info.examiner_no.count(search_string) > 0 \
                    or case_info.examiner_name.count(search_string) > 0 \
                    or case_info.remarks.count(search_string) > 0 \
                    or probe_id.count(search_string) > 0 \
                    or created_date.count(search_string) > 0:
                searched.append(item)
        start_index = current_page * number_per_page
        end_index = start_index + number_per_page
        if start_index > report_len:
            dif = start_index - report_len
            start_index -= dif
            end_index = report_len
        else:
            if end_index > report_len:
                end_index = report_len
        paginated = searched[start_index:end_index]
        return paginated

    def get_pagination_results(self, report_len, current_page, number_per_page):
        results = []
        start_index = current_page * number_per_page
        end_index = start_index + number_per_page
        if start_index > report_len:
            dif = start_index - report_len
            start_index -= dif
            end_index = report_len
        else:
            if end_index > report_len:
                end_index = report_len
        results = self.reports[start_index:end_index]
        return results

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
        filename = gen_pdf_filename(probe_result.probe_id, probe_result.case_info.case_number, probe_result.case_info.case_PS)
        file_location = QFileDialog.getSaveFileName(self, "Save report pdf file", os.path.join(Common.EXPORT_PATH, filename), ".pdf")
        if file_location[0] == "":
            return
        dirs = file_location[0].split("/")
        file_path = file_location[0].replace(dirs[len(dirs) - 1], "")
        exported = export_report_pdf(file_path, filename)
        if exported:
            Common.show_message(QMessageBox.Information, "Pdf report was exported.", "Report Generation", "Notice", "")
        else:
            Common.show_message(QMessageBox.Information, "Pdf report was not exported.", "Report Generation", "Notice", "")

    @pyqtSlot()
    def on_clicked_export_allzip(self):
        zip_call_interval = time.time() - self.zip_time
        if zip_call_interval < 3: return

        report_path = Common.get_reg(Common.REG_KEY)
        if report_path:
            report_path = report_path + "/" + Common.REPORTS_PATH
        else:
            report_path = Common.STORAGE_PATH + "/" + Common.REPORTS_PATH        
        Common.create_path(report_path)    

        datestr = datetime.strftime(datetime.now(), "%d_%m_%Y")
        zip_file = "%s/probe_reports_%s"%(Common.EXPORT_PATH, datestr)
        zip_location = QFileDialog.getSaveFileName(self, "Save report zip file", zip_file, ".zip")
        self.zip_time = time.time()

        if zip_location[0] == '':
            return
        #
        # db = DBConnection()
        # reports = db.get_values()
        self.zip_thread = ZipThread(self.shown_reports, zip_location[0] + zip_location[1])
        self.zip_thread.finished_zip_signal.connect(self.finished_zip_slot)
        self.zip_thread.start()
        self.setEnabled(False)  # set screen to be unable to operate

    @pyqtSlot(ThreadResult)
    def finished_zip_slot(self, res):
        self.zip_thread.quit()
        self.setEnabled(True)
        if res.status:
            Common.show_message(QMessageBox.Information, "Zip file included all pdfs was created.", "AllZip Generation", "Notice", "")
        else:
            Common.show_message(QMessageBox.Information, "Zip file included all pdfs was not created. Because %s"%res.message, "AllZip Generation", "Notice", "")
