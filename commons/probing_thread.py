from PyQt5.QtCore import QThread, pyqtSignal

from commons.probing_result import ProbingResult
from insightfaces.main import recognition


class ProbingThread(QThread):
    finished_probing_signal = pyqtSignal(ProbingResult)

    def __init__(self, case_info, parent=None):
        QThread.__init__(self, parent)
        self.probing_result = ProbingResult()
        self.probing_result.case_info = case_info

    def run(self) -> None:
        self.probe_images()

    def probe_images(self):
        json_data = recognition(self.probing_result.case_info.subject_image_url,
                                self.probing_result.case_info.target_image_urls)
        print(json_data)
        self.probing_result.json_result = json_data
        self.finished_probing_signal.emit(self.probing_result)
    # def start(self, priority: 'QThread.Priority' = ...) -> None:
    #     self.start()
    #
    # def run(self) -> None:
    #     self.run()
