import json

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRegExp, Qt
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QSizePolicy, QTextEdit
from commons.common import Common
from commons.db_connection import DBConnection
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
        self.etextJsonResult = self.findChild(QTextEdit, "teditJsonResult")
        self.vlyReportResultLayout = self.findChild(QVBoxLayout, "vlyTargetResults")
        self.glyReportBuff = QGridLayout()
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
        remaining_number = int(self.leditRemainingPhotoNumber.text())
        if remaining_number > 0:
            # remove some items from json results except remaining number
            self.probe_result.json_result['results'] = \
                Common.remove_elements_from_list_tail(self.probe_result.json_result['results'], remaining_number)
            # repaint target images view
            self.init_target_images_view()

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
        probe_id = Common.generate_probe_id()
        # check whether probe id exist on database
        db = DBConnection()
        while db.is_exist_value("cases", "probe_id", probe_id):
            probe_id = Common.generate_probe_id()
        self.probe_result.probe_id = probe_id
        self.lblProbeId.setText(probe_id)
        self.lblProbeResult.setText(self.probe_result.is_matched())
        self.lblCaseNumber.setText(self.probe_result.case_info.case_number)
        self.lblExaminerNo.setText(self.probe_result.case_info.examiner_no)
        self.lblExaminerName.setText(self.probe_result.case_info.examiner_name)
        self.lblRemarks.setText(self.probe_result.case_info.remarks)
        self.lblTimeOfReportGeneration.setText(str(self.probe_result.json_result['time_used']))
        subject_pixmap = QPixmap(self.probe_result.case_info.subject_image_url)
        self.lblSubjectImage.setPixmap(subject_pixmap)
        self.lblSubjectImage.setScaledContents(True)
        self.lblSubjectImage.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        subject_pixmap.scaled(self.lblSubjectImage.rect().x(), self.lblSubjectImage.rect().y(), Qt.KeepAspectRatio,
                              Qt.FastTransformation)

        js_result = json.dumps(self.probe_result.json_result, indent=4, sort_keys=True)
        self.etextJsonResult.setPlainText(js_result)

    def init_target_images_view(self):
        # clear all child on result container layout
        self.clear_result_list()
        print(str(self.vlyReportResultLayout.count()))
        # add items to result container layout
        self.glyReportBuff = QGridLayout(self)
        # if there is one matched image
        results = self.probe_result.json_result['results']
        # hly_result = QHBoxLayout()
        index = 0
        for result in results:
            # show the cross button on image
            result_view_item = ProbeResultItemWidget(result, True)
            # connect delete signal from delete button on target image.
            result_view_item.delete_item_signal.connect(self.delete_result_item)
            self.glyReportBuff.addWidget(result_view_item, index // 3, index % 3)
            index += 1
        self.vlyReportResultLayout.addLayout(self.glyReportBuff)

    @pyqtSlot(object)
    def delete_result_item(self, item):
        self.probe_result.remove_json_item(item)
        self.init_target_images_view()

    def clear_result_list(self):
        Common.clear_layout(self.vlyReportResultLayout)
        self.repaint()
        self.showMaximized()
