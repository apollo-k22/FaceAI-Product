import decimal
import json
import operator
import os.path
import pathlib
import winreg

import PIL.Image
import cv2
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QMessageBox
import numpy as np


class Common:
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\FaceAI\main.exe"
    STORAGE_PATH = "Data Storage"
    MEDIA_PATH = "Media"
    REPORTS_PATH = "Probe Reports"
    TEMP_PATH = "Temporary Data"
    REG_KEY = "DataFolder"
    EXPORT_PATH = r"C:\\Users\\" + os.getlogin() + r"\\Documents"
    MATCH_LEVEL = 70
    CASE_NUMBER_LENGTH = 14
    CASE_PS_LENGTH = 31
    CASE_EXAMINER_NAME_LENGTH = 63
    CASE_EXAMINER_NO_LENGTH = 20
    CASE_REMARKS_LENGTH = 139
    # CREATE_CASE_REGX = "\w"
    # CREATE_CASE_REGX = "[\u0020-\u007E]"
    CREATE_CASE_REGX = r'[a-zA-Z0-9]+'
    CREATE_CASE_REGX_FOR_REMOVE = r'[^a-zA-Z0-9]+'
    EXTENSIONS = ['.png', '.jpe?g', '.jpg', '.tif', '.jpeg', '.ico']
    IMAGE_FILTER = "Image Files (*.cur *.icns *.ico *.jpeg" \
                   " *.jpg *.pbm *.pgm *.png *.ppm *.svg *.svgz *.tga" \
                   " *.tif *.tiff *.wbmp" \
                   " *.webp *.xbm *.xpm)"
    LABEL_MAX_HEIGHT_IN_ITEM = 30
    LABEL_MAX_WIDTH_IN_ITEM = 170
    VALUE_MAX_HEIGHT_IN_ITEM = 30
    VALUE_MAX_WIDTH_IN_ITEM = 230
    CROSS_BUTTON_SIZE = 30
    PAGINATION_BUTTON_SIZE = 60
    NUMBER_PER_PAGE = 5
    RESULT_ITEM_WIDGET_SIZE = 330

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
        try:
            path = pathlib.Path(path_name)
            path.mkdir(parents=True, exist_ok=True)
        except Exception as ex:
            print(ex)

    @staticmethod
    def copy_file(from_path, to_path):
        Common.create_path(Common.get_folder_path(to_path))
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
                ret_list.append(removing_list[index])
                print(removing_list[index])
        else:
            ret_list = removing_list
        return ret_list

    @staticmethod
    def resize_image(img_path, size):
        try:
            body_img = cv2.imread(img_path)
            if body_img is None:
                print('resize image: wrong path', img_path)
            else:
                img = np.array(body_img)
                rate = 1
                width = img.shape[0]
                height = img.shape[1]
                if width > height:
                    rate = size / width
                else:
                    rate = size / height
                if rate > 1:
                    print("resized:", img_path)
                    dim = (int(img.shape[1] * rate), int(img.shape[0] * rate))
                    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                    cv2.imwrite(img_path, img)
        except IOError as e:
            print("resize image error:", e)
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

    @staticmethod
    def get_reg(name):
        try:
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, Common.REG_PATH, 0,
                                          winreg.KEY_READ)
            value, regtype = winreg.QueryValueEx(registry_key, name)
            value = value.replace("\\", "/")
            winreg.CloseKey(registry_key)
            return value
        except WindowsError as wr:
            print(wr)
            return None

    @staticmethod
    def set_reg(name, value):
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, Common.REG_PATH)
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, Common.REG_PATH, 0,
                                          winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False

    # sort list by attr.
    # if reverse is true, sorted by desc
    # sorting_list: list to be sorted,
    # attr: sort key
    # attr_type: attr type
    @staticmethod
    def sort_list_by_float_attribute(sorting_list, attr, attr_type, reverse):
        ret = []

        if len(sorting_list):
            if attr_type == 'string':
                for item in sorting_list:
                    item[attr] = float(item[attr])
            ret = sorted(sorting_list, key=lambda x: x[attr], reverse=reverse)
            for item in ret:
                item[attr] = str(item[attr]) + "%"
        return ret

    # round the float string up to 2 decimals
    @staticmethod
    def round_float_string(float_string):
        sim = float(float_string) * 100
        decimal_value = decimal.Decimal(sim)
        # rounding the number upto 2 digits after the decimal point
        rounded = decimal_value.quantize(decimal.Decimal('0.00'))
        return str(rounded)

