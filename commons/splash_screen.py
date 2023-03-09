# Creating indicators for Splash Screen animation
# SplashScreen current frame indicator
import sys

from PyQt5.QtCore import QThread, Qt, pyqtSignal, QTimer, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen, QApplication, QDialog, QWidget, QMainWindow, QSizePolicy
import images

splash_i = 0
splash_i_widget = 99
splash_stop = 0  # Stop indicator SplashScreen
max_i_widget = 199  # Max. SplashScreen frame
splash_i_data = 202
max_i_data = 295
max_i = 0
splash_i_buff = 0


# Thread to determine the completion of the SplashScreen
class SplashThread(QThread):
    mysignal = pyqtSignal(int)  # create a signal that will inform about the stop of the timer
    stop_signal = pyqtSignal()
    started_signal = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.splash_screen = QSplashScreen()
        self.splash_screen.setMinimumSize(0, 0)
        self.splash_screen.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.splash_screen.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.splash_screen.setEnabled(False)
        splash_pixmap = QPixmap(':/newPrefix/splash/splash_0.png')
        self.splash_screen.setPixmap(splash_pixmap)
        self.splash_screen.setStyleSheet("background:transparent;")
        self.timer = QTimer()
        self.splash_type = "widget"  # the splash whether while loading widget or data.
        self.start()

    def start_splash(self, data_type):
        global splash_i_widget, splash_i_data, max_i_data, max_i_widget, splash_stop, max_i, splash_i, splash_i_buff

        self.timer.setInterval(0)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.update_splash_screen)
        self.mysignal.connect(self.stop_splash)
        if data_type == "widget":
            print("start splash with widget")
            splash_i_buff = splash_i_widget
            splash_i = splash_i_widget
            max_i = max_i_widget
        else:
            print("start splash with data")
            splash_i = splash_i_data
            splash_i_buff = splash_i_data
            max_i = max_i_data
        self.timer.start()
        self.splash_screen.show()

    # Update SplashScreen animation
    def update_splash_screen(self):
        global splash_i_widget, splash_i_data, max_i_data, max_i_widget, splash_stop, max_i, splash_i, splash_i_buff
        # if the current frame is equal to the maximum, then we slow down the animation timer
        # print("update splash screen")
        self.timer.setInterval(50)
        if splash_i == 583:
            splash_i = 0
            splash_stop = 1
        else:  # otherwise update the frame to the next
            if splash_i < max_i:
                splash_i = splash_i + 1
            else:
                splash_i = splash_i_buff
        pixmap = QPixmap(':/newPrefix/splash/splash_' + str(splash_i) + '.png')
        # pixmap = QPixmap(':/newPrefix/Background.png')
        self.splash_screen.setPixmap(pixmap)

    def run(self):
        # global splash_i, splash_stop, max_i  # connect indicators
        #
        # # Simulate processes
        # start_time = time.time()  # calculate the start of the process
        # time.sleep(3)  # 1 process (duration)
        # t = round(time.time() - start_time)  # calculate the end of the process and its execution time
        # if t < 3: # if the process took less time than we have prepared animation for it
        #     max_i = 90  # stop the frame at the maximum allotted for it
        # elif t >= 3:  # if the process took longer or the same as its animation duration
        #     max_i = max_i + 90  # expand splash screen frames
        #
        # print('splash intro done')
        #
        # start_time = time.time()
        # time.sleep(6)  # 2 process
        # t = round(time.time() - start_time)
        # if t < 3:
        #     max_i = 180
        # elif t >= 3:
        #     max_i = max_i + 90
        #
        # print('loading widgets done')
        #
        # start_time = time.time()
        # time.sleep(2)  # 3 process
        # t = round(time.time() - start_time)
        # if t < 3:
        #     max_i = 270
        # elif t >= 3:
        #     max_i = max_i + 90
        #
        # print('loading data done')
        #
        # start_time = time.time()
        # time.sleep(4)  # 4 process
        # t = round(time.time() - start_time)
        # if t < 3:
        #     max_i = 360
        # elif t >= 3:
        #     max_i = max_i + 90
        #
        # print('loading settings done')
        #
        # start_time = time.time()
        # time.sleep(1)  # 5 process
        # t = round(time.time() - start_time)
        # if t < 3:
        #     max_i = 480
        # elif t >= 3:
        #     max_i = max_i + 103
        #
        # print('loading ram done')
        #
        # time.sleep(3)  # 6 process
        # max_i = 583
        #
        # print('loading by cyberta done')

        # Wait for the entire animation to complete
        while splash_stop == 0:
            QApplication.processEvents()
        if splash_stop == 1:
            self.mysignal.emit(1)  # # send signal from thread to stop SplashScreen

    # Function to stop the timer and close the SplashScreen window
    @pyqtSlot()
    def stop_splash(self, wdt):
        global splash_i, max_i, splash_i_buff
        print("stop splash")
        splash_i = 0
        max_i = 0
        splash_i_buff = 0
        # self.timer.stop()  # stop the timer
        if wdt is not None:
            wdt.show()  # show form
            wdt.setFocus()
        self.splash_screen.hide()  # close SplashScreen

