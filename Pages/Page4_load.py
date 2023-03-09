from random import random

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QLabel

from commons.case_info import CaseInfo
from commons.probing_result import ProbingResult
from commons.probing_thread import ProbingThread
from insightfaces.main import FaceAI


class LoaderProbingPage(QWidget, FaceAI):
    completed_probing_signal = pyqtSignal(ProbingResult)
    start_splash_signal = pyqtSignal()

    def __init__(self, faceai):
        super().__init__()
        self.faceai = faceai
        self.probing_result = ProbingResult()
        self.probing_thread = ProbingThread(CaseInfo, self.faceai)
        self.processing_gif = QMovie(":/newPrefix/AIFace_Processing.gif")
        self.current_gif = self.processing_gif
        self.failed_gif = QMovie(":/newPrefix/AIFace_Failed.gif")
        self.success_gif = QMovie(":/newPrefix/AIFace_Success.gif")
        self.window = uic.loadUi("./forms/Page_4.ui", self)
        self.lblFaceGif = self.findChild(QLabel, "lblFaceGif")
        self.lblFaceGif.setMovie(self.processing_gif)

    def start_gif(self):
        self.current_gif.start()

    def stop_gif(self):
        self.current_gif.stop()

    def start_probing(self, case_info):
        self.probing_result.case_info = case_info
        self.start_gif()
        # start to probe images
        self.probing_thread.probing_result.case_info = case_info
        self.probing_thread.finished_probing_signal.connect(self.finished_probing_slot)
        self.probing_thread.start()

    @pyqtSlot(ProbingResult)
    def finished_probing_slot(self, probing_result):
        self.stop_gif()
        self.probing_thread.quit()
        self.start_splash_signal.emit()
        self.completed_probing_signal.emit(probing_result)

    @pyqtSlot()
    # a slot to be run when timeout on probing page
    def timeout_probing(self):
        self.stop_gif()
        self.completed_probing_signal.emit(self.probing_result)

