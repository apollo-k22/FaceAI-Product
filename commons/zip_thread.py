from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from commons.common import Common
from commons.probing_result import ProbingResult
from commons.gen_report import create_pdf

import os, uuid
from zipfile import ZIP_DEFLATED, ZipFile
from pathlib import Path

class ThreadResult(object):
    def __init__(self):
        super().__init__()
        self.status = False
        self.message = ""

class ZipThread(QThread, ProbingResult):
    finished_zip_signal = pyqtSignal(ThreadResult)

    def __init__(self, probe_result, export_path, parent=None):
        QThread.__init__(self, parent)
        self.reports = probe_result
        self.export_path = export_path 
        self.res = ThreadResult()

    def run(self) -> None:
        self.zip_all_reports()

    def _itertarget(self, target: Path):
        if target.is_file():
            yield target
        elif target.is_dir():
            yield from (t for t in target.rglob('*') if t.is_file())

    def zip_all_reports(self):
        try:  
            zip_file = "%s/faceai_reports.zip"%self.export_path
            temp_folder = "./tmp/" + str(uuid.uuid4()) + "/"
            Common.create_path(temp_folder)            

            for report in self.reports:  
                create_pdf(report.probe_id, report, temp_folder) 
            
            with ZipFile(zip_file, 'w', ZIP_DEFLATED) as allzip:
                for f in self._itertarget(Path(temp_folder)):                    
                    with f.open('rb') as b:
                        data = b.read()
                    filepath = str(f.relative_to(temp_folder))
                    allzip.writestr(filepath, data)  
                    os.remove(temp_folder + filepath)
            os.removedirs(temp_folder)
            
            self.res.status = True
            self.res.message = ""
            self.finished_zip_signal.emit(self.res)
        except Exception as e:
            self.res.status = False
            self.res.message = e
            self.finished_zip_signal.emit(self.res)

        

