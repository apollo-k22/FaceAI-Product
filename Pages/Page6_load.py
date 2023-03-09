import json
import os

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QDateTime
from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QGridLayout, QTextEdit, \
    QSizePolicy, QFileDialog, QWidget, QMessageBox

from commons.common import Common
from commons.db_connection import DBConnection
from commons.gen_report import export_report_pdf, gen_pdf_filename
from commons.probe_result_item_widget import ProbeResultItemWidget
from commons.probing_result import ProbingResult
from commons.target_items_container_generator import TargetItemsContainerGenerator
from cryptophic.main import encrypt_file_to

class LoaderProbeReportPage(QWidget):
    return_home_signal = pyqtSignal(str)
    go_back_signal = pyqtSignal(object)
    export_pdf_signal = pyqtSignal(object)
    go_remaining_signal = pyqtSignal()
    start_splash_signal = pyqtSignal(str)
    stop_splash_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.target_items_generator_thread = TargetItemsContainerGenerator()
        self.window = uic.loadUi("./forms/Page_6.ui", self)
        self.probe_result = ProbingResult()
        self.case_data_for_results = []
        self.btnGoBack = self.findChild(QPushButton, "btnGoBack")
        self.btnExportPdf = self.findChild(QPushButton, "btnExportPdf")
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.lblCaseNumber = self.findChild(QLabel, "lblCaseNumber")
        self.lblExaminerNo = self.findChild(QLabel, "lblExaminerNo")
        self.lblExaminerName = self.findChild(QLabel, "lblExaminerName")
        self.lblProbeId = self.findChild(QLabel, "lblProbeId")
        self.lblProbeResult = self.findChild(QLabel, "lblProbeResult")
        self.teditRemarks = self.findChild(QTextEdit, "teditRemarks")
        self.lblTimeOfReportGeneration = self.findChild(QLabel, "lblTimeOfReportGeneration")
        self.lblSubjectImage = self.findChild(QLabel, "lblSubjectImage")
        self.lblMatchedDescription = self.findChild(QLabel, "lblMatchedDescription")
        self.teditJsonResult = self.findChild(QTextEdit, "teditJsonResult")
        self.vlyReportResult = self.findChild(QVBoxLayout, "vlyTargetResults")
        self.glyReportBuff = QGridLayout()

        self.init_actions()

    @pyqtSlot()
    def on_clicked_export_pdf(self):
        if self.probe_result.probe_id == '':
            Common.show_message(QMessageBox.Warning, "The data for generating report is empty. You will go home.",
                                "", "Empty Data", "")
            self.return_home_signal.emit("")
        else:
            filename = gen_pdf_filename(self.probe_result.probe_id, self.probe_result.case_info.case_number, self.probe_result.case_info.case_PS)
            file_location = QFileDialog.getSaveFileName(self, "Save report pdf file", os.path.join(Common.EXPORT_PATH, filename), ".pdf")
            if file_location[0] == "":
                return
            dirs = file_location[0].split("/")
            file_path = file_location[0].replace(dirs[len(dirs) - 1], "")
            exported = export_report_pdf(file_path, filename)
            if exported:
                Common.show_message(QMessageBox.Information, "Pdf report was exported.", "Report Generation", "Notice", "")
                self.probe_result = ProbingResult()
                self.refresh_views()
                self.init_input_values()
                # self.export_pdf_signal.emit(self.probe_result)
            else:
                Common.show_message(QMessageBox.Information, "Exporting was failed.", "Report Generation", "Notice",
                                    "")

    @pyqtSlot()
    def on_clicked_return_home(self):
        self.return_home_signal.emit("")

    @pyqtSlot()
    def on_clicked_go_back(self):
        self.probe_result = ProbingResult()
        self.go_back_signal.emit(self.probe_result)
 
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
        media_path = Common.get_reg(Common.REG_KEY)
        if media_path:
            media_path = media_path + "/" + Common.MEDIA_PATH
        else:
            media_path = Common.STORAGE_PATH + "/" + Common.MEDIA_PATH            
        Common.create_path(media_path)

        # copy subject and target images to media directory, after that, replace urls with urls in media folder
        self.probe_result.case_info.subject_image_url = Common.copy_file(self.probe_result.case_info.subject_image_url,
                                                                         media_path + "/subjects")
        target_images = []
        index = 0
        for target in self.probe_result.case_info.target_image_urls:
            modified_target = Common.copy_file(target, media_path + "/targets")
            target_images.append(modified_target)
            self.probe_result.json_result["results"][index]["image_path"] = modified_target
            self.probe_result.json_result["faces"][index]["image_path"] = modified_target
        self.probe_result.case_info.target_image_urls = target_images

    def init_actions(self):
        self.btnExportPdf.clicked.connect(self.on_clicked_export_pdf)
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        self.btnReturnHome.clicked.connect(self.on_clicked_return_home)
        self.target_items_generator_thread.finished_refreshing_target_items.connect(
            lambda case_data: self.finished_refresh_target_items_slot(case_data))

    @pyqtSlot(list)
    def finished_refresh_target_items_slot(self, case_data):
        results = self.probe_result.json_result['results']
        index = 0
        if len(results) > 0 and len(self.case_data_for_results):
            for result in results:
                case_info = self.case_data_for_results[index]
                # set unable the cross button on image
                result_view_item = ProbeResultItemWidget(result, False, self.probe_result.case_info.is_used_old_cases,
                                                         case_info)
                self.glyReportBuff.addWidget(result_view_item, index // 3, index % 3)
                index += 1
        self.vlyReportResult.addLayout(self.glyReportBuff)
        js_result = json.dumps(self.probe_result.json_result, indent=4, sort_keys=True)
        self.teditJsonResult.setPlainText(js_result)
        self.init_input_values()
        self.setEnabled(True)
        self.stop_splash_signal.emit(None)

    def refresh_views(self):
        # self.init_input_values()
        self.init_target_images_view()

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
            self.teditRemarks.setPlainText(self.probe_result.case_info.remarks)
            self.lblTimeOfReportGeneration.setText(str(self.probe_result.json_result['time_used']))
            image_style = "image:url(" + self.probe_result.case_info.subject_image_url + \
                          ");background:transparent;border: 1px solid rgb(53, 132, 228);"
            self.lblSubjectImage.setStyleSheet(image_style)
            self.lblSubjectImage.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            js_result = json.dumps(self.probe_result.json_result, indent=4, sort_keys=True)
            self.teditJsonResult.setPlainText(js_result)
        else:
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
            self.teditJsonResult.setPlainText("")

    def init_target_images_view(self):
        # clear all child on result container layout
        self.clear_result_list()
        # add items to result container layout
        self.glyReportBuff = QGridLayout(self)
        if not self.probe_result:
            return
        if not Common.is_empty(self.probe_result.case_info):
            self.setEnabled(False)
            self.start_splash_signal.emit("data")
            self.setEnabled(False)
            self.target_items_generator_thread.start()

    def clear_result_list(self):
        Common.clear_layout(self.vlyReportResult)

