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

from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, Signal, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QTableView, \
    QStyledItemDelegate, QPushButton, QHBoxLayout, QSizePolicy, QAbstractItemView, QHeaderView

from jimuflow.locales.i18n import gettext

xpath_operator = {
    "=": gettext("equal to"),
    "!=": gettext("Not equal to"),
    "contains": gettext("contains"),
    "not_contains": gettext("not contains"),
    "starts_with": gettext("starts with"),
    "not_starts_with": gettext("not starts with"),
    "ends_with": gettext("ends with"),
    "not_ends_with": gettext("not ends with"),
    ">": gettext("greater than"),
    ">=": gettext("greater than or equal to"),
    "<": gettext("less than"),
    "<=": gettext("less than or equal to"),
    "matches": gettext("regular expression matches")
}


class WebElementAttributesModel(QAbstractItemModel):
    def __init__(self, attributes: list, parent=None):
        super().__init__(parent)
        self._headers = [gettext('Attribute'), gettext('Operator'), gettext('Value'), ' ']
        self._attributes = attributes

    def set_attributes(self, attributes: list):
        self.beginResetModel()
        self._attributes = attributes
        self.endResetModel()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        attribute = self._attributes[row]
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return attribute[0]
            elif column == 1:
                op = next((key, value) for key, value in xpath_operator.items() if key == attribute[1])
                return op[1]
            elif column == 2:
                return attribute[2]
        elif role == Qt.ItemDataRole.EditRole:
            if column == 0:
                return attribute[0]
            elif column == 1:
                op = next((key, value) for key, value in xpath_operator.items() if key == attribute[1])
                return op[0]
            elif column == 2:
                return attribute[2]
        elif role == Qt.ItemDataRole.CheckStateRole:
            if column == 0:
                return Qt.CheckState.Checked if attribute[3] else Qt.CheckState.Unchecked

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        row = index.row()
        attribute = self._attributes[row]
        column = index.column()
        if role == Qt.ItemDataRole.EditRole:
            if column == 0:
                attribute[0] = value
            elif column == 1:
                attribute[1] = value
            elif column == 2:
                attribute[2] = value
            else:
                return False
        elif role == Qt.ItemDataRole.CheckStateRole:
            if column == 0:
                attribute[3] = value == Qt.CheckState.Checked.value
            else:
                return False
        else:
            return False
        self.dataChanged.emit(index, index, [role])
        return True

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self._attributes)

    def columnCount(self, parent=QModelIndex()):
        return 4

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        return self.createIndex(row, column, self._attributes[row])

    def parent(self, index: QModelIndex):
        return QModelIndex()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() == 0:
            flags |= Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsUserCheckable
        elif index.column() == 1 or index.column() == 2:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def insertRows(self, row, count, parent=QModelIndex()):
        if parent.isValid():
            return False
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            self._attributes.insert(row + i, ['', '=', '', False])
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        if parent.isValid():
            return False
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            self._attributes.pop(row)
        self.endRemoveRows()
        return True

    def index_for_attribute(self, attribute: list):
        row = self._attributes.index(attribute)
        return self.createIndex(row, 0, attribute)


class ComboBoxDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setAutoFillBackground(True)
        for key, value in xpath_operator.items():
            editor.addItem(value, key)
        return editor

    def setEditorData(self, editor: QComboBox, index):
        value = index.data(Qt.ItemDataRole.EditRole)
        editor.setCurrentIndex(editor.findData(value, Qt.ItemDataRole.UserRole))

    def setModelData(self, editor: QComboBox, model, index):
        model.setData(index, editor.currentData(), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class WebElementAttributesTable(QWidget):
    attributes_edited = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._list_remove_icon = QIcon.fromTheme(QIcon.ThemeIcon.ListRemove)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        table_view = QTableView()
        model = WebElementAttributesModel([], self)
        model.dataChanged.connect(self._on_data_changed)
        model.rowsRemoved.connect(self._on_rows_removed)
        table_view.setModel(model)
        table_view.verticalHeader().hide()
        table_view.horizontalHeader().resizeSection(0, 120)
        table_view.horizontalHeader().resizeSection(1, 100)
        # table_view.horizontalHeader().resizeSection(2, 200)
        table_view.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table_view.horizontalHeader().resizeSection(3, 60)
        table_view.setItemDelegateForColumn(1, ComboBoxDelegate())
        table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table_view.setEditTriggers(QAbstractItemView.EditTrigger.CurrentChanged
                                   | QAbstractItemView.EditTrigger.SelectedClicked
                                   | QAbstractItemView.EditTrigger.DoubleClicked)
        main_layout.addWidget(table_view)
        add_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd), "")
        add_button.setDisabled(True)
        add_button.clicked.connect(self.add_attribute)
        main_layout.addWidget(add_button)
        self._model = model
        self._table_view = table_view
        self._add_button = add_button

    def set_attributes(self, attributes: list):
        self._model.set_attributes(attributes)
        for row in range(len(attributes)):
            self._table_view.setIndexWidget(self._model.index(row, 3), self._create_actions_widget(attributes[row]))
        self._add_button.setDisabled(False)

    def _create_actions_widget(self, attribute):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        button = QPushButton(self._list_remove_icon, "")
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button.setFlat(True)
        button.clicked.connect(lambda: self._remove_attribute(attribute))
        layout.addWidget(button)
        return widget

    def _remove_attribute(self, attribute):
        index = self._model.index_for_attribute(attribute)
        self._model.removeRow(index.row())

    @Slot(QModelIndex, QModelIndex, list)
    def _on_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list):
        self.attributes_edited.emit()

    @Slot(QModelIndex, int, int)
    def _on_rows_removed(self, parent: QModelIndex, first: int, last: int):
        self.attributes_edited.emit()

    @Slot()
    def add_attribute(self):
        row = self._model.rowCount()
        self._model.insertRow(row)
        index = self._model.index(row, 0)
        attribute = index.internalPointer()
        self._table_view.setIndexWidget(self._model.index(row, 3), self._create_actions_widget(attribute))


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    table = WebElementAttributesTable()
    table.show()
    app.exec()
