import json
from datetime import date, datetime

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, QDateTime
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QGridLayout, QTextEdit, \
    QSizePolicy, QFileDialog
from sympy import false

from commons.common import Common
from commons.db_connection import DBConnection
from commons.gen_report import create_pdf
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
        self.lblMatchedDescription = self.findChild(QLabel, "lblMatchedDescription")
        self.leditRemainingPhotoNumber = self.findChild(QLineEdit, "leditRemainingPhotoNumber")
        self.teditJsonResult = self.findChild(QTextEdit, "teditJsonResult")
        self.vlyReportResult = self.findChild(QVBoxLayout, "vlyTargetResults")
        self.glyReportBuff = QGridLayout()

        self.init_actions()
        self.set_validate_input_data()

    @pyqtSlot()
    def on_clicked_export_pdf(self):
        if not (self.probe_result.case_info.subject_image_url == '') and \
                not (len(self.probe_result.case_info.target_image_urls) == 0):
            self.write_probe_results_to_database()
        export_path = QFileDialog.getExistingDirectory(self, "The path to be saved pdf")
        if not export_path == "":
            create_pdf(self.probe_result.probe_id, self.probe_result, export_path)
            self.export_pdf_signal.emit(self.probe_result)
        else:
            return

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
            self.probe_result.json_result['faces'] = \
                Common.remove_elements_from_list_tail(self.probe_result.json_result["faces"], remaining_number)
            # repaint target images view
            self.init_target_images_view()
            self.init_input_values()

    def write_probe_results_to_database(self):
        self.update_json_data()
        # make data to be inserted to database and insert
        probe_result = self.probe_result
        case_info = self.probe_result.case_info
        cases_fields = ["probe_id", "matched", "report_generation_time", "case_no",
                        "PS", "examiner_no", "examiner_name", "remarks",
                        "subject_url", "json_result", "created_date"]
        cases_data = [(probe_result.probe_id, probe_result.matched, probe_result.json_result["time_used"],
                       case_info.case_number, case_info.case_PS, case_info.examiner_no, case_info.examiner_name,
                       case_info.remarks, case_info.subject_image_url, json.dumps(probe_result.json_result),
                       QDateTime().currentDateTime().toString("yyyy-MM-dd hh-mm-ss"))]
        target_fields = ["target_url", "case_id"]
        target_data = []
        db = DBConnection()
        case_id = db.insert_values("cases", cases_fields, cases_data)
        for target in case_info.target_image_urls:
            target_tuple = (target, case_id)
            target_data.append(target_tuple)

        db.insert_values("targets", target_fields, target_data)

    # update probe result with copied image urls
    def update_json_data(self):
        # create path "FaceAI Media" if not exists
        # so that subject and target images will be saved to that directory
        Common.create_path(Common.MEDIA_PATH)

        # copy subject and target images to media directory, after that, replace urls with urls in media folder
        self.probe_result.case_info.subject_image_url = Common.copy_file(self.probe_result.case_info.subject_image_url,
                                                                         Common.MEDIA_PATH + "/subjects")
        target_images = []
        index = 0
        for target in self.probe_result.case_info.target_image_urls:
            modified_target = Common.copy_file(target, Common.MEDIA_PATH + "/targets")
            target_images.append(modified_target)
            self.probe_result.json_result["results"][index]["image_path"] = modified_target
            self.probe_result.json_result["faces"][index]["image_path"] = modified_target
        self.probe_result.case_info.target_image_urls = target_images

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
        if not self.probe_result:
            return
        if not Common.is_empty(self.probe_result.case_info):
            self.lblProbeId.setText(self.probe_result.probe_id)
            matched = self.probe_result.is_matched()
            if matched == 'Matched':
                self.lblMatchedDescription.setText("The subject photo has matched to the following target photos."
                                                   " Respective facial recognition similarity scores are attached herewith.")
            else:
                self.lblMatchedDescription.setText("The subject photo hasn't matched to any target photo.")
            self.lblProbeResult.setText(matched)
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
        if not self.probe_result:
            return
        if not Common.is_empty(self.probe_result.case_info):
            # clear all child on result container layout
            self.clear_result_list()
            print(str(self.vlyReportResult.count()))
            # add items to result container layout
            self.glyReportBuff = QGridLayout(self)
            results = self.probe_result.json_result['results']
            index = 0
            for result in results:
                # set unable the cross button on image
                result_view_item = ProbeResultItemWidget(result, False, self.probe_result.case_info.is_used_old_cases)
                self.glyReportBuff.addWidget(result_view_item, index // 3, index % 3)
                index += 1
            self.vlyReportResult.addLayout(self.glyReportBuff)

    def clear_result_list(self):
        Common.clear_layout(self.vlyReportResult)
        self.repaint()
        self.showMaximized()
