from random import random

from PyQt5 import uic
from PyQt5.QtCore import QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel
from commons.case_info import CaseInfo

from commons.case_info import CaseInfo
from commons.probing_result import ProbingResult
from insightfaces.main import recognition


class LoaderProbingPage(QMainWindow):
    completed_probing_signal = pyqtSignal(ProbingResult)

    def __init__(self):
        super().__init__()

        self.probing_result = ProbingResult()
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
        QTimer.singleShot(2000, self.timeout_probing)
        jsondata = recognition(self.probing_result.case_info.subject_image_url, self.probing_result.case_info.target_image_urls)
        print(jsondata)
        self.probing_result.json_result = jsondata

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
