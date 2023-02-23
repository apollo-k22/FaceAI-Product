from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QPushButton, QFormLayout, QLabel


class ProbeResultItemWidget(QWidget):
    delete_item_signal = pyqtSignal(object)

    def __init__(self, result_item, parent=None):
        QWidget.__init__(self, parent=parent)
        self.result_item = result_item
        self.vlayout_item_container = QVBoxLayout(self)
        self.vlayout_item_container.setSpacing(6)

        self.vly_img_container = QVBoxLayout()
        self.vly_info_container = QVBoxLayout()

        self.wdt_image = QWidget()
        self.wdt_image.setGeometry(1, 1, 330, 350)
        self.wdt_image.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.wdt_image.setMinimumSize(330, 350)
        style = "color:rgb(255, 255, 255);image:url(" + result_item['image_path'] + ");"
        self.wdt_image.setStyleSheet(style)

        self.btn_delete = QPushButton(self.wdt_image)
        image_geo = self.wdt_image.geometry()
        self.btn_delete.setGeometry(image_geo.width() - 30, 0, 30, 30)
        self.btn_delete.setStyleSheet("image: url(:/newPrefix/cross-icon.png);")
        self.vly_img_container.addWidget(self.wdt_image)

        self.flayout_info_container = QFormLayout()

        self.lbl_similarity_score_label = QLabel()
        self.lbl_similarity_score_label.setText("Similarity Score: ")
        self.lbl_similarity_score = QLabel()

        self.lbl_case_number_label = QLabel()
        self.lbl_case_number_label.setText("Case Number: ")
        self.lbl_case_number = QLabel()

        self.lbl_ps_label = QLabel()
        self.lbl_ps_label.setText("PS: ")
        self.lbl_ps = QLabel()
        self.flayout_info_container.addRow(self.lbl_similarity_score_label, self.lbl_similarity_score)
        self.flayout_info_container.addRow(self.lbl_case_number_label, self.lbl_case_number)
        self.flayout_info_container.addRow(self.lbl_ps_label, self.lbl_ps)
        self.vly_info_container.addLayout(self.flayout_info_container)

        self.vlayout_item_container.addLayout(self.vly_img_container)
        self.vlayout_item_container.addLayout(self.vly_info_container)
        self.init_view()

    @pyqtSlot()
    def on_clicked_delete(self):
        self.delete_item_signal.emit(self.result_item)

    def resizeEvent(self, event):
        image_geo = self.wdt_image.geometry()
        self.btn_delete.setGeometry(image_geo.width() - 30, 0, 30, 30)

    def init_view(self):
        # if self.result_item['image_path']:
            # target_image_pixmap = QPixmap(self.result_item['image_path'])
            # self.wdt_image.setPixmap(target_image_pixmap)
        if self.result_item['confidence']:
            self.lbl_similarity_score.setText(str(self.result_item['confidence']))
        self.btn_delete.clicked.connect(self.on_clicked_delete)
