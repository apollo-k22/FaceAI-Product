import os.path
import pathlib

import PIL.Image
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QMessageBox
import numpy as np


class Common:
    DATABASE_PATH = "FaceAI Media"
    REPORTS_PATH = "FaceAI Probe Reports"
    MATCH_LEVEL = 0.7
    CASE_NUMBER_LENGTH = 14
    CASE_PS_LENGTH = 31
    CASE_EXAMINER_NAME_LENGTH = 63
    CASE_EXAMINER_NO_LENGTH = 20
    CASE_REMARKS_LENGTH = 139
    CREATE_CASE_REGX = "\w"
    EXTENSIONS = ['.png', '.jpe?g', '.jpg', '.bmp', '.tif', '.gif', '.jpeg', '.bmp', '.gif', '.ico']
    IMAGE_FILTER = "Image Files (*.bmp *.cur *.gif *.icns *.ico *.jpeg" \
                   " *.jpg *.pbm *.pgm *.png *.ppm *.svg *.svgz *.tga" \
                   " *.tif *.tiff *.wbmp" \
                   " *.webp *.xbm *.xpm)"
    MEDIA_PATH = "FaceAI Media"
    LABEL_MAX_HEIGHT_IN_ITEM = 30
    LABEL_MAX_WIDTH_IN_ITEM = 170
    VALUE_MAX_HEIGHT_IN_ITEM = 30
    VALUE_MAX_WIDTH_IN_ITEM = 230
    CROSS_BUTTON_SIZE = 30
    PAGINATION_BUTTON_SIZE = 60
    NUMBER_PER_PAGE = 5

    @staticmethod
    def clear_layout(layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                Common.clear_layout(child)

    @staticmethod
    def create_path(path_name):
        path = pathlib.Path(path_name)
        print(path.mkdir(parents=True, exist_ok=True))

    @staticmethod
    def copy_file(from_path, to_directory):
        Common.create_path(to_directory)
        to_path = to_directory + "/" + Common.get_file_name_from_path(from_path)
        if not QFile.exists(to_path):
            QFile.copy(from_path, to_path)
        return to_path

    @staticmethod
    def get_file_name_from_path(url):
        pa = pathlib.Path(url)
        return pa.name

    @staticmethod
    def remove_elements_from_list_tail(removing_list, start_index):
        ret_list = []
        list_len = len(removing_list)
        if start_index < list_len:
            for index in range(start_index):
                print(str(index))
                ret_list.append(removing_list[index])
                print(removing_list[index])
        else:
            ret_list = removing_list
        return ret_list

    @staticmethod
    def resize_image(img_path):
        img = PIL.Image.open(img_path)
        if os.path.getsize(img_path)/(1000 * 1000) > 6:
            wid = img.width
            he = img.height
            img.resize((wid, he), PIL.Image.ADAPTIVE)
            img.save(img_path)
        return img_path

    @staticmethod
    def is_empty(case_info):
        if case_info.case_number:
            return False
        return True

    @staticmethod
    def show_message(icon, text, information_text, title, detailed_text):
        msg = QMessageBox()
        msg.setStyleSheet("background-color:lightblue")
        msg.setIcon(icon)
        msg.setText(text)
        msg.setInformativeText(information_text)
        msg.setWindowTitle(title)
        msg.setDetailedText(detailed_text)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.exec_()

    # this method make one integer with the number of integers,
    # each digit is between start and end
    @staticmethod
    def generate_digits(start, end, number):
        arr = np.random.uniform(start, end, number)
        arr = np.round(arr).astype(int)
        return "".join(str(x) for x in arr)

    @staticmethod
    def generate_probe_id():
        probe_id = str(Common.generate_digits(0, 9, 9))
        while Common.verify_probe_id(probe_id):
            return probe_id
        else:
            Common.generate_probe_id()

    # verify generated probe_id whether is already exist on database
    # if exist, return false
    @staticmethod
    def verify_probe_id(probe_id):
        return True

    @staticmethod
    def get_folder_path(absolute_file_path):
        return os.path.dirname(os.path.abspath(absolute_file_path))