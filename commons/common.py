from PyQt5.QtCore import QRegularExpression
from PyQt5.QtWidgets import QMessageBox


class Common:
    CASE_NUMBER_LENGTH = 14
    CASE_PS_LENGTH = 31
    CASE_EXAMINER_NAME_LENGTH = 63
    CASE_EXAMINER_NO_LENGTH = 20
    CASE_REMARKS_LEGNTH = 139
    CREATE_CASE_REGX = "\w"
    EXTENSIONS = {'.png', '.jpe?g', '.bmp', '.tif', '.gif', '.png'}
    IMAGE_FILTER = "All files (*.*);;BMP (*.bmp);;CUR (*.cur);;GIF (*.gif);;ICNS (*.icns);;" \
                   "ICO (*.ico);;JPEG (*.jpeg);;" \
                   "JPG (*.jpg);;PBM (*.pbm);;PGM (*.pgm);;PNG (*.png);;" \
                   "PPM (*.ppm);;SVG (*.svg);;SVGZ (*.svgz);;TGA (*.tga);;" \
                   "TIF (*.tif);;TIFF (*.tiff);;WBMP (*.wbmp);;" \
                   "WEBP (*.webp);;XBM (*.xbm);;XPM (*.xpm)"
    MEDIA_FOLDER = "FaceAI Media"

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                layout.removeItem(item)
                # widget = item.widget()
                # if widget is not None:
                #     widget.setParent(None)
                # else:
                #     self.clear_layout(item.layout())

    def clear_item(self, item):
        if hasattr(item, "layout"):
            if callable(item.layout):
                layout = item.layout()
        else:
            layout = None

        if hasattr(item, "widget"):
            if callable(item.widget):
                widget = item.widget()
        else:
            widget = None

        if widget:
            widget.setParent(None)
        elif layout:
            for i in reversed(range(layout.count())):
                self.clear_item(layout.itemAt(i))

    def box_delete(self, box):
        for i in range(box.count()):
            layout_item = box.itemAt(i)
            box.removeItem(layout_item)
            return

    @staticmethod
    def show_message(icon, text, information_text, title, detailed_text):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setInformativeText(information_text)
        msg.setWindowTitle(title)
        msg.setDetailedText(detailed_text)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.exec_()

    @staticmethod
    def resize_image(url):
        print("")

    @classmethod
    def clear_layout(self, vlyReportResultLayout):
        pass
