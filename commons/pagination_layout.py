from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel, QWidget, QLayout, QSpacerItem, QSizePolicy, QLineEdit

from commons.common import Common
from commons.pagination_button import PaginationButton


class PaginationLayout(QHBoxLayout):
    previous_page_signal = pyqtSignal()
    next_page_signal = pyqtSignal()
    # emitted whenever changed page
    changed_page_signal = pyqtSignal(int)
    go_to_page_signal = pyqtSignal(int)

    def __init__(self, totals, num_per_page, current_page):
        QHBoxLayout.__init__(self)
        self.totals = totals
        self.num_per_pages = num_per_page
        self.current_page = current_page
        self.page_count = self.totals // self.num_per_pages
        if self.totals % self.num_per_pages:
            self.page_count += 1

        self.hlyPaginationButtons = QHBoxLayout()

        self.hlyGo2Page = QHBoxLayout()

        self.init_views()

    def init_views(self):
        self.init_pagination_buttons()
        self.init_go_to_page_layout()
        self.addLayout(self.hlyPaginationButtons)
        hspacer = QSpacerItem(50, 10, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addSpacerItem(hspacer)
        self.addLayout(self.hlyGo2Page)

    def init_pagination_buttons(self):
        # clear pagination layout
        Common.clear_layout(self)

        # add pagination buttons
        btnPrevious = QPushButton()
        btnPrevious.setMaximumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        btnPrevious.setMinimumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        btnPrevious.setStyleSheet("background-image: url(:/newPrefix/icon-back2.png); "
                                  "background-size: cover;"
                                  "border: 1px solid #7F00E2;"
                                  "border-radius: 10px;"
                                  "background-repeat: no-repeat;"
                                  "background-color: rgb(127, 0, 226);")
        btnPrevious.clicked.connect(self.previous_page_slot)

        btnNext = QPushButton()
        btnNext.setMinimumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        btnNext.setMaximumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        btnNext.setStyleSheet("background-image: url(:/newPrefix/icon-next2.png); "
                              "background-size: cover;"
                              "border: 1px solid #7F00E2;"
                              "border-radius: 10px;"
                              "background-repeat: no-repeat;"
                              "background-color: rgb(127, 0, 226);")
        btnNext.clicked.connect(self.next_page_slot)

        if not self.page_count == 0:
            # add previous button
            self.hlyPaginationButtons.addWidget(btnPrevious)
            if self.page_count > 5:
                # add page buttons
                if self.page_count - self.current_page > 5:
                    start_index = 0
                    if self.current_page > 0:
                        start_index = self.current_page - 1
                    for index in range(start_index, start_index + 3):
                        button = self.create_pagination_button(index)
                        # set current page button to inactive
                        if index == self.current_page:
                            button.setEnabled(False)
                        self.hlyPaginationButtons.addWidget(button)

                    omitting_label = QLabel("...")
                    omitting_label.setMinimumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
                    omitting_label.setMaximumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
                    omitting_label.setStyleSheet("color: rgb(255, 255, 255);"
                                                 "background-color: rgb(0, 0, 0);"
                                                 "padding-bottom:5px;")
                    omitting_label.setAlignment(Qt.AlignVCenter)
                    self.hlyPaginationButtons.addWidget(omitting_label)
                    for index in range(self.page_count - 2, self.page_count):
                        button = self.create_pagination_button(index)
                        self.hlyPaginationButtons.addWidget(button)

                else:
                    for index in range(self.page_count - 6, self.page_count):
                        button = self.create_pagination_button(index)
                        # set current page button to inactive
                        if index == self.current_page:
                            button.setEnabled(False)
                        self.hlyPaginationButtons.addWidget(button)
            else:
                for index in range(self.page_count):
                    button = self.create_pagination_button(index)
                    # set current page button to inactive
                    if index == self.current_page:
                        button.setEnabled(False)
                    self.hlyPaginationButtons.addWidget(button)
            # add next button
            self.hlyPaginationButtons.addWidget(btnNext)
            # add spacer
            hspacer = QSpacerItem(50, 10, QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.hlyPaginationButtons.addSpacerItem(hspacer)

    def init_go_to_page_layout(self):

        lbl_go_label = QLabel("Go To")
        lbl_page_label = QLabel("Page")
        lbl_page_number = QLineEdit()
        lbl_page_number.setObjectName("leditGoPageNumber")
        btn_go = QPushButton("Go")
        btn_go.clicked.connect(self.clicked_go_button)
        lbl_go_label.setStyleSheet("background: transparent;color: rgb(255, 255, 255);")
        lbl_go_label.setMinimumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        lbl_go_label.setMaximumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)

        lbl_page_label.setStyleSheet("background: transparent;color: rgb(255, 255, 255);")
        lbl_page_label.setMinimumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        lbl_page_label.setMaximumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)

        lbl_page_number.setStyleSheet("border: 1px solid rgb(53, 132, 228);border-radius: 10px;background: transparent")
        lbl_page_number.setMinimumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        lbl_page_number.setMaximumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        hspacer = QSpacerItem(50, 10, QSizePolicy.Fixed, QSizePolicy.Fixed)

        btn_go.setStyleSheet("border-radius: 10px;background: transparent"
                             "color: rgb(255, 255, 255);border: 1px solid white;")
        btn_go.setMinimumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        btn_go.setMaximumSize(Common.PAGINATION_BUTTON_SIZE, Common.PAGINATION_BUTTON_SIZE)
        self.hlyGo2Page.addWidget(lbl_go_label)
        self.hlyGo2Page.addWidget(lbl_page_number)
        self.hlyGo2Page.addWidget(lbl_page_label)
        self.hlyGo2Page.addSpacerItem(hspacer)
        self.hlyGo2Page.addWidget(btn_go)

    @pyqtSlot()
    def previous_page_slot(self):
        if self.current_page >= 1:
            self.current_page -= 1
        print("previous clicked: current page is ", self.current_page)
        self.init_views()
        self.changed_page_signal.emit(self.current_page)

    @pyqtSlot()
    def next_page_slot(self):
        if self.current_page < self.page_count - 1:
            self.current_page += 1
        print("next clicked : current page is ", self.current_page)
        self.init_views()
        self.changed_page_signal.emit(self.current_page)

    @pyqtSlot(int)
    def clicked_slot(self, current_page):
        self.current_page = current_page
        print("clicked button: current page is ", current_page)
        self.changed_page_signal.emit(self.current_page)

    @pyqtSlot()
    def clicked_go_button(self):
        to_be_gone_page = int(self.hlyGo2Page.itemAt(1).widget().text()) - 1
        if to_be_gone_page < 0 or to_be_gone_page > self.page_count - 1:
            return
        self.changed_page_signal.emit(to_be_gone_page)

    def create_pagination_button(self, current):
        button = PaginationButton(current)
        button.button_clicked_signal.connect(
            lambda current_page: self.clicked_slot(current_page))
        return button