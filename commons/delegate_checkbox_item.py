import ast

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QEvent, QSize
from PyQt5.QtGui import QPalette, QIcon
from PyQt5.QtWidgets import QStyledItemDelegate, QCheckBox, QStyle, QApplication, QStyleOptionButton, \
    QStyleOptionViewItem, QItemDelegate, QWidget
from sympy.printing.numpy import const


class DelegateCheckboxItem(QStyledItemDelegate):
    CHECK_ROLE = Qt.UserRole + 1

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.option = QtWidgets.QStyleOptionViewItem()

    def editorEvent(self, event, model, option, index):
        # if not int(index.flags() & QtCore.Qt.ItemIsEditable) > 0:
        #     return False
        #
        # if event.type() == QtCore.QEvent.MouseButtonRelease:
        #     # # Change the checkbox-state
        #     # print(event.button())
        #     # li = logicalIndexAt(event->pos());
        #     # if (li == -1) return;
        #     # states[li] = !states[li];
        #     # Q_EMIT
        #     # checked(li, states[li]);
        #     # columnDown = -1;
        #     # updateSection(li);
        #
        #     self.setModelData(None, model, index)
        #     return True
        #
        # return False
        if event.type() == QEvent.MouseButtonRelease:
            options = QtWidgets.QStyleOptionViewItem(option)
            print("options checkstate", options.checkState)
            value = index.data(self.CHECK_ROLE)
            print("value:", value)
            # editor = self.createEditor(None, option, index)
            # self.setEditorData(editor, index)
            # self.setModelData(editor, model, index)
            checkbox = QStyleOptionButton()
            checkbox.rect = option.rect
            checkbox.text = index.data()
            checkbox.state = QtWidgets.QStyle.State_On | QtWidgets.QStyle.State_Enabled
            model.setData(index, checkbox.text, Qt.EditRole)
            model.setData(index, checkbox.state, Qt.CheckStateRole)
        return True

    def createEditor(self, parent, option, index):
        print("create editor")
        editor = QStyleOptionButton()
        return editor

    def setEditorData(self, editor, index):
        print("set editor")
        editor.text = index.model().data(index, Qt.EditRole)
        editor.state |= QStyle.State_Off
        # color = index.model().data(index, Qt.BackgroundColorRole)
        # palette = QPalette()
        # palette.setBrush(QPalette.Base, color)
        # editor.setPalette(palette)
        # editor.repaint()

    def setModelData(self, editor, model, index):
        '''
        The user wanted to change the old state in the opposite.
        '''
        print("set model data", editor)
        if index.column() == 0:

            print("model:", model.data(index, QtCore.Qt.DisplayRole))
            print("checkable:", index.model().data(index, QtCore.Qt.CheckStateRole))
            print("editor" , editor.text)
            print("editor state", editor.state)
            checkbox = QStyleOptionButton()
            checkbox.text = index.data()
            checkbox.state |= QStyle.State_Off
            # if index.model().data(index, QtCore.Qt.DisplayRole) == 'True':
            #     checkbox.state |= QStyle.State_Off
            # else:
            #     checkbox.state |= QStyle.State_On
            che = model.itemData(index)

            print("findchild:", che[1])
            che[1] = checkbox
            # model.setItemData(index, che)
            # model.setData(index, checkbox, Qt.EditRole)
            # model.setData(index, checkbox.state, Qt.CheckStateRole)
            model.setData(index, checkbox, QtCore.Qt.DisplayRole)

    def drawDisplay(self, painter, option, rect, text):
        super().drawDisplay(painter, option, rect, "")

    def paint(self, painter, option, index):
        self.option = option
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        if options.widget:
            style = option.widget.style()
        else:
            style = QtWidgets.QApplication.style()
        if index.column() == 0:
            checkbox = QStyleOptionButton()
            checkbox.rect = option.rect
            checkbox.text = index.data()
            if options.checkState == QtCore.Qt.Checked:
                checkbox.state = (
                        QtWidgets.QStyle.State_On | QtWidgets.QStyle.State_Enabled
                )
                options.state = QtWidgets.QStyle.State_Off | QtWidgets.QStyle.State_Enabled
            else:
                checkbox.state = (
                        QtWidgets.QStyle.State_Off | QtWidgets.QStyle.State_Enabled
                )
                options.state = QtWidgets.QStyle.State_On | QtWidgets.QStyle.State_Enabled

            # checkbox.state |= QStyle.State_On
            QApplication.style().drawControl(QStyle.CE_CheckBox, checkbox, painter, option.widget)

        else:
            if index.data(QtCore.Qt.DisplayRole):
                rect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, options)
                painter.drawText(
                    rect,
                    QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
                    options.fontMetrics.elidedText(
                        options.text, QtCore.Qt.ElideRight, rect.width()
                    ),
                )

    # def my_paint(self, painter, option, index):
