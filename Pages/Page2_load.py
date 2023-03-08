import re

from PyQt5 import uic
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QMessageBox, QSizePolicy, QWidget, QPlainTextEdit, QTextEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QRegularExpression, pyqtSignal
from PyQt5.QtCore import pyqtSlot
from sympy import false, true
from commons.common import Common
from commons.case_info import CaseInfo
from insightfaces.main import FaceAI


class LoaderCreateNewCasePage(QWidget, FaceAI):
    # when clicked 'return home' button, this will be emitted
    return_home_signal = pyqtSignal()
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
        # self.set_regx_line_edit(self.leditCaseNumber, Common.CREATE_CASE_REGX, Common.CASE_NUMBER_LENGTH)
        # self.set_regx_line_edit(self.leditPS, Common.CREATE_CASE_REGX, Common.CASE_PS_LENGTH)
        # self.set_regx_line_edit(self.leditExaminerName, Common.CREATE_CASE_REGX, Common.CASE_EXAMINER_NAME_LENGTH)
        # self.set_regx_line_edit(self.leditExaminerNo, Common.CREATE_CASE_REGX, Common.CASE_EXAMINER_NO_LENGTH)
        # self.set_regx_plain_text_edit(self.leditRemarks, Common.CREATE_CASE_REGX, Common.CASE_REMARKS_LENGTH)
        self.set_regx_line_edit(self.leditCaseNumber, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_NUMBER_LENGTH)
        self.set_regx_line_edit(self.leditPS, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_PS_LENGTH)
        self.set_regx_line_edit(self.leditExaminerName, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_EXAMINER_NAME_LENGTH)
        self.set_regx_line_edit(self.leditExaminerNo, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_EXAMINER_NO_LENGTH)
        self.set_regx_plain_text_edit(self.leditRemarks, Common.CREATE_CASE_REGX_FOR_REMOVE, Common.CASE_REMARKS_LENGTH)

    # set regular expression for checking on line edit
    def set_regx_line_edit(self, line_edit, regx, length):
        # line_edit.cursorPositionChanged[int, int].connect(
        #     lambda oldPos, newPos:
        #     self.check_ledit_value_validation(line_edit, newPos, regx, length)
        # )
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
            if not self.faceai.is_face(photo_url):
                Common.show_message(QMessageBox.Warning, "Please select an image with man", "",
                                    "Incorrect image selected.",
                                    "")
                self.subject_photo_url = ""
                # btn_style = "border-image:url("");"
                # self.btnSelectPhoto.setStyleSheet(btn_style)
                self.get_subject_photo()
            else:
                Common.resize_image(photo_url, self.btnSelectPhoto.size().width())
                self.subject_photo_url = photo_url
                btn_style = "image:url(" + self.subject_photo_url + ");background:transparent;" \
                             "border: 1px solid rgb(53, 132, 228);background-size:cover;"
                self.btnSelectPhoto.setStyleSheet(btn_style)
                self.btnSelectPhoto.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        else:
            self.subject_photo_url = ""
            btn_style = "image:url(" + self.subject_photo_url + ");background:transparent;" \
                        "border: 1px solid rgb(53, 132, 228);background-size:cover;"
            self.btnSelectPhoto.setStyleSheet(btn_style)

    @pyqtSlot()
    def return_home(self):
        self.return_home_signal.emit()

    @pyqtSlot()
    def continue_probe_slot(self):
        is_empty, ledit_name = self.is_empty_input_values()
        if is_empty == true:
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
    # even if one value is empty, return false
    def is_empty_input_values(self):
        if self.leditCaseNumber.text() == '':
            self.leditCaseNumber.setFocus()
            return true, 'Case Number'
        if self.leditPS.text() == '':
            self.leditPS.setFocus()
            return true, 'PS'
        if self.leditExaminerNo.text() == '':
            self.leditExaminerNo.setFocus()
            return true, "Examiner's NO"
        if self.leditExaminerName.text() == '':
            self.leditExaminerName.setFocus()
            return true, "Examiner's Name"
        if self.leditRemarks.toPlainText() == '':
            self.leditRemarks.setFocus()
            return true, "Remarks"
        if self.subject_photo_url == '':
            self.btnSelectPhoto.setFocus()
            return true, "Subject Image Url"
        return false, "All Fields are filled."

    # # a slot to call whenever move cursor on line edit.
    # @pyqtSlot(int, int)
    # def check_ledit_value_validation(self, line_edit, pos, regx, str_len):
    #     regx = QRegularExpression(regx)
    #     # set regx option to use unicode printable characters
    #     regx.setPatternOptions(QRegularExpression.UseUnicodePropertiesOption)
    #     text = line_edit.text()
    #     if pos != 0:
    #         match = regx.match(text[pos - 1])
    #         # check whether valid the latest input character
    #         if not match.hasMatch():
    #             text = text[:pos - 1] + text[pos:]
    #             # set string to line edit
    #             line_edit.setText(text)
    #         # check whether length of text of line edit is over str_len or not
    #         # if over, remove the fulfill characters
    #         if len(text) > str_len:
    #             text = text[:str_len - 1]
    #             # set string to line edit
    #             line_edit.setText(text)
    #
    # @pyqtSlot()
    # def check_ptedit_value_validation(self, text_edit, regx, length):
    #     regx = QRegularExpression(regx)
    #     # set regx option to use unicode printable characters
    #     regx.setPatternOptions(QRegularExpression.UseUnicodePropertiesOption)
    #     text = text_edit.toPlainText()
    #     cursor = text_edit.textCursor()
    #     cursor.movePosition(QTextCursor.End)
    #     text_edit.setTextCursor(cursor)
    #     # cursor.deletePreviousChar()
    #     newPos = text_edit.textCursor().position()
    #     print("newPos in text edit", newPos)
    #     print("text" , text)
    #     if newPos != 0:
    #         match = regx.match(text[newPos - 1])
    #         # check whether valid the latest input character
    #         if not match.hasMatch():
    #             text = text[:newPos - 1] + text[newPos:]
    #             print("when appear non matched text:", text)
    #             text_edit.setPlainText(text)
    #         # check whether length of text of line edit is over str_len or not
    #         # if over, remove the fulfill characters
    #         if len(text) > length:
    #             text = text[:length - 1]
    #             print("when exceed len text:", text)
    #             text_edit.setPlainText(text)

    # remove all invalid substring according to regx
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
        btn_style = "content-aligne:left;border:none;background:transparent;" \
                    "border-image:url(:/newPrefix/Group 68.png);border-radius: 30px;background:none;"
        self.btnSelectPhoto.setStyleSheet(btn_style)
        self.leditCaseNumber.setText("")
        self.leditPS.setText("")
        self.leditExaminerName.setText("")
        self.leditExaminerNo.setText("")
        self.leditRemarks.setText("")

    def mock_view(self):
        # init for testing
        self.leditCaseNumber.setText("1231")
        self.leditPS.setText("ps1")
        self.leditExaminerName.setText("examiner")
        self.leditExaminerNo.setText("examiner no")
        self.leditRemarks.setText("remarks")
        self.subject_photo_url = "Architecture.png"
        self.btnSelectPhoto.setStyleSheet("image:url(Architecture.png);")
        self.repaint()