from random import random

from PyQt5 import uic
from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel

from commons.case_info import CaseInfo
from commons.probing_result import ProbingResult
from commons.probing_thread import ProbingThread
from insightfaces.main import recognition


class LoaderProbingPage(QMainWindow):
    completed_probing_signal = pyqtSignal(ProbingResult)

    def __init__(self):
        super().__init__()

        self.probing_result = ProbingResult()
        self.probing_thread = ProbingThread(CaseInfo)
        self.gif = QMovie(":/newPrefix/AIFace.gif")  # ('ui/animated_gif_logo_UI_.gif') !!!
        self.window = uic.loadUi("./forms/Page_4.ui", self)
        self.lblFaceGif = self.findChild(QLabel, "lblFaceGif")
        self.lblFaceGif.setMovie(self.gif)

    def start_gif(self):
        self.gif.start()

    def stop_gif(self):
        self.gif.stop()

    def start_probing(self, case_info):
        self.probing_result.case_info = case_info
        # self.make_mock()
        self.start_gif()
        # QTimer.singleShot(2000, self.timeout_probing)
        # start to probe images
        self.probing_thread.probing_result.case_info = case_info
        self.probing_thread.finished_probing_signal.connect(self.finished_probing_slot)
        self.probing_thread.start()

        # self.make_mock()
        # json_data = recognition(self.probing_result.case_info.subject_image_url,
        # self.probing_result.case_info.target_image_urls)
        # print(json_data)
        # self.probing_result.json_result = json_data

    @pyqtSlot(ProbingResult)
    def finished_probing_slot(self, probing_result):
        self.stop_gif()
        self.probing_thread.quit()
        self.completed_probing_signal.emit(probing_result)

    @pyqtSlot()
    # a slot to be run when timeout on probing page
    def timeout_probing(self):
        self.stop_gif()
        self.completed_probing_signal.emit(self.probing_result)

    def make_mock(self):
        faces = []
        results = []
        index = 0
        for target_url in self.probing_result.case_info.target_image_urls:
            face = {
                "face_token": index,
                "face_rectangle": {}
            }
            result = {
                "face_path": target_url,
                "confidence": random() * 100
            }
            faces.append(face)
            results.append(result)
        json_buff = {
            "time_used": 467,
            "thresholds": {
                "low": 70,
                "medium": 80,
                "high": 90
            },
            "faces": faces,
            "results": results
        }
        self.probing_result.json_result = json_buff
