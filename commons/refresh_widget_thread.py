from PyQt5.QtCore import QThread, pyqtSignal


class RefreshWidgetThread(QThread):
    finished_refreshing_widget = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget = None  # the widget to be refreshed.

    def set_widget(self, wdt):
        self.widget = wdt

    def run(self) -> None:
        self.refresh_views()

    def refresh_views(self):
        print("start refresh")
        self.widget.refresh_views()
        print("stop refresh")
        self.finished_refreshing_widget.emit(self.widget)


