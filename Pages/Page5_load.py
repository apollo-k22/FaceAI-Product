import json
import os

from PyQt5 import uic, QtGui
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QDateTime
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QGridLayout, \
    QSizePolicy, QTextEdit, QWidget, QFileDialog, QMessageBox
from commons.common import Common
from commons.db_connection import DBConnection
from commons.gen_report import create_pdf, gen_pdf_filename
from commons.gen_report_thread import GenReportThread
from commons.probe_result_item_widget import ProbeResultItemWidget
from commons.probing_result import ProbingResult
from commons.target_items_container_generator import TargetItemsContainerGenerator
from cryptophic.main import encrypt_file_to


class LoaderProbeReportPreviewPage(QWidget):
    return_home_signal = pyqtSignal(str)
    go_back_signal = pyqtSignal(object)
    generate_report_signal = pyqtSignal(object, object)
    go_remaining_signal = pyqtSignal()
    start_splash_signal = pyqtSignal(str)
    stop_splash_signal = pyqtSignal(object)
    show_window_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.target_items_generator_thread = TargetItemsContainerGenerator()
        self.case_data_for_results = []
        self.probe_result = ProbingResult()
        self.generate_report_thread = GenReportThread()
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
        self.teditRemarks = self.findChild(QTextEdit, "teditRemarks")
        self.lblTimeOfReportGeneration = self.findChild(QLabel, "lblTimeOfReportGeneration")
        self.lbeSubjectImage = self.findChild(QLabel, "lblSubjectImage")
        self.leditRemainingPhotoNumber = self.findChild(QLineEdit, "leditRemainingPhotoNumber")
        self.lblSubjectImage = self.findChild(QLabel, "lblSubjectImage")
        self.lblMatchedDescription = self.findChild(QLabel, "lblMatchedDescription")
        self.etextJsonResult = self.findChild(QTextEdit, "teditJsonResult")
        self.vlyReportResultLayout = self.findChild(QVBoxLayout, "vlyTargetResults")
        self.glyReportBuff = QGridLayout()
        self.init_actions()
        # self.init_input_values()
        # self.init_result_views()
        self.set_validate_input_data()

    @pyqtSlot(ProbingResult)
    def finished_generate_report_slot(self, probe_result):
        self.probe_result = probe_result
        self.generate_report_signal.emit(self.probe_result, self.case_data_for_results)
        self.stop_splash_signal.emit(None)
        self.setEnabled(True)

    @pyqtSlot()
    def on_clicked_generate_report(self):
        if self.probe_result.probe_id == '':
            Common.show_message(QMessageBox.Warning, "The data for generating report is empty. You will go home.",
                                "", "Empty Data", "")
            self.return_home_signal.emit("")
        else:
            self.start_splash_signal.emit("data")
            self.generate_report_thread.probe_result = self.probe_result
            self.setEnabled(False)
            self.generate_report_thread.start()

    @pyqtSlot()
    def on_clicked_return_home(self):
        self.return_home_signal.emit("")

    @pyqtSlot()
    def on_clicked_go_back(self):
        case_info = self.probe_result.case_info
        # self.probe_result = ProbingResult()
        self.go_back_signal.emit(case_info)

    @pyqtSlot()
    def on_clicked_go_remaining(self):
        if self.leditRemainingPhotoNumber.text() == '':
            return
        remaining_number = int(self.leditRemainingPhotoNumber.text())
        if remaining_number > 0:
            # remove some items from json results except remaining number
            result_images = \
                Common.remove_elements_from_list_tail(self.probe_result.json_result['results'], remaining_number)
            self.probe_result.json_result['results'].clear()
            self.probe_result.json_result['results'] = result_images
            result_faces = \
                Common.remove_elements_from_list_tail(self.probe_result.json_result['faces'], remaining_number)
            self.probe_result.json_result['faces'].clear()
            self.probe_result.json_result['faces'] = result_faces
            self.leditRemainingPhotoNumber.setText("")
            # repaint view
            self.refresh_views()

    # set validator to input box
    def set_validate_input_data(self):
        remaining_number_validator = QIntValidator(self.leditRemainingPhotoNumber)
        self.leditRemainingPhotoNumber.setValidator(remaining_number_validator)

    def init_actions(self):
        self.btnGenerateReport.clicked.connect(self.on_clicked_generate_report)
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)
        self.btnGoRemaining.clicked.connect(self.on_clicked_go_remaining)
        self.target_items_generator_thread.finished_refreshing_target_items.connect(
            self.finished_refresh_target_widget_slot)
        self.generate_report_thread.finished_generate_report_signal.connect(self.finished_generate_report_slot)

    def refresh_views(self):
        # self.init_input_values()
        self.start_splash_signal.emit("data")
        self.setEnabled(False)
        self.init_target_images_view()
        # self.repaint()

    @pyqtSlot(list)
    def finished_refresh_target_widget_slot(self, case_data):
        self.glyReportBuff = QGridLayout(self)
        results = self.probe_result.json_result['results']
        faces = self.probe_result.json_result['faces']
        self.case_data_for_results = case_data
        index = 0
        if len(results) > 0 and len(case_data):
            for result in results:
                case_information = case_data[index]
                face = faces[index]
                # show the cross button on image
                result_view_item = ProbeResultItemWidget(result, face, True,
                                                         self.probe_result.case_info.is_used_old_cases,
                                                         case_information)
                # connect delete signal from delete button on target image.
                result_view_item.delete_item_signal.connect(self.delete_result_item)
                self.glyReportBuff.addWidget(result_view_item, index // 3, index % 3)
                index += 1
        self.vlyReportResultLayout.addLayout(self.glyReportBuff)
        js_result = json.dumps(self.probe_result.json_result, indent=4, sort_keys=True)
        self.etextJsonResult.setPlainText(js_result)
        self.init_input_values()
        self.setEnabled(True)
        self.stop_splash_signal.emit(None)

    def init_input_values(self):
        if not self.probe_result:
            return
        if not Common.is_empty(self.probe_result.case_info):
            if self.probe_result.probe_id == '':
                probe_id = Common.generate_probe_id()
                # check whether probe id exist on database
                db = DBConnection()
                while db.is_exist_value("cases", "probe_id", probe_id):
                    probe_id = Common.generate_probe_id()
                self.probe_result.probe_id = probe_id
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
            self.teditRemarks.setPlainText(self.probe_result.case_info.remarks)
            self.lblTimeOfReportGeneration.setText(str(self.probe_result.json_result['time_used']))
            # image_style = "background:transparent;border: 1px solid rgb(53, 132, 228);"
            image_style = "image:url(" + self.probe_result.case_info.subject_image_url + \
                          ");background:transparent;border: 1px solid rgb(53, 132, 228);"
            self.lblSubjectImage.setStyleSheet(image_style)
            self.lblSubjectImage.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            # lbl_x, lbl_y, pixmap = Common.make_pixmap_from_image(self.probe_result.case_info.subject_image_url, self.lblSubjectImage)
            # self.lblSubjectImage.setPixmap(pixmap)

            js_result = json.dumps(self.probe_result.json_result, indent=4, sort_keys=True)
            self.etextJsonResult.setPlainText(js_result)
        else:
            self.lblProbeId.setText("")
            self.lblMatchedDescription.setText("The subject photo hasn't matched to any target photo.")
            self.lblProbeResult.setText("")
            self.lblCaseNumber.setText("")
            self.lblExaminerNo.setText("")
            self.lblExaminerName.setText("")
            self.teditRemarks.setPlainText("")
            self.lblTimeOfReportGeneration.setText("")
            image_style = "background:transparent;border: 1px solid rgb(53, 132, 228);"
            self.lblSubjectImage.setStyleSheet(image_style)
            self.lblSubjectImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.etextJsonResult.setPlainText("")
            self.leditRemainingPhotoNumber.setText("")

    def init_target_images_view(self):
        # clear all child on result container layout
        self.clear_result_list()
        self.etextJsonResult.setPlainText("")
        if not self.probe_result:
            self.setEnabled(True)
            self.stop_splash_signal.emit(None)
            return
        if not Common.is_empty(self.probe_result.case_info):
            results = self.probe_result.json_result['results']

            self.target_items_generator_thread.set_data(self, results, True,
                                                        self.probe_result.case_info.is_used_old_cases)
            self.target_items_generator_thread.start()
        else:
            self.setEnabled(True)
            self.stop_splash_signal.emit(None)

    @pyqtSlot(object)
    def delete_result_item(self, item):
        self.probe_result.remove_json_item(item)
        self.init_target_images_view()

    def clear_result_list(self):
        Common.clear_layout(self.vlyReportResultLayout)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        super().showEvent(a0)
        print("shown")
        self.show_window_signal.emit()

    def init_views(self):
        self.lblProbeId.setText("")
        self.lblMatchedDescription.setText("The subject photo hasn't matched to any target photo.")
        self.lblProbeResult.setText("")
        self.lblCaseNumber.setText("")
        self.lblExaminerNo.setText("")
        self.lblExaminerName.setText("")
        self.teditRemarks.setPlainText("")
        self.lblTimeOfReportGeneration.setText("")
        image_style = "image:url(" + self.probe_result.case_info.subject_image_url + \
                      ");background:transparent;border: 1px solid rgb(53, 132, 228);"
        self.lblSubjectImage.setStyleSheet(image_style)
        self.lblSubjectImage.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.etextJsonResult.setPlainText("")
        self.leditRemainingPhotoNumber.setText("")
        self.clear_result_list()
        self.probe_result = ProbingResult()
