# This software is dual-licensed under the GNU General Public License (GPL) 
# and a commercial license.
#
# You may use this software under the terms of the GNU GPL v3 (or, at your option,
# any later version) as published by the Free Software Foundation. See 
# <https://www.gnu.org/licenses/> for details.
#
# If you require a proprietary/commercial license for this software, please 
# contact us at jimuflow@gmail.com for more information.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Copyright (C) 2024-2025  Weng Jing

from PySide6.QtCore import QEvent, Qt, Slot, QSize
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QFrame, QCompleter, QSizePolicy, QPushButton


class MyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.textEdited.connect(self.on_text_edit)

    def sizeHint(self):
        size = QSize(max(100, self.fontMetrics().horizontalAdvance(self.text()) + 20), self.fontMetrics().height())
        return size

    @Slot(str)
    def on_text_edit(self, text):
        self.updateGeometry()


class ExpressionEditPopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("item 1"))
        self.layout.addWidget(QLabel("item 2"))
        self.setWindowFlag(Qt.WindowType.Popup)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def focusOutEvent(self, event):
        print('focusOutEvent')
        event.ignore()


class ExpressionEdit(QFrame):
    def __init__(self):
        super().__init__()
        # 自定义一种水平布局，保证当前焦点元素位于可见区域
        self.item_widgets = []
        self.scroll_x = 0
        self.current_item_index = 0
        self.var_label = QPushButton("变量1", self)
        self.var_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.var_label.installEventFilter(self)
        self.op_label = QPushButton("+", self)
        self.op_label.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.op_label.installEventFilter(self)
        self.input = MyLineEdit(self)
        self.input.textEdited.connect(self.on_input_edited)
        self.input.cursorPositionChanged.connect(self.on_cursorPositionChanged)
        self.completer = QCompleter(self.create_completer_model(), self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.activated.connect(self.input.setText)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.input.installEventFilter(self)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.completer.setWidget(self)
        # self.setFocusProxy(self.input)
        # self.completer.popup().setFocusProxy(self.input)
        self.item_widgets.append(self.var_label)
        self.item_widgets.append(self.op_label)
        self.item_widgets.append(self.input)
        self.popup = ExpressionEditPopup(self)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def create_completer_model(self):
        model = QStandardItemModel(0, 2, self)
        model.appendRow([QStandardItem("+"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("-"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("*"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("/"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("abc"), QStandardItem("变量")])
        model.appendRow([QStandardItem("efg"), QStandardItem("变量")])
        return model

    def event(self, e):
        if e.type() == QEvent.Type.LayoutRequest:
            self.layout_items()
            e.accept()
            return True
        return super(ExpressionEdit, self).event(e)

    def sizeHint(self):
        size = QSize(0, 0)
        for item in self.item_widgets:
            child_size = item.sizeHint()
            size.setWidth(size.width() + child_size.width())
            size.setHeight(max(size.height(), child_size.height()))
        print("sizeHint", size)
        return size

    def minimumSizeHint(self):
        return QSize(100, 20)

    def cursor_offset(self):
        pass

    def layout_items(self):
        cursor_pos = self.cursor_pos()
        if cursor_pos < self.scroll_x:
            self.scroll_x = cursor_pos
        elif cursor_pos > self.scroll_x + self.size().width():
            self.scroll_x = cursor_pos - self.size().width() + 1
        x = -self.scroll_x
        for i in range(len(self.item_widgets)):
            item = self.item_widgets[i]
            child_size = item.sizeHint()
            item.setGeometry(x, 0, child_size.width(), child_size.height())
            if x + child_size.width() > self.size().width():
                break
            x += child_size.width()
        self.update()

    def resizeEvent(self, event):
        print("resizeEvent", event.size(), self.size())
        self.layout_items()

    @Slot(int, int)
    def on_cursorPositionChanged(self, oldPos, newpos):
        print('cursorPositionChanged', oldPos, newpos, self.input.cursorRect())
        self.layout_items()

    def keyPressEvent(self, event):
        print('keyPressEvent', event)
        self.input.event(event)
        print('input size hint', self.input.sizeHint())

    @Slot(str)
    def on_input_edited(self, text):
        # print(text)
        self.completer.setCompletionPrefix(text)
        self.completer.complete()

    def focusInEvent(self, event):
        print("focusInEvent", event)
        super().focusInEvent(event)
        self.item_widgets[self.current_item_index].setFocus()

    def focusOutEvent(self, event):
        print("focusOutEvent", event)
        super().focusOutEvent(event)

    def cursor_pos(self):
        x = 0
        for i in range(len(self.item_widgets)):
            item = self.item_widgets[i]
            if i == self.current_item_index:
                if isinstance(item, QLineEdit):
                    return x + item.cursorRect().x() + 3
                else:
                    return x
            child_size = item.sizeHint()
            x += child_size.width()
        return x

    def set_current_item_index(self, index):
        if self.current_item_index == index:
            return
        self.current_item_index = index
        for i in range(len(self.item_widgets)):
            item = self.item_widgets[i]
            item.setProperty("selected", i == index)
            item.style().unpolish(item)
            item.style().polish(item)
            if i == index:
                item.setFocus()
        self.layout_items()

    def move_cursor_left(self):
        self.set_current_item_index(max(0, self.current_item_index - 1))

    def move_cursor_right(self):
        self.set_current_item_index(min(len(self.item_widgets) - 1, self.current_item_index + 1))

    def eventFilter(self, watched, event):
        if watched in self.item_widgets and isinstance(watched, QPushButton):
            if event.type() == QEvent.Type.MouseButtonPress:
                self.op_label.setProperty("selected", False)
                self.op_label.style().unpolish(self.op_label)
                self.op_label.style().polish(self.op_label)
                self.var_label.setProperty("selected", True)
                self.var_label.style().unpolish(self.var_label)
                self.var_label.style().polish(self.var_label)
            elif event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Left:
                    self.move_cursor_left()
                    return True
                if event.key() == Qt.Key.Key_Right:
                    self.move_cursor_right()
                    return True
        elif watched is self.input:
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Left and self.input.cursorPosition() == 0:
                    self.move_cursor_left()
                    return True
                if event.key() == Qt.Key.Key_Right and self.input.cursorPosition() == len(self.input.text()):
                    self.move_cursor_right()
                    return True
            if event.type() == QEvent.Type.FocusOut:
                print('input focus out', self.completer.popup().isVisible())
                self.style().unpolish(self)
                self.style().polish(self)
                print('input size hint', self.input.sizeHint())
                return self.completer.popup().isVisible()

        return super().eventFilter(watched, event)


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(ExpressionEdit())
        self.layout.addWidget(QLineEdit())


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    w = MyWidget()
    w.show()
    with open("expression_edit.qss.css", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
    app.exec()
