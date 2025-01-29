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

from PySide6.QtCore import Qt, Slot, Signal, QModelIndex, QEvent
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView

from jimuflow.datatypes import DataTypeRegistry
from jimuflow.definition import VariableDef


class ExpressionEditPopup(QWidget):
    item_selected = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(Qt.WindowType.Popup)
        self._list_view = QTreeView()
        self._list_view.setHeaderHidden(True)
        self._list_view.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        self._list_view.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self._list_view.activated.connect(self.on_item_activated)
        self._list_model = QStandardItemModel()
        self._list_view.setModel(self._list_model)
        self.layout.addWidget(self._list_view)
        self._list_view.installEventFilter(self)

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._list_model.clear()
        # 变量名、变量类型、变量说明
        for var_def in variables:
            name_item = QStandardItem(var_def.name)
            name_item.setData([var_def.name], Qt.ItemDataRole.UserRole)
            name_item.setData(var_def.name, Qt.ItemDataRole.ToolTipRole)
            name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            type_def = type_registry.get_data_type(var_def.type)
            type_item = QStandardItem(type_def.display_name)
            type_item.setData(type_def.display_name, Qt.ItemDataRole.ToolTipRole)
            type_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            if var_def.ui_config.placeholder:
                desc_item = QStandardItem(var_def.ui_config.placeholder)
                desc_item.setData(var_def.ui_config.placeholder, Qt.ItemDataRole.ToolTipRole)
            else:
                desc_item = QStandardItem('')
            desc_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self._list_model.appendRow([name_item, type_item, desc_item])
            for property in type_def.properties:
                child_name_item = QStandardItem(property.name)
                child_name_item.setData([var_def.name, '.', property.name], Qt.ItemDataRole.UserRole)
                child_name_item.setData(property.name, Qt.ItemDataRole.ToolTipRole)
                child_name_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                child_type_def = type_registry.get_data_type(property.data_type)
                child_type_item = QStandardItem(child_type_def.display_name)
                child_type_item.setData(child_type_def.display_name, Qt.ItemDataRole.ToolTipRole)
                child_type_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                child_desc_item = QStandardItem(property.description)
                child_desc_item.setData(property.description, Qt.ItemDataRole.ToolTipRole)
                child_desc_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                name_item.appendRow([child_name_item, child_type_item, child_desc_item])
        self._resize_columns()

    def _resize_columns(self):
        width = self.contentsRect().width()-20
        min_column1_width = 120
        column2_width = 70
        min_column3_width = 200
        if width > 0:
            min_width = min_column1_width + column2_width + min_column3_width
            if width < min_width:
                column1_width = width * min_column1_width / min_width
                column2_width = width * column2_width / min_width
                column3_width = width * min_column3_width / min_width
            else:
                column1_width = (width - column2_width) * min_column1_width / (min_column1_width + min_column3_width)
                column3_width = (width - column2_width) * min_column3_width / (min_column1_width + min_column3_width)
        else:
            column1_width = min_column1_width
            column3_width = min_column3_width
        self._list_view.setColumnWidth(0, column1_width)
        self._list_view.setColumnWidth(1, column2_width)
        self._list_view.setColumnWidth(2, column3_width)

    @Slot(QModelIndex)
    def on_item_activated(self, index: QModelIndex):
        self.hide()
        if index.column() != 0:
            index = self._list_model.index(index.row(), 0, index.parent())
        tokens = index.data(Qt.ItemDataRole.UserRole)
        self.item_selected.emit(tokens)

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_columns()
