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

from PySide6.QtCore import Qt, QModelIndex, Slot, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QSplitter, QTableView

from jimuflow.definition import ProcessDef
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import Component


class DebugVariablesWidget(QSplitter):
    call_stack_double_clicked = Signal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOrientation(Qt.Orientation.Horizontal)
        self._call_stack_list = QTableView()
        self._call_stack_model = QStandardItemModel()
        self._call_stack_list.setModel(self._call_stack_model)
        self._call_stack_list.setMinimumWidth(200)
        self._call_stack_model.setHorizontalHeaderLabels([gettext('Call Stack')])
        self._call_stack_list.horizontalHeader().setStretchLastSection(True)
        self.addWidget(self._call_stack_list)
        self._variables_table = QTableView()
        self._variables_model = QStandardItemModel()
        self._variables_table.setModel(self._variables_model)
        self._variables_table.setMinimumWidth(300)
        self._variables_model.setHorizontalHeaderLabels([gettext('Variable Name'), gettext('Variable Value')])
        self._variables_table.setColumnWidth(0, 80)
        self._variables_table.horizontalHeader().setStretchLastSection(True)
        self.addWidget(self._variables_table)
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 1)
        self._call_stack_list.selectionModel().currentChanged.connect(self._on_call_stack_item_changed)
        self._call_stack_list.doubleClicked.connect(self._on_call_stack_item_double_clicked)

    def set_component(self, component: Component | None):
        self._clear_call_stack_model()
        self._clear_variables()
        while component and component.process:
            process_name = gettext('Process {name}').format(name=component.process.component_def.name)
            if isinstance(component.component_def, ProcessDef):
                comp_name = gettext('Process {name}').format(name=component.component_def.name)
            else:
                comp_name = gettext(component.component_def.display_name)
            line_no = component.node.line_no
            line_no_text = gettext('Line {line_no}').format(line_no=line_no)
            call_stack_item = QStandardItem(f'{process_name}({line_no_text}) - {comp_name}')
            call_stack_item.setData(component, Qt.ItemDataRole.UserRole)
            call_stack_item.setData(gettext(
                "Click to view the variable at the call location, double-click to navigate to the call location"),
                Qt.ItemDataRole.ToolTipRole)
            call_stack_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._call_stack_model.appendRow(call_stack_item)
            component = component.process
        if self._call_stack_model.rowCount() > 0:
            index = self._call_stack_model.index(0, 0)
            self._call_stack_list.setCurrentIndex(index)

    def _clear_call_stack_model(self):
        row_count = self._call_stack_model.rowCount()
        if row_count:
            self._call_stack_model.removeRows(0, row_count)

    def _clear_variables(self):
        row_count = self._variables_model.rowCount()
        if row_count:
            self._variables_model.removeRows(0, row_count)

    @Slot(QModelIndex, QModelIndex)
    def _on_call_stack_item_changed(self, current: QModelIndex, previous: QModelIndex):
        self._clear_variables()
        if current.isValid():
            component: Component = current.data(Qt.ItemDataRole.UserRole)
            for name, value in component.process.variables.items():
                name_item = QStandardItem(name)
                name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                name_item.setData(name, Qt.ItemDataRole.ToolTipRole)
                value_text = str(value)
                value_item = QStandardItem(value_text)
                value_item.setData(value_text, Qt.ItemDataRole.ToolTipRole)
                value_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self._variables_model.appendRow([name_item, value_item])

    @Slot(QModelIndex)
    def _on_call_stack_item_double_clicked(self, index: QModelIndex):
        component: Component = index.data(Qt.ItemDataRole.UserRole)
        process_id = component.process.component_id()
        line_no = component.node.line_no
        self.call_stack_double_clicked.emit(process_id, line_no)
