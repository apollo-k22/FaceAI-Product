from PyQt5.QtWidgets import QPushButton


class ExportPdfButton(QPushButton):
    def __init__(self, probe_result):
        super().__init__()
        self.setStyleSheet("color:rgb(88,156,255);font:12pt 'Arial';max-height:50px")
        self.setText("Export")
        self.probe_result = probe_result
