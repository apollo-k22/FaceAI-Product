import datetime
import sys

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QPushButton
from PyQt5.QtWidgets import QWidget

from Pages.Page0_load import LicenseBoxPage
from Pages.Page2_load import LoaderCreateNewCasePage
from Pages.Page3_load import LoaderSelectTargetPhotoPage
from Pages.Page4_load import LoaderProbingPage
from Pages.Page5_load import LoaderProbeReportPreviewPage
from Pages.Page6_load import LoaderProbeReportPage
from Pages.Page7_load import LoaderProbeReportListPage
# start home page for probing
from commons.case_info import CaseInfo
from commons.probing_result import ProbingResult
from commons.qss import QSS
from commons.splash_screen import SplashThread
from cryptophic.dec_thread import DecThread
from cryptophic.license import read_information_db, get_cpu_info
from cryptophic.main import exit_process
from insightfaces.faceai_init_thread import FaceAIInitThread
from insightfaces.main import FaceAI


class StartHome(QWidget):
    finished_loading_signal = pyqtSignal()
    update_progress_signal = pyqtSignal(int)
    start_splash_signal = pyqtSignal(QWidget)

    def __init__(self):
        super().__init__()
        self.btnGo2ProbeReport = self.findChild(QPushButton, "btnGo2ProbeReport")
        self.btnCreateCase = self.findChild(QPushButton, "btnCreateCase")
        self.window = uic.loadUi("./forms/Page_1.ui", self)
        QTimer.singleShot(0, self.doLater)

    def doLater(self):
        print("finished load home page")
