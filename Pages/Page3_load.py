import pathlib

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QShowEvent
from PyQt5.QtWidgets import QPushButton, QRadioButton, QStackedWidget, QFileDialog, QMessageBox, QLabel, \
    QSizePolicy, QWidget

from commons.case_info import CaseInfo
from commons.common import Common
from commons.get_images_thread import GetImagesThread


class LoaderSelectTargetPhotoPage(QWidget):
    go_back_signal = pyqtSignal()
    start_probe_signal = pyqtSignal(object)
    return_home_signal = pyqtSignal(str)
    start_splash_signal = pyqtSignal(str)
    stop_splash_signal = pyqtSignal(object)

    def __init__(self, faceai):
        super().__init__()

        self.window = uic.loadUi("./forms/Page_3-Copy.ui", self)
        self.case_info = CaseInfo()
        self.faceai = faceai
        self.image_urls = []
        self.get_images_thread = GetImagesThread(faceai, [])
        self.current_work_folder = ""
        self.cmdbtnGoBack = self.findChild(QPushButton, "cmdbtnGoBack")
        self.btnStartProbe = self.findChild(QPushButton, "btnStartProbe")
        self.btnReturnHome = self.findChild(QPushButton, "btnReturnHome")
        self.rdobtnSinglePhoto = self.findChild(QRadioButton, "rdobtnSinglePhoto")
        self.rdobtnMultiPhoto = self.findChild(QRadioButton, "rdobtnMultiPhoto")
        self.rdobtnEntireFolder = self.findChild(QRadioButton, "rdobtnEntireFolder")
        self.rdobtnOldCasePhoto = self.findChild(QRadioButton, "rdobtnOldCasePhoto")
        self.btnSinglePhoto = self.findChild(QPushButton, "btnSinglePhoto")
        self.btnMultiPhoto = self.findChild(QPushButton, "btnMultiPhoto")
        self.lblMultiPhotos = self.findChild(QLabel, "lblMultiPhotos")
        self.lblMultiPhotoResult = self.findChild(QLabel, "lblMultiResult")
        self.btnEntireFolder = self.findChild(QPushButton, "btnEntireFolder")
        self.lblEntireFolder = self.findChild(QLabel, "lblEntireFolder")
        self.lblEntireResult = self.findChild(QLabel, "lblEntireFolderResult")
        self.lblOldCaseResult = self.findChild(QLabel, "lblOldCaseResult")
        self.lblOldCaseSelectedNumber = self.findChild(QLabel, "lblOldCaseSelectedNumber")
        self.stkwdtSelectPhotos = self.findChild(QStackedWidget, "stkwdtSelectPhotos")
        self.stkwdtSelectPhotos.setCurrentIndex(0)
        self.init_actions()

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
        self.return_home_signal.emit("")

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

    @pyqtSlot(list)
    def get_images_slot(self, urls):
        self.setEnabled(True)
        self.image_urls = urls
        if self.get_images_thread.is_urls:
            self.get_images_thread.is_urls = False
            if len(self.image_urls) == 0:
                self.lblMultiPhotoResult.setText("There are no raster images in this folder.")
            else:
                self.lblMultiPhotos.setText(str(len(self.image_urls)) + " was selected.")
        if self.get_images_thread.is_direct:
            self.get_images_thread.is_direct = False
            if len(self.image_urls) == 0:
                self.lblEntireResult.setText("There are no raster images in this folder.")
            else:
                self.lblEntireFolder.setText(str(len(self.image_urls)) + " was selected.")
        if self.case_info.is_used_old_cases:
            # self.case_info.is_used_old_cases = False
            if not len(self.image_urls):
                self.lblOldCaseSelectedNumber.setText("")
                self.lblOldCaseResult.setText("There are no old cases images. Please select manually on other tab.")
            else:
                self.lblOldCaseResult.setText(
                    "Click on the \"Start probe\" button below to continue the further process.")
                self.lblOldCaseSelectedNumber.setText(str(len(self.image_urls)) + " was selected.")
        self.stop_splash_signal.emit(None)

    @pyqtSlot()
    def select_single_photo_slot(self):
        self.refresh_view()
        url, _ = QFileDialog.getOpenFileName(self, 'Open File', self.current_work_folder, Common.IMAGE_FILTER)
        if url:
            if not self.faceai.is_face(url):
                Common.show_message(QMessageBox.Warning, "Please select an image with man", "",
                                    "Incorrect image selected.",
                                    "")
            else:
                self.current_work_folder = Common.get_folder_path(url)
                Common.resize_image(url, self.btnSinglePhoto.size().width())
                btn_style = "image:url(" + url + ");height: auto;border: 1px solid rgb(53, 132, 228);"
                self.btnSinglePhoto.setStyleSheet(btn_style)
                self.btnSinglePhoto.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                self.image_urls.append(url)
        else:
            btn_style = "border: 1px solid rgb(53, 132, 228);image:url(:/newPrefix/Group 67.png);"
            self.btnSinglePhoto.setStyleSheet(btn_style)

    @pyqtSlot()
    def select_multi_photo_slot(self):
        self.refresh_view()
        urls, _ = QFileDialog.getOpenFileNames(self, 'Open Files', self.current_work_folder, Common.IMAGE_FILTER)
        length = len(urls)
        if length:
            self.lblMultiPhotos.setText("")
            self.setEnabled(False)
            self.current_work_folder = Common.get_folder_path(urls[0])
            self.get_images_thread.urls = urls
            self.get_images_thread.is_urls = True
            self.start_splash_signal.emit("data")
            self.get_images_thread.start()
        else:
            self.lblMultiPhotos.setText("Select target images.")
            self.lblMultiPhotoResult.setText("Raster image formats are accepted.")

    @pyqtSlot()
    def select_entire_folder_slot(self):
        self.refresh_view()
        direct = QFileDialog.getExistingDirectory(self, 'Entire Folder')

        if direct:
            self.lblEntireFolder.setText("")
            self.current_work_folder = direct
            self.get_images_thread.direct = direct
            self.get_images_thread.is_direct = True
            self.setEnabled(False)
            self.start_splash_signal.emit("data")
            self.get_images_thread.start()

        else:
            self.lblEntireFolder.setText("Select target folder.")
            self.lblEntireResult.setText("Raster image formats are accepted.")

    # get all images from old cases
    def select_from_old_cases(self):
        self.refresh_view()
        self.lblOldCaseResult.setText("Loading images from old cases.... ")
        self.setEnabled(False)
        # start splash
        self.start_splash_signal.emit("data")
        self.image_urls.clear()
        self.case_info.is_used_old_cases = True
        reg_val = Common.get_reg(Common.REG_KEY)
        targets_path = ""
        if reg_val:
            targets_path = Common.get_reg(Common.REG_KEY) + "/" + Common.MEDIA_PATH + "/targets"
        else:
            targets_path = Common.MEDIA_PATH + "/targets"
        self.get_images_thread.is_direct = True
        self.get_images_thread.direct = targets_path
        self.get_images_thread.start()

    # make file filter for QFileDialog from Common.EXTENSIONS
    def make_file_filter(self):
        file_filter = ' *.'.join([str(a) for a in Common.EXTENSIONS])
        file_filter = '"Images (*.' + file_filter + ')"'
        return file_filter

    # initiate actions for window
    def init_actions(self):
        self.btnStartProbe.clicked.connect(self.start_probe_slot)
        self.btnReturnHome.clicked.connect(self.return_home_slot)
        self.cmdbtnGoBack.clicked.connect(self.go_back_slot)
        self.btnSinglePhoto.clicked.connect(self.select_single_photo_slot)
        self.btnMultiPhoto.clicked.connect(self.select_multi_photo_slot)
        self.btnEntireFolder.clicked.connect(self.select_entire_folder_slot)
        self.get_images_thread.finished_get_images_signal.connect(
            lambda urls: self.get_images_slot(urls))

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

    def refresh_view(self):
        self.image_urls.clear()
        self.case_info.target_image_urls.clear()
        self.case_info.is_used_old_cases = False
        btn_style = "background:transparent;border:0px;image:url(:/newPrefix/Group 67.png);"
        self.btnSinglePhoto.setStyleSheet(btn_style)
        self.lblMultiPhotos.setText("Select target photos.")
        self.lblMultiPhotoResult.setText("Raster image formats are accepted.")
        self.lblEntireFolder.setText("Select target folder.")
        self.lblEntireResult.setText("Raster image formats are accepted.")
        self.lblOldCaseSelectedNumber.setText("")
        self.lblOldCaseResult.setText("Click on the \"Start probe\" button below to continue the further process.")
        self.repaint()

    def showEvent(self, a0: QShowEvent) -> None:
        super(LoaderSelectTargetPhotoPage, self).showEvent(a0)
        self.refresh_view()

    def init_views(self):
        self.refresh_view()
        self.stkwdtSelectPhotos.setCurrentIndex(0)
        self.rdobtnSinglePhoto.setChecked(True)
