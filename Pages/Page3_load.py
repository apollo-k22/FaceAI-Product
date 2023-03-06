import pathlib

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QRadioButton, QStackedWidget, QFileDialog, QMessageBox, QLabel, \
    QSizePolicy, QWidget

from commons.case_info import CaseInfo
from commons.common import Common


class LoaderSelectTargetPhotoPage(QWidget):
    go_back_signal = pyqtSignal()
    start_probe_signal = pyqtSignal(object)
    return_home_signal = pyqtSignal()

    def __init__(self, faceai):
        super().__init__()

        self.window = uic.loadUi("./forms/Page_3.ui", self)
        self.case_info = CaseInfo()
        self.faceai = faceai
        self.image_urls = []
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
        self.stkwdtSelectPhotos = self.findChild(QStackedWidget, "stkwdtSelectPhotos")
        self.stkwdtSelectPhotos.setCurrentIndex(0)
        self.init_actions()
        #
        self.image_urls = ["E:/freelancing/inpregress/faceAI-Team/New folder/FaceAI_App_Demo/student/1.jpg",
                           "E:/freelancing/inpregress/faceAI-Team/New folder/FaceAI_App_Demo/student/2.jpg",
                           "E:/freelancing/inpregress/faceAI-Team/New folder/FaceAI_App_Demo/student/3.jpg",
                           "E:/freelancing/inpregress/faceAI-Team/New folder/FaceAI_App_Demo/student/4.jpg",
                           "E:/freelancing/inpregress/faceAI-Team/New folder/FaceAI_App_Demo/student/huge2.png",
                           "E:/freelancing/inpregress/faceAI-Team/New folder/FaceAI_App_Demo/student/huge3.jpg"
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
        url, _ = QFileDialog.getOpenFileName(self, 'Open File', self.current_work_folder, Common.IMAGE_FILTER)
        if url:
            if not self.faceai.is_face(url):
                Common.show_message(QMessageBox.Warning, "Please select an image with man", "",
                                    "Incorrect image selected.",
                                    "")
            else:
                self.current_work_folder = Common.get_folder_path(url)
                btn_style = "image:url(" + url + ");height: auto;border: 1px solid rgb(53, 132, 228);"
                # self.btnSinglePhoto.setStyleSheet(btn_style)
                # btn_style = "background:transparent;border: 1px solid rgb(53, 132, 228);"
                self.btnSinglePhoto.setStyleSheet(btn_style)
                # btn_icon = QIcon(url)
                # btn_rect = self.btnSinglePhoto.size()
                # self.btnSinglePhoto.setIcon(btn_icon)
                # self.btnSinglePhoto.setIconSize(btn_rect)
                self.btnSinglePhoto.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                self.image_urls.append(url)

    @pyqtSlot()
    def select_multi_photo_slot(self):
        self.image_urls.clear()
        urls, _ = QFileDialog.getOpenFileNames(self, 'Open Files', self.current_work_folder, Common.IMAGE_FILTER)
        length = len(urls)
        if length:
            self.current_work_folder = Common.get_folder_path(urls[0])
            self.lblMultiPhotos.setText(str(length) + " was selected.")
        else:
            self.lblMultiPhotoResult.setText("There are no raster images in selected folder.")
        for url in urls:
            if self.faceai.is_face(url):
                url_buff = Common.resize_image(url)
                self.image_urls.append(url_buff)

    @pyqtSlot()
    def select_entire_folder_slot(self):
        self.image_urls.clear()
        direct = QFileDialog.getExistingDirectory(self, 'Entire Folder')
        self.current_work_folder = direct
        desktop = pathlib.Path(direct)
        self.lblEntireFolder.setText(direct)
        for url in desktop.glob(r'**/*'):
            # url = url.__str__()
            if Common.EXTENSIONS.count(url.suffix):
                if self.faceai.is_face(url):
                    url = Common.resize_image(url)
                    self.image_urls.append(url)
        if len(self.image_urls) == 0:
            self.lblEntireResult.setText("There are no raster images in this folder.")

    # get all images from old cases
    def select_from_old_cases(self):
        self.image_urls.clear()
        self.case_info.is_used_old_cases = True
        desktop = pathlib.Path(Common.MEDIA_PATH + "/targets")
        for url in desktop.glob(r'**/*'):
            if url.suffix in Common.EXTENSIONS:
                self.image_urls.append(url)
        if not len(self.image_urls):
            self.lblOldCaseResult.setText("There are no old cases images. Please select manually on other tab.")

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

    def refresh_view(self):
        btn_style = "background:transparent;border:0px;border-image:url(:/newPrefix/Group 67.png);"
        self.btnSinglePhoto.setStyleSheet(btn_style)
        self.lblMultiPhotos.setText("Select target photos")
        self.lblMultiPhotoResult.setText("Raster image formats are accepted")
        self.lblEntireFolder.setText("Select target folder")
        self.lblEntireResult.setText("Raster image formats are accepted")
        self.lblOldCaseResult.setText("Click on the \"Start probe\" button below to continue the further process.")
