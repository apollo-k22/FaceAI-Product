import ast

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QStyledItemDelegate, QCheckBox, QStyle, QApplication, QStyleOptionButton, \
    QStyleOptionViewItem, QItemDelegate
from sympy.printing.numpy import const


class DelegateCheckboxItem(QStyledItemDelegate):
    CHECK_ROLE = Qt.UserRole + 1

    def __init__(self):
        super().__init__()

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
            value = index.data(self.CHECK_ROLE)
            print(event.button())
            model.setData(index, False, self.CHECK_ROLE)

            return True

        return QStyledItemDelegate.editorEvent(self, event, model, option, index)

    def paint(self, painter, option, index):
        if index.column() == 1:

            checkbox = QStyleOptionButton()
            checkbox.rect = option.rect

            checkbox.text = index.data()
            checkbox.state |= QStyle.State_On
            print(index.data())
            print("row:", index.row())
            print("column", index.column())

        QApplication.style().drawControl(QStyle.CE_CheckBox, checkbox, painter, option.widget)
        # self.drawCheck(self, painter, option, )
    # is_checked = ast.literal_eval(index.data(DelegateCheckboxItem.CHECK_ROLE))
    # if is_checked:
    #     checkbox.state |= QStyle.State_On
    # else:
    #     checkbox.state |= QStyle.State_Off
    # if index.column() == 1:
    #
    #     progress = index.data().toInt()
    #
    #     progressBarOption = QStyleOptionProgressBar()
    #     progressBarOption.rect = option.rect
    #     progressBarOption.minimum = 0
    #     progressBarOption.maximum = 100
    #     progressBarOption.progress = progress
    #     progressBarOption.text = QString::number(progress) + "%"
    #     progressBarOption.textVisible = True
    #
    #     QApplication.style().drawControl(QStyle.CE_CheckBox, progressBarOption, painter)
    # else:
    #     QStyledItemDelegate.paint(self, painter, option, index)


class MyDelegate(QtWidgets.QStyledItemDelegate):
    MARGINS = 10

    def __init__(self, parent=None, *args):
        QtWidgets.QStyledItemDelegate.__init__(self, parent, *args)

    # overrides
    def sizeHint(self, option, index):
        '''
        Description:
            Since labels are stacked we will take whichever is the widest
        '''
        options = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(options, index)

        # draw rich text
        doc = QtGui.QTextDocument()
        doc.setHtml(index.data(QtCore.Qt.DisplayRole))
        doc.setDocumentMargin(self.MARGINS)
        doc.setDefaultFont(options.font)
        doc.setTextWidth(option.rect.width())
        return QtCore.QSize(doc.idealWidth(), doc.size().height())

    # methods
    def paint(self, painter, option, index):
        painter.save()
        painter.setClipping(True)
        painter.setClipRect(option.rect)

        opts = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(opts, index)

        style = QtGui.QApplication.style() if opts.widget is None else opts.widget.style()

        # Draw background
        if option.state & QtWidgets.QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight().color())
        else:
            painter.fillRect(option.rect, QtGui.QBrush(QtCore.Qt.NoBrush))

        # Draw checkbox
        if (index.flags() & QtCore.Qt.ItemIsUserCheckable):
            cbStyleOption = QtWidgets.QStyleOptionButton()

            if index.data(QtCore.Qt.CheckStateRole):
                cbStyleOption.state |= QtWidgets.QStyle.State_On
            else:
                cbStyleOption.state |= QtWidgets.QStyle.State_Off

            cbStyleOption.state |= QtWidgets.QStyle.State_Enabled
            cbStyleOption.rect = option.rect.translated(self.MARGINS, 0)
            style.drawControl(QtWidgets.QStyle.CE_CheckBox, cbStyleOption, painter, option.widget)

        # Draw Title
        doc = QtGui.QTextDocument()
        doc.setHtml(index.data(QtCore.Qt.DisplayRole))
        doc.setTextWidth(option.rect.width())
        doc.setDocumentMargin(self.MARGINS)
        doc.setDefaultFont(opts.font)

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        # highlight text
        if option.state & QtWidgets.QStyle.State_Selected:
            ctx.palette.setColor(option.palette.Text,
                                 option.palette.color(option.palette.Active, option.palette.HighlightedText))
        else:
            ctx.palette.setColor(option.palette.Text, option.palette.color(option.palette.Active, option.palette.Text))

        textRect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, option)
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        # end
        painter.restore()

