from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QPushButton, QFormLayout, QLabel
from commons.common import Common
from commons.db_connection import DBConnection


class ProbeResultItemWidget(QWidget):
    delete_item_signal = pyqtSignal(object)

    def __init__(self, result_item, is_shown_delete_button, is_used_old_cases, parent=None):
        QWidget.__init__(self, parent=parent)
        self.result_item = result_item
        self.is_used_old_cases = is_used_old_cases
        # set whether to show cross button on image
        self.is_showed_cross_button = is_shown_delete_button

        self.vly_item_container = QVBoxLayout(self)

        self.vly_img_container = QVBoxLayout()
        self.vly_info_container = QVBoxLayout()

        self.wdt_image = QWidget()

        if self.is_showed_cross_button:
            self.btn_delete = QPushButton(self.wdt_image)

        self.fly_info_container = QFormLayout()

        self.lbl_similarity_score_label = QLabel()

        self.lbl_similarity_score = QLabel()

        self.lbl_case_number_label = QLabel()

        self.lbl_case_number = QLabel()

        self.lbl_ps_label = QLabel()

        self.lbl_ps = QLabel()

        self.init_view()

    @pyqtSlot()
    def on_clicked_delete(self):
        self.delete_item_signal.emit(self.result_item)

    def resizeEvent(self, event):
        if self.is_showed_cross_button:
            image_geo = self.wdt_image.geometry()
            self.btn_delete.setGeometry(image_geo.width() - Common.CROSS_BUTTON_SIZE,
                                        0, Common.CROSS_BUTTON_SIZE, Common.CROSS_BUTTON_SIZE)

    def init_view(self):
        self.vly_item_container.setSpacing(6)

        self.wdt_image.setGeometry(1, 1, 330, 350)
        self.wdt_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.wdt_image.setMinimumSize(330, 350)
        self.wdt_image.setMaximumSize(400, 500)
        style = ".QWidget{color:rgb(255, 255, 255);border-image:url(" + self.result_item['image_path'] + ");}"
        self.wdt_image.setStyleSheet(style)

        if self.is_showed_cross_button:
            image_geo = self.wdt_image.geometry()
            self.btn_delete.setGeometry(image_geo.width() - Common.CROSS_BUTTON_SIZE,
                                        0, Common.CROSS_BUTTON_SIZE, Common.CROSS_BUTTON_SIZE)
            self.btn_delete.setStyleSheet("image: url(:/newPrefix/cross-icon.png);background:transparent;border:none")
            self.btn_delete.clicked.connect(self.on_clicked_delete)

        self.vly_img_container.addWidget(self.wdt_image)

        self.lbl_similarity_score_label.setText("Similarity Score: ")
        self.lbl_similarity_score_label.setMaximumSize(Common.LABEL_MAX_WIDTH_IN_ITEM, Common.LABEL_MAX_HEIGHT_IN_ITEM)
        self.lbl_similarity_score.setMaximumSize(Common.VALUE_MAX_WIDTH_IN_ITEM, Common.VALUE_MAX_WIDTH_IN_ITEM)

        self.lbl_case_number_label.setText("Case Number: ")
        self.lbl_case_number.setMaximumSize(Common.VALUE_MAX_WIDTH_IN_ITEM, Common.VALUE_MAX_WIDTH_IN_ITEM)
        self.lbl_case_number_label.setMaximumSize(Common.LABEL_MAX_WIDTH_IN_ITEM, Common.LABEL_MAX_HEIGHT_IN_ITEM)

        self.lbl_ps_label.setText("PS: ")
        self.lbl_ps.setMaximumSize(Common.LABEL_MAX_WIDTH_IN_ITEM, Common.LABEL_MAX_HEIGHT_IN_ITEM)
        self.lbl_ps_label.setMaximumSize(Common.VALUE_MAX_WIDTH_IN_ITEM, Common.VALUE_MAX_WIDTH_IN_ITEM)

        self.fly_info_container.addRow(self.lbl_similarity_score_label, self.lbl_similarity_score)
        self.fly_info_container.addRow(self.lbl_case_number_label, self.lbl_case_number)
        self.fly_info_container.addRow(self.lbl_ps_label, self.lbl_ps)
        self.vly_info_container.addLayout(self.fly_info_container)

        self.vly_item_container.addLayout(self.vly_img_container)
        self.vly_item_container.addLayout(self.vly_info_container)

        if self.result_item['confidence']:
            self.lbl_similarity_score.setText(str(self.result_item['confidence']))
        if self.is_used_old_cases:
            db = DBConnection()
            case_no, ps = db.get_case_info(self.result_item['image_path'])
            self.lbl_case_number.setText(case_no)
            self.lbl_ps.setText(ps)

