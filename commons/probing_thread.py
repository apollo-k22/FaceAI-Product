from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from commons.common import Common
from commons.probing_result import ProbingResult
from insightfaces.main import FaceAI
from commons.case_info import CaseInfo


class ProbingThread(QThread, CaseInfo, FaceAI):
    finished_probing_signal = pyqtSignal(ProbingResult)
    start_splash_signal = pyqtSignal()

    def __init__(self, case_info, faceai, parent=None):
        QThread.__init__(self, parent)
        self.faceai = faceai
        self.probing_result = ProbingResult()
        self.probing_result.case_info = case_info

    def run(self) -> None:
        self.probe_images()

    def probe_images(self):
        json_data = self.faceai.recognition(self.probing_result.case_info.subject_image_url,
                                            self.probing_result.case_info.target_image_urls)
        print(json_data)
        self.probing_result.json_result, self.probing_result.case_info.target_image_urls\
            = self.process_images_url(json_data)
        print("treated data:", self.probing_result.json_result)
        self.start_splash_signal.emit()
        self.finished_probing_signal.emit(self.probing_result)

    def process_images_url(self, json_data):
        ret_json = json_data
        results = json_data["results"]
        faces = json_data["faces"]
        results_buff = []
        faces_buff = []
        targets_buff = []
        if type(results).__name__ == 'list':
            for item in results:
                img_url = item['image_path']
                img_url = img_url.replace("\\", "/")
                item['image_path'] = img_url
                item['confidence'] = Common.round_float_string(item['confidence']) + "%"
                targets_buff.append(img_url)
                results_buff.append(item)
            # sort list by confidence desc
            results_buff = Common.sort_list_by_float_attribute(results_buff, 'confidence', 'string', True)
            ret_json['results'] = results_buff
        if type(faces).__name__ == 'list':
            for item in faces:
                img_url = item['image_path']
                img_url = img_url.replace("\\", "/")
                item['image_path'] = img_url
                faces_buff.append(item)
            ret_json['faces'] = faces_buff
        return ret_json, targets_buff
