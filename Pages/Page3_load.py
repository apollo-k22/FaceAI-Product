import pathlib

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QPushButton, QRadioButton, QStackedWidget, QFileDialog, QMessageBox

from commons.case_info import CaseInfo
from commons.common import Common


class LoaderSelectTargetPhotoPage(QMainWindow):
    go_back_signal = pyqtSignal()
    start_probe_signal = pyqtSignal(object)
    return_home_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.window = uic.loadUi("./forms/Page_3.ui", self)
        self.case_info = CaseInfo()
        self.image_urls = []
        self.cmdbtnGoBack = self.findChild(QPushButton, "cmdbtnGoBack")
        self.btnStartProbe = self.findChild(QPushButton, "btnStartProbe")
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.rdobtnSinglePhoto = self.findChild(QRadioButton, "rdobtnSinglePhoto")
        self.rdobtnMultiPhoto = self.findChild(QRadioButton, "rdobtnMultiPhoto")
        self.rdobtnEntireFolder = self.findChild(QRadioButton, "rdobtnEntireFolder")
        self.rdobtnOldCasePhoto = self.findChild(QRadioButton, "rdobtnOldCasePhoto")
        self.btnSinglePhoto = self.findChild(QPushButton, "btnSinglePhoto")
        self.btnMultiPhoto = self.findChild(QPushButton, "btnMultiPhoto")
        self.btnEntireFolder = self.findChild(QPushButton, "btnEntireFolder")
        self.stkwdtSelectPhotos = self.findChild(QStackedWidget, "stkwdtSelectPhotos")
        self.stkwdtSelectPhotos.setCurrentIndex(0)
        self.init_actions()
        #
        self.image_urls = ["Background.png",
                           "book-1.jpg",
                           "book-2.jpg",
                           "book-3.jpg",
                           "book-4.jpg",
                           "pro4.jpg",
                           "profile-bg.jpg",
                           ]

    @pyqtSlot()
    def start_probe_slot(self):
        if self.case_info.subject_image_url == '':
            Common.show_message(QMessageBox.Warning, "Please select subject image.", "", "Empty Warning", "")
            self.go_back_signal.emit()
        else:
            if len(self.image_urls) == 0:
                Common.show_message(QMessageBox.Warning, "Please select target images.", "", "Empty Warning", "")
            else:
                self.case_info.target_image_urls = self.image_urls
                self.start_probe_signal.emit(self.case_info)

    @pyqtSlot()
    def return_home_slot(self):
        self.return_home_signal.emit()

    @pyqtSlot()
    def go_back_slot(self):
        self.go_back_signal.emit()

    @pyqtSlot()
    def select_photo_mode_slot(self, checked, index):
        if checked:
            self.stkwdtSelectPhotos.setCurrentIndex(index)
            # if selected old cases, select images from that folder
            if index == 3:
                self.select_from_old_cases()

    @pyqtSlot()
    def select_single_photo_slot(self):
        self.image_urls.clear()
        url, _ = QFileDialog.getOpenFileName(self, 'Open File', "Image files", Common.IMAGE_FILTER)
        if url:
            # create icon with selected file name
            icon = QIcon(url)
            # get button size
            btnSize = self.btnSinglePhoto.rect().size()
            self.btnSinglePhoto.setIcon(icon)
            # set image size to button size
            self.btnSinglePhoto.setIconSize(btnSize)
            self.image_urls.append(url)

    @pyqtSlot()
    def select_multi_photo_slot(self):
        self.image_urls.clear()
        self.image_urls, _ = QFileDialog.getOpenFileNames(self, 'Open Files', "Image files", Common.IMAGE_FILTER)

    @pyqtSlot()
    def select_entire_folder_slot(self):
        self.image_urls.clear()
        direct = QFileDialog.getExistingDirectory(self, 'Entire Folder')
        desktop = pathlib.Path(direct)
        for path in desktop.glob(r'**/*'):
            if Common.EXTENSIONS.count(path.suffix):
                self.image_urls.append(path)

    # get all images from old cases
    def select_from_old_cases(self):
        self.image_urls.clear()
        desktop = pathlib.Path(Common.MEDIA_PATH)
        for path in desktop.glob(r'**/*'):
            if path.suffix in Common.EXTENSIONS:
                self.image_urls.append(path)

    # make file filter for QFileDialog from Common.EXTENSIONS
    def make_file_filter(self):
        file_filter = ' *.'.join([str(a) for a in Common.EXTENSIONS])
        file_filter = '"Images (*.' + file_filter + ')"'
        return file_filter

    # initiate actions for window
    def init_actions(self):
        # connect(pageComboBox, SIGNAL(activated(int)),
        #         stackedWidget, SLOT(setCurrentIndex(int)));
        self.btnStartProbe.clicked.connect(self.start_probe_slot)
        self.btnReturnHome.clicked.connect(self.return_home_slot)
        self.cmdbtnGoBack.clicked.connect(self.go_back_slot)
        self.btnSinglePhoto.clicked.connect(self.select_single_photo_slot)
        self.btnMultiPhoto.clicked.connect(self.select_multi_photo_slot)
        self.btnEntireFolder.clicked.connect(self.select_entire_folder_slot)

        self.rdobtnSinglePhoto.toggled[bool].connect(
            lambda checked:
            self.select_photo_mode_slot(checked, 0)
        )
        self.rdobtnMultiPhoto.toggled[bool].connect(
            lambda checked:
            self.select_photo_mode_slot(checked, 1)
        )
        self.rdobtnEntireFolder.toggled[bool].connect(
            lambda checked:
            self.select_photo_mode_slot(checked, 2)
        )
        self.rdobtnOldCasePhoto.toggled[bool].connect(
            lambda checked:
            self.select_photo_mode_slot(checked, 3)
        )
