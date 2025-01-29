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

# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

import json
import sys
from typing import Any, List, Dict, Union

from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt, QFileInfo, Slot
from PySide6.QtWidgets import QTreeView, QApplication, QHeaderView, QWidget, QHBoxLayout, QPushButton, QVBoxLayout


class InputDefItem:
    """A Json item corresponding to a line in QTreeView"""

    def __init__(self, parent: "InputDefItem" = None):
        self._parent = parent
        self._name = ""
        self._type = ""
        self._object_class = ""
        self._children = []

    def appendChild(self, item: "InputDefItem"):
        """Add item as a child"""
        self._children.append(item)

    def insertChild(self, item: "InputDefItem", row: int):
        """Insert child item before the index"""
        self._children.insert(row, item)

    def removeChild(self, row: int):
        """Remove the child item from the given row"""
        return self._children.pop(row)

    def child(self, row: int) -> "InputDefItem":
        """Return the child of the current item from the given row"""
        return self._children[row]

    def parent(self) -> "InputDefItem":
        """Return the parent of the current item"""
        return self._parent

    def childCount(self) -> int:
        """Return the number of children of the current item"""
        return len(self._children)

    def row(self) -> int:
        """Return the row where the current item occupies in the parent"""
        return self._parent._children.index(self) if self._parent else 0

    @property
    def name(self) -> str:
        """Return the key name"""
        return self._name

    @name.setter
    def name(self, name: str):
        """Set key name of the current item"""
        self._name = name

    @property
    def type(self) -> str:
        """Return the value name of the current item"""
        return self._type

    @type.setter
    def type(self, type: str):
        """Set value name of the current item"""
        self._type = type

    @property
    def object_class(self) -> str:
        """Return the python type of the item's value."""
        return self._object_class

    @object_class.setter
    def object_class(self, object_class: str):
        """Set the python type of the item's value."""
        self._object_class = object_class

    @classmethod
    def load(
            cls, value: Union[List, Dict], parent: "InputDefItem" = None, sort=True
    ) -> "InputDefItem":
        """Create a 'root' InputDefItem from a nested list or a nested dictonary

        Examples:
            with open("file.json") as file:
                data = json.dump(file)
                root = InputDefItem.load(data)

        This method is a recursive function that calls itself.

        Returns:
            InputDefItem: InputDefItem
        """
        rootItem = InputDefItem(parent)

        if isinstance(value, dict):
            rootItem.name = value['name'] if 'name' in value else ''
            rootItem.type = value['type']
            if rootItem.type == 'object':
                rootItem.object_class = value.get('objectClass')
            if rootItem.type == 'list':
                if 'elementDef' in value and isinstance(value['elementDef'], dict):
                    child = cls.load(value['elementDef'], rootItem)
                    child.name = 'element'
                    rootItem.appendChild(child)
            elif rootItem.type == 'struct':
                if 'fields' in value and isinstance(value['fields'], list):
                    for field in value['fields']:
                        child = cls.load(field, rootItem)
                        rootItem.appendChild(child)

        elif isinstance(value, list):
            rootItem.name = 'root'
            for index, value in enumerate(value):
                child = cls.load(value, rootItem)
                rootItem.appendChild(child)

        return rootItem


class InputDefModel(QAbstractItemModel):
    """ An editable model of Json data """

    def __init__(self, parent: QObject = None):
        super().__init__(parent)

        self._rootItem = InputDefItem()
        self._headers = ("name", "type", "Object Class")

    def clear(self):
        """ Clear data from the model """
        self.load([])

    def load(self, input_defs: list):
        """Load model from a nested dictionary returned by json.loads()

        Arguments:
            document (dict): JSON-compatible dictionary
        """

        assert isinstance(
            input_defs, list
        ), "`inputDefs` must be list, " f"not {type(input_defs)}"

        self.beginResetModel()

        self._rootItem = InputDefItem.load(input_defs)

        self.endResetModel()

        return True

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        """Override from QAbstractItemModel

        Return data from a json item according index and role

        """
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return item.name

            if index.column() == 1:
                return item.type

            if index.column() == 2:
                return item.object_class

        elif role == Qt.EditRole:
            if index.column() == 0:
                return item.name

            if index.column() == 1:
                return item.type

            if index.column() == 2:
                return item.object_class

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole):
        """Override from QAbstractItemModel

        Set json item according index and role

        Args:
            index (QModelIndex)
            value (Any)
            role (Qt.ItemDataRole)

        """
        if role == Qt.EditRole:
            if index.column() == 0:
                item = index.internalPointer()
                item.name = str(value)

                self.dataChanged.emit(index, index, [Qt.EditRole])

                return True
            elif index.column() == 1:
                item = index.internalPointer()
                item.type = str(value)

                self.dataChanged.emit(index, index, [Qt.EditRole])

                return True
            elif index.column() == 2:
                item = index.internalPointer()
                item.object_class = str(value)

                self.dataChanged.emit(index, index, [Qt.EditRole])

                return True

        return False

    def headerData(
            self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        """Override from QAbstractItemModel

        For the InputDefModel, it returns only data for columns (orientation = Horizontal)

        """
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self._headers[section]

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        """Override from QAbstractItemModel

        Return index according row, column and parent

        """
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Override from QAbstractItemModel

        Return parent index of index

        """
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self._rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return row count from parent index
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return column number. For the model, it always return 2 columns
        """
        return 3

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super(InputDefModel, self).flags(index)

        return Qt.ItemIsEditable | flags

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()
        for i in range(count):
            item = InputDefItem(parentItem)
            item.name='newone'
            parentItem.insertChild(item, row)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()
        for i in range(count):
            parentItem.removeChild(row)
        self.endRemoveRows()
        return True

    def to_json(self, item=None):

        if item is None:
            item = self._rootItem

        nchild = item.childCount()

        item_def_json = {
            "name": item.name,
            "type": item.type,
        }

        if item.type == 'list':
            item_def_json['elementDef'] = self.to_json(item.child(0)) if nchild > 0 else None
        elif item.type == 'struct' or item is self._rootItem:
            item_def_json['fields'] = []
            for i in range(nchild):
                ch = item.child(i)
                item_def_json['fields'].append(self.to_json(ch))
        elif item.type == 'object':
            item_def_json['objectClass'] = item.object_class

        return item_def_json['fields'] if item is self._rootItem else item_def_json


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super(MyWidget, self).__init__(parent)
        layout = QVBoxLayout(self)
        view = QTreeView()
        self.view = view
        model = InputDefModel()
        self.model = model

        view.setModel(model)

        json_path = QFileInfo(__file__).absoluteDir().filePath("input_defs.json")

        with open(json_path) as file:
            document = json.load(file)
            model.load(document)

        view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        view.setAlternatingRowColors(True)
        layout.addWidget(view)

        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)
        add_button = QPushButton("Add Row")
        remove_button = QPushButton("Remove Row")
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(remove_button)
        add_button.clicked.connect(self.add_row)
        remove_button.clicked.connect(self.remove_row)

    @Slot()
    def add_row(self):
        indexes = self.view.selectionModel().selectedIndexes()
        if len(indexes) > 0:
            self.model.insertRows(indexes[0].row(), 1, indexes[0].parent())
        else:
            self.model.insertRows(self.model.rowCount(QModelIndex()), 1, QModelIndex())

    @Slot()
    def remove_row(self):
        indexes = self.view.selectionModel().selectedIndexes()
        if len(indexes) > 0:
            self.model.removeRows(indexes[0].row(), 1, indexes[0].parent())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    widget.resize(500, 300)
    app.exec()
