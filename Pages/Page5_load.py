from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRegExp
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout

from commons.common import Common
from commons.probe_result_item_widget import ProbeResultItemWidget
from commons.probing_result import ProbingResult


class LoaderProbeReportPreviewPage(QMainWindow):
    return_home_signal = pyqtSignal()
    go_back_signal = pyqtSignal(object)
    generate_report_signal = pyqtSignal(object)
    go_remaining_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.probe_result = ProbingResult()
        self.window = uic.loadUi("./forms/Page_5.ui", self)
        self.btnGoBack = self.findChild(QPushButton, "btnGoBack")
        self.btnGoRemaining = self.findChild(QPushButton, "btnGoRemaining")
        self.btnGenerateReport = self.findChild(QPushButton, "btnGenerateReport")
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.lblCaseNumber = self.findChild(QLabel, "lblCaseNumber")
        self.lblExaminerNo = self.findChild(QLabel, "lblExaminerNo")
        self.lblExaminerName = self.findChild(QLabel, "lblExaminerName")
        self.lblProbeId = self.findChild(QLabel, "lblProbeId")
        self.lblProbeResult = self.findChild(QLabel, "lblProbeResult")
        self.lblRemarks = self.findChild(QLabel, "lblRemarks")
        self.lblTimeOfReportGeneration = self.findChild(QLabel, "lblTimeOfReportGeneration")
        self.lbeSubjectImage = self.findChild(QLabel, "lblSubjectImage")
        self.leditRemainingPhotoNumber = self.findChild(QLineEdit, "leditRemainingPhotoNumber")
        self.lblSubjectImage = self.findChild(QLabel, "lblSubjectImage")
        self.vlyReportResultLayout = self.findChild(QVBoxLayout, "report_result_layout")
        self.vlyReportResultLayout_buff = QVBoxLayout(self)
        self.init_actions()
        # self.init_input_values()
        # self.init_result_views()
        self.set_validate_input_data()

    @pyqtSlot()
    def on_clicked_generate_report(self):
        self.generate_report_signal.emit(self.probe_result)

    @pyqtSlot()
    def on_clicked_return_home(self):
        self.return_home_signal.emit()

    @pyqtSlot()
    def on_clicked_go_back(self):
        self.go_back_signal.emit(self.probe_result.case_info)

    @pyqtSlot()
    def on_clicked_go_remaining(self):
        remaining_number = self.leditRemainingPhotoNumber.text()

    # set validator to input box
    def set_validate_input_data(self):
        remaining_number_validator = QIntValidator(self.leditRemainingPhotoNumber)
        self.leditRemainingPhotoNumber.setValidator(remaining_number_validator)

    def init_actions(self):
        self.btnGenerateReport.clicked.connect(self.on_clicked_generate_report)
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)
        self.btnGoRemaining.clicked.connect(self.on_clicked_go_remaining)

    def init_input_values(self):
        self.lblProbeId.setText("123456789")
        self.lblProbeResult.setText(self.probe_result.is_matched())
        self.lblCaseNumber.setText(self.probe_result.case_info.case_number)
        self.lblExaminerNo.setText(self.probe_result.case_info.examiner_no)
        self.lblExaminerName.setText(self.probe_result.case_info.examiner_name)
        self.lblRemarks.setText(self.probe_result.case_info.remarks)
        self.lblTimeOfReportGeneration.setText(str(self.probe_result.json_result['time_used']))
        subject_pixmap = QPixmap(self.probe_result.case_info.subject_image_url)
        self.lblSubjectImage.setPixmap(subject_pixmap)

    def init_result_views(self):
        # Common.clear_layout(self.vlyReportResultLayout)
        # Common.box_delete(self.vlyReportResultLayout)
        self.vlyReportResultLayout_buff.setParent(None)
        self.vlyReportResultLayout_buff = QVBoxLayout(self)
        self.vlyReportResultLayout.addLayout(self.vlyReportResultLayout_buff)
        results = self.probe_result.json_result['results']
        hly_result = QHBoxLayout()
        index = 1
        for result in results:
            result_view_item = ProbeResultItemWidget(result)
            # connect delete signal from delete button on target image.
            result_view_item.delete_item_signal.connect(self.delete_result_item)
            if index % 4:
                hly_result.addWidget(result_view_item)
            else:
                hly_result_buff = hly_result
                hly_result = QHBoxLayout()
                # add QHLayoutBox row to result show part
                self.vlyReportResultLayout_buff.addLayout(hly_result_buff)
                hly_result.addWidget(result_view_item)
            index += 1
        # if the number of remaining items is less than 3
        self.vlyReportResultLayout_buff.addLayout(hly_result)

    @pyqtSlot(object)
    def delete_result_item(self, item):
        self.probe_result.remove_json_item(item)
        self.init_result_views()
