from PyQt5.QtCore import QThread, pyqtSignal
from commons.systimer import SysTimer
from time import sleep

class SysTimerThread(QThread):
    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.clock = None

    def reset(self, clock):
        self.clock = clock

    def run(self) -> None:
        self.timepick()

    def timepick(self):
        while True:
            self.clock.timepick()
            sleep(1)
