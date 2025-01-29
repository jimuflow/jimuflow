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

from PySide6.QtCore import Slot, Signal, Qt, QModelIndex, QEvent, QPoint
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QVBoxLayout, QListView, QAbstractItemView

from jimuflow.datatypes import DataTypeRegistry
from jimuflow.definition import VariableDef
from jimuflow.gui.expression_edit_v3 import ExpressionEditV3
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.expression import escape_string

window_element_properties = {
    "class_name": gettext("The class name of the element"),
    "friendly_class_name": gettext("The friendly class name for the control"),
    "texts": gettext("The text for each item of this control"),
    "control_id": gettext("The ID of the element"),
    "rectangle": gettext("The rectangle of the element on the screen"),
    "is_visible": gettext("Whether the element is visible or not"),
    "is_enabled": gettext("Whether the element is enabled or not"),
    "control_count": gettext("The number of children of this control"),
    "selection_indices": gettext("The start and end indices of the current selection text"),
    "column_count": gettext("The number of columns"),
    "item_count": gettext("The number of items in the ListView or TreeView"),
    "columns": gettext("The information on the columns of the ListView"),
    "button_count": gettext("The number of buttons on the ToolBar")
}


class WindowElementPropertyPopup(QWidget):
    item_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(Qt.WindowType.Popup)
        self._list_view = QListView()
        self._list_model = QStandardItemModel()
        self._list_view.setModel(self._list_model)
        self._list_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._list_view.activated.connect(self.on_item_activated)
        self.layout.addWidget(self._list_view)
        self._list_view.installEventFilter(self)
        self._populate_model()

    def _populate_model(self):
        for key, value in window_element_properties.items():
            item = QStandardItem(f'{key} - {value}')
            item.setData(key, Qt.ItemDataRole.UserRole)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self._list_model.appendRow([item])

    @Slot(QModelIndex)
    def on_item_activated(self, index: QModelIndex):
        self.hide()
        self.item_selected.emit(index.data(Qt.ItemDataRole.UserRole))

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


class WindowElementPropertyEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._expression_editor = ExpressionEditV3()
        button = QPushButton(gettext("Choose"))
        self._button = button
        popup = WindowElementPropertyPopup(button)
        popup.item_selected.connect(self._on_popup_item_selected)
        popup.setVisible(False)
        self._popup = popup
        button.clicked.connect(self._open_popup)
        self._layout.addWidget(self._expression_editor, 0, 0)
        self._layout.addWidget(button, 0, 1)

    def _on_popup_item_selected(self, name):
        self.set_value(escape_string(name))

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
        pos = self._button.mapToGlobal(QPoint(0, self._button.height() - 2))
        self._popup.move(pos)
        self._popup.show()
