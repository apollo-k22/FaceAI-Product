import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

# start home page for probing
from Pages.MainPage_load import StartMain
from commons.qss import QSS
from commons.splash_screen import SplashThread
from cryptophic.main import exit_process

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(QSS)
        # start splash screen
        # global for splash
        global_splash = SplashThread()
        global_splash.splash_type = "widget"

        window = StartMain(global_splash)
        window.finished_initiating_widget_signal.connect(
            lambda wdt: global_splash.stop_splash(wdt))
        window.start_splash_signal.connect(global_splash.start_splash)
        global_splash.start_splash()
        app.exec_()
    finally:
        exit_process()
        print("exit")
