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

import html
import json
import os
import re
from pathlib import Path
from typing import Any

from PySide6.QtCore import QAbstractItemModel, QObject, QModelIndex, Qt, Signal, QMimeData, Slot
from PySide6.QtGui import QColor, QStandardItemModel, QStandardItem, QIcon

from jimuflow.common.mimetypes import mimetype_component_def_ids, mimetype_process_flow_nodes
from jimuflow.common.uri_utils import build_web_element_uri, build_window_element_uri
from jimuflow.definition import Package, ProcessDef, FlowNode, ComponentDef, VariableDef
from jimuflow.definition.process_def import snapshot_flow_node_tree
from jimuflow.gui.undo_redo_manager import UndoRedoManager
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import ExecutionEngine, Process


class AppContext:
    _app = None
    _engine = None

    @classmethod
    def set_app(cls, app: "App"):
        cls._app = app
        if app is None:
            cls._engine = None
        else:
            cls._engine = app.engine

    @classmethod
    def app(cls) -> "App":
        return cls._app

    @classmethod
    def engine(cls) -> ExecutionEngine:
        return cls._engine


class ProcessModel(QAbstractItemModel):
    component_dropped = Signal(int, QModelIndex, ComponentDef)
    nodes_dropped = Signal(Qt.DropAction, int, QModelIndex, dict)
    variable_added = Signal(VariableDef)
    variable_updated = Signal(int, VariableDef, VariableDef)
    variable_removed = Signal(int, VariableDef)
    dirty_changed = Signal(bool)
    errors_updated = Signal()

    def __init__(self, process_def: ProcessDef, parent: QObject = None):
        super().__init__(parent)
        self._process_def = process_def
        self._headers = ("node",)
        self._last_saved_snapshot = process_def.clone()
        self._dirty = False
        self.errors = []
        self.undo_redo_manager = UndoRedoManager(self)
        self.validate()

    def save(self):
        self.process_def.save_to_file(self.process_def.path)
        self._last_saved_snapshot = self.process_def.clone()
        self.dirty = False

    @property
    def process_def(self) -> ProcessDef:
        return self._process_def

    @property
    def dirty(self):
        return self._dirty

    @dirty.setter
    def dirty(self, dirty: bool):
        self.validate()
        if self._dirty == dirty:
            return
        self._dirty = dirty
        self.dirty_changed.emit(dirty)

    def update_dirty(self):
        self.dirty = self.process_def != self._last_saved_snapshot

    def validate(self):
        self.errors = Process.validate_flow(AppContext.engine(), self._process_def, self._process_def.flow, 0)[0]
        self.errors_updated.emit()
        self.dataChanged.emit(self.index(0, 0, QModelIndex()),
                              self.index(len(self._process_def.flow) - 1, 0, QModelIndex()), )

    def clear(self):
        """ Clear data from the model """
        self.beginResetModel()
        self._process_def.flow.clear()
        self.update_dirty()
        self.endResetModel()

    def node_index(self, node: FlowNode):
        if node.parent:
            parent = self.node_index(node.parent)
            return self.index(node.parent.flow.index(node), 0, parent)
        else:
            return self.index(node.process_def.flow.index(node), 0, QModelIndex())

    def add_variable(self, var_def: VariableDef):
        self._process_def.variables.append(var_def)
        self.variable_added.emit(var_def)
        self.update_dirty()

    def update_variable(self, new_var_def: VariableDef, old_var_def: VariableDef):
        index = self._process_def.variables.index(old_var_def)
        self._process_def.variables.pop(index)
        self._process_def.variables.insert(index, new_var_def)
        self.variable_updated.emit(index, new_var_def, old_var_def)
        self.update_dirty()

    def remove_variable(self, var_def: VariableDef):
        index = self._process_def.variables.index(var_def)
        self._process_def.variables.pop(index)
        self.variable_removed.emit(index, var_def)
        self.update_dirty()

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> Any:
        """Override from QAbstractItemModel

        Return data from a json item according index and role

        """
        if not index.isValid():
            return None

        item: FlowNode = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                if not item.component:
                    return ''
                tpl = """
                        <style>
                        .name{{
                            font-weight: bold;
                            color: $$NAME_COLOR$$;
                        }}
                        em{{
                            font-style: normal;
                            background-color: #ECF0F0;
                            color: #376EDE;
                        }}
                        .selected em{{
                            background-color: #606266;
                            color: #FFFFFF;
                        }}
                        .description{{
                            color: #7D8083;
                            padding-left:10px;
                        }}
                        .selected .description{{
                            color: #C0C4CC;
                        }}
                        </style>
                        {content}
                        """
                component_def = AppContext.engine().get_component_def(self._process_def.package, item.component)
                item.component_def = component_def
                content = '<table $$ROOT_STYLE$$><tr><td class="name">'
                if component_def is None:
                    content += gettext('Unknown instruction or process {name}').format(name=html.escape(item.component))
                elif isinstance(component_def, ProcessDef):
                    content += gettext('Invoke process {name}').format(name=html.escape(item.component))
                else:
                    component_class = AppContext.engine().load_component_class(component_def)
                    content += f'{html.escape(gettext(component_def.display_name))}</td><td class="description">'
                    description = component_class.display_description(item)
                    prev_end = 0
                    for match in re.finditer(r'##(.*?)##', description):
                        content += html.escape(description[prev_end:match.start()])
                        content += f'<em>{html.escape(match.group(1))}</em>'
                        prev_end = match.end()
                    content += html.escape(description[prev_end:])
                content += '</td></tr></table>'
                return tpl.format(content=content)
        elif role == Qt.ItemDataRole.BackgroundRole:
            if index.column() == 0:
                return QColor('#fef0f0') if len(item.errors) > 0 else None
        elif role == Qt.ItemDataRole.ToolTipRole:
            if index.column() == 0:
                if len(item.errors) > 0:
                    return "\n".join(item.errors)
                else:
                    return gettext('Press the delete key or the backspace key to delete the instruction.')

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole = Qt.EditRole):
        """Override from QAbstractItemModel

        Set json item according index and role

        Args:
            index (QModelIndex)
            value (Any)
            role (Qt.ItemDataRole)

        """
        if role == Qt.EditRole:
            if index.column() == 0:
                item: FlowNode = index.internalPointer()
                if 'breakpoint' in value:
                    item.breakpoint = value["breakpoint"]
                else:
                    item.component = value["component"]
                    item.inputs = value["inputs"]
                    item.outputs = value["outputs"]
                    if 'error_handling_type' in value:
                        item.error_handling_type = value["error_handling_type"]
                    if 'max_retries' in value:
                        item.max_retries = value["max_retries"]
                    if 'retry_interval' in value:
                        item.retry_interval = value["retry_interval"]
                    if 'outputs_on_error' in value:
                        item.outputs_on_error = value["outputs_on_error"]
                    self.update_dirty()
                self.dataChanged.emit(index, index, [Qt.EditRole])
                return True

        return False

    def update_line_no(self):
        """
        更新所有节点的行号
        """
        stack = []
        stack.extend(reversed(self.process_def.flow))
        line_no = 0
        while len(stack) > 0:
            node = stack.pop()
            line_no += 1
            node.line_no = line_no
            stack.extend(reversed(node.flow))

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = Qt.DisplayRole):
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
            parent_item = self._process_def
        else:
            parent_item = parent.internalPointer()

        child_item = parent_item.flow[row]
        if child_item:
            return self.createIndex(row, column, child_item)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Override from QAbstractItemModel

        Return parent index of index

        """
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent

        if not parent_item:
            return QModelIndex()

        return self.createIndex(self.item_row(parent_item), 0, parent_item)

    def item_row(self, item: FlowNode):
        """Return row of item"""
        if item.parent:
            return item.parent.flow.index(item)
        else:
            return self._process_def.flow.index(item)

    def rowCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return row count from parent index
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            return len(self._process_def.flow)
        else:
            return len(parent.internalPointer().flow)

    def columnCount(self, parent=QModelIndex()):
        """Override from QAbstractItemModel

        Return column number. For the model, it always return 2 columns
        """
        return len(self._headers)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Override from QAbstractItemModel

        Return flags of index
        """
        flags = super(ProcessModel, self).flags(index)

        return Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag.ItemIsDragEnabled | flags

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        if not parent.isValid():
            parent_item = self._process_def
        else:
            parent_item = parent.internalPointer()
        for i in range(count):
            item = FlowNode(self._process_def, None if parent_item is self._process_def else parent_item)
            parent_item.flow.insert(row, item)
        self.endInsertRows()
        return True

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        if not parent.isValid():
            parentItem = self._process_def
        else:
            parentItem = parent.internalPointer()
        for i in range(count):
            parentItem.flow.pop(row)
        self.endRemoveRows()
        self.update_dirty()
        return True

    def mimeTypes(self):
        return [mimetype_process_flow_nodes]

    def mimeData(self, indexes):
        mime_data = QMimeData()
        subtree_indexes = self.get_subtree_indexes(indexes)
        node_data_list = []
        for index in subtree_indexes:
            node_data = snapshot_flow_node_tree(index.internalPointer())
            node_data['source_parent_index_locator'] = self.index_locator(index.parent())
            node_data['source_row'] = index.row()
            node_data_list.append(node_data)
        data = {
            "source_process_def_id": self.process_def.id(AppContext.app().app_package),
            "node_data_list": node_data_list
        }
        mime_data.setData(mimetype_process_flow_nodes, json.dumps(data, ensure_ascii=False).encode('utf-8'))
        return mime_data

    def get_subtree_indexes(self, indexes):
        subtree_indexes = []
        for index in indexes:
            parent = index.parent()
            while parent.isValid():
                if any(index2 == parent for index2 in indexes):
                    break
                parent = parent.parent()
            else:
                subtree_indexes.append(index)
        subtree_indexes.sort(key=lambda index: index.internalPointer().line_no)
        return subtree_indexes

    def supportedDropActions(self):
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    def canDropMimeData(self, data, action, row, column, parent):
        if action == Qt.DropAction.IgnoreAction:
            return True
        if not data.hasFormat(mimetype_component_def_ids) and not data.hasFormat(mimetype_process_flow_nodes):
            return False
        if column > 0:
            return False
        if parent.isValid() and parent.column() > 0:
            return False
        return True

    def dropMimeData(self, data, action, row, column, parent):
        if not self.canDropMimeData(data, action, row, column, parent):
            return False
        if action == Qt.DropAction.IgnoreAction:
            return True
        if row != -1:
            begin_row = row
        else:
            begin_row = self.rowCount(parent)
        if data.hasFormat(mimetype_component_def_ids):
            component_def_ids = data.data(mimetype_component_def_ids).data().decode('utf-8').split(',')
            comp_def = AppContext.engine().get_component_def(self.process_def.package, component_def_ids[0])
            self.component_dropped.emit(begin_row, parent, comp_def)
            return True
        elif data.hasFormat(mimetype_process_flow_nodes):
            nodes_data = json.loads(data.data(mimetype_process_flow_nodes).data().decode('utf-8'))
            self.nodes_dropped.emit(action, begin_row, parent, nodes_data)
            return True
        else:
            return False

    def index_locator(self, index: QModelIndex):
        row_path = []
        column_path = []
        while index.isValid():
            row_path.append(index.row())
            column_path.append(index.column())
            index = index.parent()
        row_path.reverse()
        column_path.reverse()
        return row_path, column_path

    def locate_index(self, row_path, column_path):
        index = QModelIndex()
        for row, column in zip(row_path, column_path):
            index = self.index(row, column, index)
            if not index.isValid():
                return QModelIndex()
        return index

    def locate_parent_index(self, row_path, column_path):
        parent_index = self.locate_index(row_path[:-1], column_path[:-1])
        return parent_index, row_path[-1]

    def get_index_by_node_id(self, node_id):
        stack = [QModelIndex()]
        while stack:
            index = stack.pop()
            if index.isValid() and index.internalPointer().id == node_id:
                return index
            for row in range(self.rowCount(index)):
                stack.append(self.index(row, 0, index))
        return None

    def refresh_all_display_data(self):
        stack = [QModelIndex()]
        while stack:
            parent = stack.pop()
            row_count = self.rowCount(parent)
            self.dataChanged.emit(self.index(0, 0, parent), self.index(row_count - 1, 0, parent),
                                  [Qt.ItemDataRole.DisplayRole])
            for row in range(row_count):
                stack.append(self.index(row, 0, parent))


class App(QObject):
    process_def_created = Signal(ProcessDef)
    process_def_config_updated = Signal(ProcessDef)
    process_def_deleted = Signal(str)
    process_def_files_changed = Signal()
    main_process_changed = Signal(str, str)
    web_elements_changed = Signal()
    window_elements_changed = Signal()

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.engine: ExecutionEngine | None = None
        self.app_package: Package | None = None
        self.process_models: list[ProcessModel] = []
        self.web_elements_model: QStandardItemModel | None = None
        self.window_elements_model: QStandardItemModel | None = None
        self.element_icon = QIcon(":/icons/web_element.png")
        self.window_element_icon = QIcon(":/icons/window_element.png")

    def save(self):
        self.app_package.save()

    def load(self, app_path: Path):
        self.engine = ExecutionEngine([])
        self.app_package = self.engine.load_package(app_path)
        self.web_elements_model = QStandardItemModel(self)
        self.reload_web_elements_model()
        self.web_elements_model.dataChanged.connect(
            lambda topLeft, bottomRight, roles: self.web_elements_changed.emit())
        self.web_elements_model.rowsRemoved.connect(lambda parent, first, last: self.web_elements_changed.emit())

        self.window_elements_model = QStandardItemModel(self)
        self.reload_window_elements_model()
        self.window_elements_model.dataChanged.connect(
            lambda topLeft, bottomRight, roles: self.window_elements_changed.emit())
        self.window_elements_model.rowsRemoved.connect(lambda parent, first, last: self.window_elements_changed.emit())

    @Slot()
    def reload_web_elements_model(self):
        self.web_elements_model.clear()
        for group in self.app_package.get_web_element_groups():
            group_item = QStandardItem(group["name"])
            if "icon" in group:
                group_item.setIcon(QIcon(str(group["icon"])))
            group_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.web_elements_model.appendRow(group_item)
            for element in self.app_package.get_web_elements_by_group(group["name"]):
                element_item = QStandardItem(element["name"])
                element_item.setIcon(self.element_icon)
                element_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                element_item.setData(element["id"], Qt.ItemDataRole.UserRole)
                element_item.setData(build_web_element_uri(element), Qt.ItemDataRole.UserRole + 1)
                group_item.appendRow(element_item)

    @Slot()
    def reload_window_elements_model(self):
        self.window_elements_model.clear()
        for group in self.app_package.get_window_element_groups():
            group_item = QStandardItem(group["name"])
            if "icon" in group:
                group_item.setIcon(QIcon(str(group["icon"])))
            group_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.window_elements_model.appendRow(group_item)
            for element in self.app_package.get_window_elements_by_group(group["name"]):
                element_item = QStandardItem(element["name"])
                element_item.setIcon(self.window_element_icon)
                element_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                element_item.setData(element["id"], Qt.ItemDataRole.UserRole)
                element_item.setData(build_window_element_uri(element["id"]), Qt.ItemDataRole.UserRole + 1)
                group_item.appendRow(element_item)

    def get_all_process_defs(self) -> list[ProcessDef]:
        return [item for item in self.app_package.components if isinstance(item, ProcessDef)]

    def create_process_def(self, process_def_name: str) -> ProcessDef:
        process_file = self.app_package.path / f'{process_def_name}.process.json'
        process_def = ProcessDef(self.app_package)
        process_def.name = process_def_name
        process_def.path = process_file
        process_def.save_to_file(process_file)
        self.app_package.components.append(process_def)
        self.process_def_created.emit(process_def)
        self.process_def_files_changed.emit()
        return process_def

    def update_process_def_config(self, process_def: ProcessDef, process_def_name: str):
        if process_def.name != process_def_name:
            old_name = process_def.name
            new_path = process_def.path.parent / f'{process_def_name}.process.json'
            process_def.path.rename(new_path)
            process_def.name = process_def_name
            process_def.path = new_path
            process_def.save_to_file(process_def.path)
            if self.app_package.main_process == old_name:
                self.app_package.main_process = process_def_name
                self.save()
            self.process_def_config_updated.emit(process_def)
            self.process_def_files_changed.emit()
            return process_def

    def open_process_def(self, process_def: ProcessDef):
        process_model = ProcessModel(process_def)
        self.process_models.append(process_model)
        self.web_elements_changed.connect(lambda: process_model.refresh_all_display_data())
        return process_model

    def close_process_def(self, process_model: ProcessModel):
        process_model.process_def.reload()
        self.process_models.remove(process_model)

    def set_main_process_def(self, process_def_name: str | None):
        old_value = self.app_package.main_process
        self.app_package.main_process = process_def_name
        self.save()
        self.main_process_changed.emit(old_value, process_def_name)

    def is_main_process_def(self, process_def_name: str):
        return self.app_package.main_process == process_def_name

    def delete_process_def(self, process_def: ProcessDef):
        if self.app_package.main_process == process_def.name:
            self.set_main_process_def(None)
            self.save()
        for process_model in self.process_models:
            if process_model.process_def == process_def:
                self.process_models.remove(process_model)
                break
        self.app_package.components.remove(process_def)
        self.process_def_deleted.emit(process_def.name)
        self.process_def_files_changed.emit()
        os.remove(process_def.path)
