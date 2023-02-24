from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QRegularExpression, pyqtSignal
from PyQt5.QtCore import pyqtSlot
from sympy import false, true
from commons.common import Common
from commons.case_info import CaseInfo
from insightfaces.main import recognition


class LoaderCreateNewCasePage(QMainWindow):
    # when clicked 'return home' button, this will be emitted
    return_home_signal = pyqtSignal()
    # when clicked 'continue to probe' button, this will be emitted
    continue_probe_signal = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.window = uic.loadUi("./forms/Page_2.ui", self)
        # instance CaseInfo to save the case information
        self.case_info = CaseInfo()
        # set button and line edit
        self.btnSelectPhoto = self.findChild(QPushButton, 'btnSelectTargetPhoto')
        self.btnReturnHome = self.findChild(QPushButton, 'btnReturnHome')
        self.btnContinueProbe = self.findChild(QPushButton, 'btnContinueProbe')
        self.leditCaseNumber = self.findChild(QLineEdit, 'leditCaseNumber')
        self.leditPS = self.findChild(QLineEdit, 'leditPS')
        self.leditExaminerName = self.findChild(QLineEdit, 'leditExaminerName')
        self.leditExaminerNo = self.findChild(QLineEdit, 'leditExaminerNo')
        self.leditRemarks = self.findChild(QLineEdit, 'leditRemarks')

        # recognition(
        #     r'C:\Users\marko\Documents\Work\20230211\03_Work\test_images\ttt3.png',
        #     [r'C:\Users\marko\Documents\Work\20230211\03_Work\test_images\ttt4.png']);

        # set image url
        self.subject_photo_url = ''
        self.set_event_actions()
        self.set_regxs()

        # init for testing
        # self.leditCaseNumber.setText("1231")
        # self.leditPS.setText("ps1")
        # self.leditExaminerName.setText("examiner")
        # self.leditExaminerNo.setText("examiner no")
        # self.leditRemarks.setText("remarks")
        # self.subject_photo_url = "Architecture.png"

    # set slots to each widget
    def set_event_actions(self):
        self.btnSelectPhoto.clicked.connect(self.get_subject_photo)
        self.btnReturnHome.clicked.connect(self.return_home)
        self.btnContinueProbe.clicked.connect(self.continue_probe_slot)

    # set regular expression for checking input data
    def set_regxs(self):
        self.set_regx_line_edit(self.leditCaseNumber, Common.CREATE_CASE_REGX, Common.CASE_NUMBER_LENGTH)
        self.set_regx_line_edit(self.leditPS, Common.CREATE_CASE_REGX, Common.CASE_PS_LENGTH)
        self.set_regx_line_edit(self.leditExaminerName, Common.CREATE_CASE_REGX, Common.CASE_EXAMINER_NAME_LENGTH)
        self.set_regx_line_edit(self.leditExaminerNo, Common.CREATE_CASE_REGX, Common.CASE_EXAMINER_NO_LENGTH)
        self.set_regx_line_edit(self.leditRemarks, Common.CREATE_CASE_REGX, Common.CASE_REMARKS_LEGNTH)

    # set regular expression for checking on line edit
    def set_regx_line_edit(self, line_edit, regx, length):
        line_edit.cursorPositionChanged[int, int].connect(
            lambda oldPos, newPos:
            self.check_value_validation(line_edit, newPos, regx, length)
        )

    @pyqtSlot()
    # get subject photo from file dialog and set the gotten photo on button
    def get_subject_photo(self):
        self.subject_photo_url, _ = QFileDialog.getOpenFileName(self, 'Open file', "Image files", Common.IMAGE_FILTER)
        if self.subject_photo_url:
            # create icon with selected file name
            icon = QIcon(self.subject_photo_url)
            # get button size
            btn_size = self.btnSelectPhoto.rect().size()
            self.btnSelectPhoto.setIcon(icon)
            # set image size to button size
            self.btnSelectPhoto.setIconSize(btn_size)

    # a slot to call whenever move cursor on line edit.
    @pyqtSlot(int, int)
    def check_value_validation(self, lineEdit, pos, regx, strLength):
        regx = QRegularExpression(regx)
        # set regx option to use unicode printable characters
        regx.setPatternOptions(QRegularExpression.UseUnicodePropertiesOption)
        text = lineEdit.text()
        if (pos != 0):
            match = regx.match(text[pos - 1])
            # check whether valid the latest input character
            if not match.hasMatch():
                text = text[:pos - 1] + text[pos:]
            # check whether length of text of line edit is over strLength or not
            # if over, remove the fulfill characters
            if len(text) > strLength:
                text = text[:strLength - 1]
            # set string to line edit
            lineEdit.setText(text)

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
            # init the case data for next probe step
            self.case_info.case_number = self.leditCaseNumber.text()
            self.case_info.case_PS = self.leditPS.text()
            self.case_info.examiner_no = self.leditExaminerNo.text()
            self.case_info.examiner_name = self.leditExaminerName.text()
            self.case_info.remarks = self.leditRemarks.text()
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
        if self.leditRemarks.text() == '':
            self.leditRemarks.setFocus()
            return true, "Remarks"
        if self.subject_photo_url == '':
            self.btnSelectPhoto.setFocus()
            return true, "Subject Image Url"
        return false, "All Fields are filled."
