import json
from datetime import date, datetime

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QDateTime
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QGridLayout, QTextEdit, \
    QSizePolicy
from sympy import false

from commons.common import Common
from commons.db_connection import DBConnection
from commons.probe_result_item_widget import ProbeResultItemWidget
from commons.probing_result import ProbingResult


class LoaderProbeReportPage(QMainWindow):
    return_home_signal = pyqtSignal()
    go_back_signal = pyqtSignal(object)
    export_pdf_signal = pyqtSignal(object)
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
        self.lblSubjectImage = self.findChild(QLabel, "lblSubjectImage")
        self.leditRemainingPhotoNumber = self.findChild(QLineEdit, "leditRemainingPhotoNumber")
        self.teditJsonResult = self.findChild(QTextEdit, "teditJsonResult")
        self.vlyReportResult = self.findChild(QVBoxLayout, "vlyTargetResults")
        self.glyReportBuff = QGridLayout()

        self.init_actions()
        self.set_validate_input_data()

    @pyqtSlot()
    def on_clicked_export_pdf(self):
        self.write_probe_results_to_database()
        self.export_pdf_signal.emit(self.probe_result)

    @pyqtSlot()
    def on_clicked_return_home(self):
        self.return_home_signal.emit()

    @pyqtSlot()
    def on_clicked_go_back(self):
        self.go_back_signal.emit(self.probe_result)

    @pyqtSlot()
    def on_clicked_go_remaining(self):
        remaining_number = int(self.leditRemainingPhotoNumber.text())
        if remaining_number > 0:
            # remove some items from json results except remaining number
            self.probe_result.json_result['results'] = \
                Common.remove_elements_from_list_tail(self.probe_result.json_result['results'], remaining_number)
            # repaint target images view
            self.init_target_images_view()

    def write_probe_results_to_database(self):
        cases_fields = ["probe_id", "matched", "report_generation_time", "case_no",
                        "PS", "examiner_no", "examiner_name", "remarks",
                        "subject_url", "json_result", "created_date"]
        # create path "FaceAI Media" if not exists
        # so that subject and target images will be saved to that directory
        Common.create_path(Common.MEDIA_PATH)

        # copy subject and target images to media directory, after that, replace urls with urls in media folder
        self.probe_result.case_info.subject_image_url = Common.copy_file(self.probe_result.case_info.subject_image_url,
                                                                         Common.MEDIA_PATH)
        target_images = []
        for target in self.probe_result.case_info.target_image_urls:
            target_images.append(Common.copy_file(target, Common.MEDIA_PATH))
        self.probe_result.case_info.target_image_urls = target_images

        # make data to be inserted to database and insert
        probe_result = self.probe_result
        case_info = self.probe_result.case_info
        cases_data = [(probe_result.probe_id, probe_result.matched, probe_result.json_result["time_used"],
                       case_info.case_number, case_info.case_PS, case_info.examiner_no, case_info.examiner_name,
                       case_info.remarks, case_info.subject_image_url, json.dumps(probe_result.json_result),
                       QDateTime().currentDateTime().toString("yyyy-MM-dd hh-mm-ss"))]
        db = DBConnection()
        db.insert_values("cases", cases_fields, cases_data)

    # set validator to input box
    def set_validate_input_data(self):
        remaining_number_validator = QIntValidator(self.leditRemainingPhotoNumber)
        self.leditRemainingPhotoNumber.setValidator(remaining_number_validator)

    def init_actions(self):
        self.btnExportPdf.clicked.connect(self.on_clicked_export_pdf)
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)
        self.btnGoRemaining.clicked.connect(self.on_clicked_go_remaining)

    def init_input_values(self):
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
        self.teditJsonResult.setPlainText(js_result)

    def init_target_images_view(self):
        # clear all child on result container layout
        self.clear_result_list()
        print(str(self.vlyReportResult.count()))
        # add items to result container layout
        self.glyReportBuff = QGridLayout(self)
        results = self.probe_result.json_result['results']
        index = 0
        for result in results:
            # set unable the cross button on image
            result_view_item = ProbeResultItemWidget(result, False)
            self.glyReportBuff.addWidget(result_view_item, index // 3, index % 3)
            index += 1
        self.vlyReportResult.addLayout(self.glyReportBuff)

    def clear_result_list(self):
        Common.clear_layout(self.vlyReportResult)
        self.repaint()
        self.showMaximized()
