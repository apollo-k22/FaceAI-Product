import re

from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMessageBox, QSizePolicy, QWidget, QTextEdit
from PyQt5.QtWidgets import QPushButton

from commons.case_info import CaseInfo
from commons.common import Common
from insightfaces.main import FaceAI


class LoaderCreateNewCasePage(QWidget, FaceAI):
    # when clicked 'return home' button, this will be emitted
    return_home_signal = pyqtSignal(str)
    # when clicked 'continue to probe' button, this will be emitted
    continue_probe_signal = pyqtSignal(object)

    def __init__(self, faceai):
        super().__init__()
        self.faceai = faceai
        self.window = uic.loadUi("./forms/Page_2.ui", self)
        # instance CaseInfo to save the case information
        self.case_info = CaseInfo()
        self.current_work_folder = ""
        # set button and line edit
        self.btnSelectPhoto = self.findChild(QPushButton, 'btnSelectTargetPhoto')
        self.btnReturnHome = self.findChild(QPushButton, 'btnReturnHome')
        self.btnContinueProbe = self.findChild(QPushButton, 'btnContinueProbe')
        self.leditCaseNumber = self.findChild(QLineEdit, 'leditCaseNumber')
        self.leditPS = self.findChild(QLineEdit, 'leditPS')
        self.leditExaminerName = self.findChild(QLineEdit, 'leditExaminerName')
        self.leditExaminerNo = self.findChild(QLineEdit, 'leditExaminerNo')
        self.leditRemarks = self.findChild(QTextEdit, 'teditRemarks')

        # set image url
        self.subject_photo_url = ''
        self.set_event_actions()
        self.set_regxs()
        # self.mock_view()

    # set slots to each widget
    def set_event_actions(self):
        self.btnSelectPhoto.clicked.connect(self.get_subject_photo)
        self.btnReturnHome.clicked.connect(self.return_home)
        self.btnContinueProbe.clicked.connect(self.continue_probe_slot)

    # set regular expression for checking input data
    def set_regxs(self):
        self.set_regx_line_edit(self.leditCaseNumber, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_NUMBER_LENGTH)
        self.set_regx_line_edit(self.leditPS, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_PS_LENGTH)
        self.set_regx_line_edit(self.leditExaminerName, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_EXAMINER_NAME_LENGTH)
        self.set_regx_line_edit(self.leditExaminerNo, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_EXAMINER_NO_LENGTH)
        self.set_regx_plain_text_edit(self.leditRemarks, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_REMARKS_LENGTH)

    # set regular expression for checking on line edit
    def set_regx_line_edit(self, line_edit, regx, length):
        line_edit.textChanged[str].connect(
            lambda txt: self.check_ledit_string_validation(line_edit, regx, txt, length))

    def set_regx_plain_text_edit(self, text_edit, regx, length):
        # text_edit.cursorPositionChanged.connect(lambda: self.check_ptedit_value_validation(text_edit, regx, length))
        text_edit.textChanged.connect(
            lambda: self.check_ptedit_string_validation(text_edit, regx, length))

    @pyqtSlot()
    # get subject photo from file dialog and set the gotten photo on button
    def get_subject_photo(self):
        photo_url, _ = QFileDialog.getOpenFileName(self, 'Open file', self.current_work_folder, Common.IMAGE_FILTER)
        if photo_url:
            self.current_work_folder = Common.get_folder_path(photo_url)
            if self.faceai.is_face(photo_url) == 0:
                Common.show_message(QMessageBox.Warning, "Please select an image with man", "",
                                    "Incorrect image selected.",
                                    "")
                self.subject_photo_url = ""
                self.get_subject_photo()
            elif self.faceai.is_face(photo_url) == 2:
                Common.show_message(QMessageBox.Warning, "Subject photo must be a single photo", "",
                                    "Incorrect image selected.",
                                    "")
                self.subject_photo_url = ""
                self.get_subject_photo()
            else:
                # check the "data storage" folder exist.
                is_exist, root_path = Common.check_exist_data_storage()
                if is_exist:
                    resized_image_path = Common.resize_image(photo_url, self.btnSelectPhoto.size().width())
                    self.subject_photo_url = resized_image_path
                    btn_style = "image:url('" + resized_image_path + "');background:transparent;" \
                                 "border: 1px solid rgb(53, 132, 228);"
                    self.btnSelectPhoto.setStyleSheet(btn_style)
                    self.btnSelectPhoto.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                else:
                    Common.show_message(QMessageBox.Warning, "\"" + root_path + "\" folder does not exist."
                                                             "\nPlease make it and then retry.",
                                        "", "Folder Not Exist", "")
        else:
            self.subject_photo_url = ""
            btn_style = "border:none;background:transparent;" \
                        "image:url(:/newPrefix/Group 68.png);border-radius: 30px;background:none;"
            self.btnSelectPhoto.setStyleSheet(btn_style)

    @pyqtSlot()
    def return_home(self):
        self.return_home_signal.emit("")

    @pyqtSlot()
    def continue_probe_slot(self):
        is_empty, ledit_name = self.is_empty_input_values()
        if is_empty == True:
            Common.show_message(QMessageBox.Warning, "Please fill all fields", "", "Empty Warning",
                                ledit_name + " is empty")
        else:
            self.case_info.case_number = self.leditCaseNumber.text()
            self.case_info.case_PS = self.leditPS.text()
            self.case_info.examiner_no = self.leditExaminerNo.text()
            self.case_info.examiner_name = self.leditExaminerName.text()
            self.case_info.remarks = self.leditRemarks.toPlainText()
            self.case_info.subject_image_url = self.subject_photo_url
            # emit continue probe signal
            self.continue_probe_signal.emit(self.case_info)

    # check whether all input value is empty or not
    # even if one value is empty, return False
    def is_empty_input_values(self):
        if self.leditCaseNumber.text() == '':
            self.leditCaseNumber.setFocus()
            return True, 'Case Number'
        if self.leditPS.text() == '':
            self.leditPS.setFocus()
            return True, 'PS'
        if self.leditExaminerNo.text() == '':
            self.leditExaminerNo.setFocus()
            return True, "Examiner's NO"
        if self.leditExaminerName.text() == '':
            self.leditExaminerName.setFocus()
            return True, "Examiner's Name"
        if self.leditRemarks.toPlainText() == '':
            self.leditRemarks.setFocus()
            return True, "Remarks"
        if self.subject_photo_url == '':
            self.btnSelectPhoto.setFocus()
            return True, "Subject Image Url"
        return False, "All Fields are filled."

    # remove all invalid substring according to regx
    @pyqtSlot(str)
    def check_ledit_string_validation(self, line_edit, regx, txt, max_length):
        sub_string = re.sub(regx, '', txt)
        if not txt == sub_string:
            txt = sub_string
            line_edit.setText(txt)
        if len(txt) > max_length:
            txt = txt[:max_length - 1]
            line_edit.setText(txt)

    # remove all invalid substring according to regx
    @pyqtSlot(str)
    def check_ptedit_string_validation(self, text_edit, regx, max_length):
        string = text_edit.toPlainText()
        if string == '':
            return
        sub_string = re.sub(regx, '', string)
        if not string == sub_string:
            string = sub_string
            text_edit.setPlainText(string)
            return
        if len(string) > max_length:
            string = string[:max_length - 1]
            text_edit.setPlainText(string)
            return
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        text_edit.setTextCursor(cursor)

    # return page to initial status
    def refresh_view(self):
        btn_style = "border:none;background:transparent;" \
                    "image:url(:/newPrefix/Group 68.png);border-radius: 30px;background:none;"
        self.btnSelectPhoto.setStyleSheet(btn_style)
        self.leditCaseNumber.setText("")
        self.leditPS.setText("")
        self.leditExaminerName.setText("")
        self.leditExaminerNo.setText("")
        self.leditRemarks.setText("")
        self.case_info = CaseInfo()

