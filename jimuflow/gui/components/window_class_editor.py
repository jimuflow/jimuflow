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

from PySide6.QtCore import Slot, Signal, Qt, QModelIndex, QEvent, QPoint, QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QListView, QAbstractItemView

from jimuflow.components.core.os_utils import is_windows
from jimuflow.datatypes import DataTypeRegistry
from jimuflow.definition import VariableDef
from jimuflow.gui.expression_edit_v3 import ExpressionEditV3
from jimuflow.gui.window_utils import draw_outline_rect, get_control_rect, close_outline_rect
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.expression import escape_string


class WindowClassPopup(QWidget):
    item_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._windows = []
        self._outline_rect = None
        self.setFixedWidth(200)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(Qt.WindowType.Popup)
        self._list_view = QListView()
        self._list_model = QStandardItemModel()
        self._list_view.setModel(self._list_model)
        self._list_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._list_view.activated.connect(self.on_item_activated)
        self._list_view.selectionModel().currentChanged.connect(self._on_current_change)
        self.layout.addWidget(self._list_view)
        self._list_view.installEventFilter(self)

    def reload_window_classes(self):
        row_count = self._list_model.rowCount()
        if row_count:
            self._list_model.removeRows(0, row_count)
        self._windows.clear()
        if not is_windows():
            return
        import pywinauto
        desktop = pywinauto.Desktop(backend='uia')
        for window in desktop.windows():
            class_name = window.class_name()
            if class_name:
                window_text = window.window_text()
                if window_text:
                    item = QStandardItem(class_name + ' - ' + window_text)
                else:
                    item = QStandardItem(class_name)
                item.setData(class_name, Qt.ItemDataRole.UserRole)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self._list_model.appendRow([item])
                self._windows.append(window)

    @Slot(QModelIndex)
    def on_item_activated(self, index: QModelIndex):
        self.hide()
        self.item_selected.emit(index.data(Qt.ItemDataRole.UserRole))

    def _close_outline_rect(self):
        if self._outline_rect:
            close_outline_rect(self._outline_rect)
            self._outline_rect = None

    @Slot(QModelIndex, QModelIndex)
    def _on_current_change(self, current: QModelIndex, previous: QModelIndex):
        self._close_outline_rect()
        if current.isValid():
            window = self._windows[current.row()]
            if window.is_visible():
                self._outline_rect = draw_outline_rect(get_control_rect(window))
                QTimer.singleShot(2000, self._close_outline_rect)

    def eventFilter(self, watched, event):
        if watched == self._list_view:
            if event.type() == QEvent.Type.KeyPress:
                if ((
                        event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Tab)
                        and self._list_view.currentIndex().isValid()):
                    self.hide()
                    self.on_item_activated(self._list_view.currentIndex())
                    return True
                elif event.key() == Qt.Key.Key_Escape:
                    self.hide()
                    return True
        return False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down:
            # 选择list_view的第一个元素
            self._list_view.setFocus()
            self._list_view.setCurrentIndex(self._list_view.model().index(0, 0))
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
        else:
            event.ignore()


class WindowClassEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._expression_editor = ExpressionEditV3()
        button = QPushButton(gettext("Choose"))
        self._button = button
        popup = WindowClassPopup(button)
        popup.item_selected.connect(self._on_popup_item_selected)
        popup.setVisible(False)
        self._popup = popup
        button.clicked.connect(self._open_popup)
        self._layout.addWidget(self._expression_editor, 0, 0)
        self._layout.addWidget(button, 0, 1)

    def _on_popup_item_selected(self, class_name):
        self.set_value(escape_string(class_name))

    def get_value(self):
        return self._expression_editor.get_expression()

    def set_value(self, value: str):
        self._expression_editor.set_expression(value)

    def setPlaceholderText(self, text):
        self._expression_editor.setPlaceholderText(text)

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._expression_editor.set_variables(variables, type_registry)

    @Slot()
    def _open_popup(self):
        self._popup.reload_window_classes()
        pos = self._button.mapToGlobal(QPoint(0, self._button.height() - 2))
        self._popup.move(pos)
        self._popup.show()
