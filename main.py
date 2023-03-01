from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, pyqtSlot
from Pages.Page0_load import LicenseBoxPage
from Pages.Page2_load import LoaderCreateNewCasePage
from Pages.Page3_load import LoaderSelectTargetPhotoPage
from Pages.Page4_load import LoaderProbingPage
from Pages.Page5_load import LoaderProbeReportPreviewPage
from Pages.Page6_load import LoaderProbeReportPage
from Pages.Page7_load import LoaderProbeReportListPage
import sys
from PyQt5.QtWidgets import QApplication
import sqlite3
import ntplib
import time
from time import ctime
import datetime
from cryptophic.license import read_information_db, get_cpu_info

# start home page for probing
from commons.case_info import CaseInfo
from commons.probing_result import ProbingResult
from commons.qss import QSS
import images
from cryptophic.dec_thread import DecThread
from cryptophic.main import exit_process
from insightfaces.faceai_init_thread import FaceAIInitThread
from insightfaces.main import FaceAI


class StartHome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.faceai = FaceAI()
        #
        # self.dec_thread = DecThread()
        # self.dec_thread.finished_decrypting_signal.connect(self.finished_decrypting_slot)
        # self.dec_thread.start()
        #
        # self.faceai_init_thread = FaceAIInitThread(self.faceai)
        # self.faceai_init_thread.finished_initializing_signal.connect(self.finished_initializing_slot)

        self.window = uic.loadUi("./forms/Page_1.ui", self)
        self.ui_0_license = LicenseBoxPage()
        self.ui_2_create_new_case = LoaderCreateNewCasePage(self.faceai)
        self.ui_3_select_target_photo = LoaderSelectTargetPhotoPage()
        self.ui_4_probing = LoaderProbingPage(self.faceai)
        self.ui_5_probe_report_preview = LoaderProbeReportPreviewPage()
        self.ui_6_probe_report = LoaderProbeReportPage()
        self.ui_7_prove_report_list = LoaderProbeReportListPage()

        # Click to go page2 from page 1 button
        self.btnCreateCase.clicked.connect(self.show_p2_create_new_case)
        # Click to go to page 7 from page 1 button
        self.btnGo2ProbeReport.clicked.connect(self.show_p7_probe_report_list_without_param)
        # set the connection between signal and slot for page transitions
        self.set_page_transition()
        self.showMaximized()
    #     app_unlocked = False
    #     app_expire = 0
    #     app_expire_date = ""
    #     app_unlocked, app_expire_date, app_fpo_info, app_atpo_info = read_information_db()
    #     print(app_unlocked, app_expire_date)
    #
    #     if app_unlocked == False:
    #         self.show_p0_license()
    #     else:
    #         fpo_info, atpo_info = get_cpu_info()
    #         if (app_fpo_info != fpo_info) & (app_atpo_info != atpo_info):
    #             quit()
    #         # try:
    #         #     NIST = 'pool.ntp.org'
    #         #     ntp = ntplib.NTPClient()
    #         #     ntpResponse = time.time() #ntp.request(NIST)
    #         #     # print(ntpResponse.tx_time)
    #         # except:
    #         #     print("ntp error")
    #
    #         app_expire = datetime.datetime.strptime(app_expire_date, "%d/%m/%Y") - datetime.datetime.today()
    #         if app_expire.total_seconds() > 0:
    #             self.showMaximized()
    #         else:
    #             print("expire error")
    #             self.show_p0_license()
    #
    # @pyqtSlot()
    # def finished_decrypting_slot(self):
    #     self.dec_thread.quit()
    #     self.faceai_init_thread.start()
    #
    # @pyqtSlot()
    # def finished_initializing_slot(self):
    #     print("faceai init ok")
    #     self.faceai_init_thread.quit()

    # set the connection between signal and slot for page transitions
    def set_page_transition(self):
        self.ui_0_license.continue_app_signal.connect(self.show_p1_home)
        self.ui_2_create_new_case.return_home_signal.connect(self.show_p1_home)
        # transit the case information 'create case page' to 'select target page'
        self.ui_2_create_new_case.continue_probe_signal.connect(
            lambda case_info:
            self.show_p3_select_target_photos(case_info)
        )
        # transit the case information 'select target page' to 'probing' page
        self.ui_3_select_target_photo.start_probe_signal.connect(
            lambda case_info:
            self.show_p4_probing(case_info)
        )
        self.ui_3_select_target_photo.go_back_signal.connect(self.show_p2_create_new_case)
        self.ui_3_select_target_photo.return_home_signal.connect(self.show_p1_home)

        # after completed probing, go to report preview page with probing_result object
        self.ui_4_probing.completed_probing_signal.connect(self.show_p5_probe_report_preview)

        # once clicked "return home" button, return home page
        self.ui_5_probe_report_preview.return_home_signal.connect(self.show_p1_home)
        # once clicked "generate report" button on preview page, go to report page
        self.ui_5_probe_report_preview.generate_report_signal.connect(self.show_p6_probe_report)
        # when clicked "go back" button on preview page, go to "select target photo" page
        self.ui_5_probe_report_preview.go_back_signal.connect(self.show_p3_select_target_photos)

        # when clicked "return home" button , return home page
        self.ui_6_probe_report.return_home_signal.connect(self.show_p1_home)
        # when clicked "export pdf" button, export result to pdf and go to report list page
        self.ui_6_probe_report.export_pdf_signal.connect(self.show_p7_probe_report_list)
        # when clicked "go back" button on report page, go to "report preview page
        self.ui_6_probe_report.go_back_signal.connect(self.show_p5_probe_report_preview)

        # when clicked "return home" button, return home page
        self.ui_7_prove_report_list.return_home_signal.connect(self.show_p1_home)
        # when clicked "go back" button, go back to "Probe report" page
        self.ui_7_prove_report_list.go_back_signal.connect(self.show_p6_probe_report)
        self.ui_7_prove_report_list.go_back_empty_signal.connect(self.show_p6_probe_report_without_param)

    @pyqtSlot(CaseInfo)
    def show_p3_select_target_photos(self, case_info):
        # hide other window
        self.hide()
        self.ui_2_create_new_case.hide()
        self.ui_5_probe_report_preview.hide()
        # set case information to page
        self.ui_3_select_target_photo.case_info = case_info
        self.ui_3_select_target_photo.showMaximized()

    def show_p0_license(self):
        self.hide()
        self.ui_0_license.showMaximized()

    @pyqtSlot()
    def show_p1_home(self):
        self.ui_0_license.hide()
        self.ui_2_create_new_case.hide()
        self.ui_3_select_target_photo.hide()
        self.ui_6_probe_report.hide()
        self.ui_7_prove_report_list.hide()
        self.ui_5_probe_report_preview.hide()
        self.showMaximized()

    @pyqtSlot()
    def show_p2_create_new_case(self):
        self.hide()
        self.ui_3_select_target_photo.hide()
        self.ui_2_create_new_case.showMaximized()

    @pyqtSlot(CaseInfo)
    def show_p4_probing(self, case_info):
        self.ui_3_select_target_photo.hide()
        # start probing
        self.ui_4_probing.showMaximized()
        self.ui_4_probing.start_probing(case_info)

    @pyqtSlot(ProbingResult)
    def show_p5_probe_report_preview(self, probe_result):
        self.ui_4_probing.hide()
        self.ui_6_probe_report.hide()
        self.ui_5_probe_report_preview.probe_result = probe_result
        self.ui_5_probe_report_preview.init_input_values()
        self.ui_5_probe_report_preview.init_target_images_view()
        self.ui_5_probe_report_preview.showMaximized()

    @pyqtSlot(ProbingResult)
    def show_p6_probe_report(self, probe_result):
        self.ui_5_probe_report_preview.hide()
        self.ui_7_prove_report_list.hide()
        self.ui_6_probe_report.probe_result = probe_result
        self.ui_6_probe_report.init_input_values()
        self.ui_6_probe_report.init_target_images_view()
        self.ui_6_probe_report.showMaximized()

    @pyqtSlot()
    def show_p6_probe_report_without_param(self):
        self.ui_7_prove_report_list.hide()
        self.ui_6_probe_report.probe_result = ProbingResult()
        self.ui_6_probe_report.init_input_values()
        self.ui_6_probe_report.init_target_images_view()
        self.ui_6_probe_report.showMaximized()

    @pyqtSlot(ProbingResult)
    def show_p7_probe_report_list(self, probe_result):
        self.hide()
        self.ui_6_probe_report.hide()
        self.ui_7_prove_report_list.probe_result = probe_result
        self.ui_7_prove_report_list.init_actions()
        self.ui_7_prove_report_list.init_views()
        self.ui_7_prove_report_list.showMaximized()

    @pyqtSlot()
    def show_p7_probe_report_list_without_param(self):
        self.hide()
        self.ui_4_probing.hide()
        self.ui_7_prove_report_list.init_views()
        self.ui_7_prove_report_list.showMaximized()


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(QSS)
        window = StartHome()
        app.exec_()
    finally:
        exit_process()
        print("exit")
