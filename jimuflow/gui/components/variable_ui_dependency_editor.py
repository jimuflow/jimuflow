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

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QGridLayout, QComboBox, QLineEdit

from jimuflow.definition import VariableUiDependency, VariableDirection, VariableUiDependencyOperator, VariableDef
from jimuflow.gui.app import ProcessModel
from jimuflow.gui.components.text_list_editor import TextListEditor
from jimuflow.locales.i18n import gettext


class VariableUiDependencyEditor(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._variable_name_editor = QComboBox()
        self._operator_editor = QComboBox()
        self._operator_editor.addItem('--')
        for op in VariableUiDependencyOperator:
            self._operator_editor.addItem(op.display_name, op.value)
        self._operator_editor.currentIndexChanged.connect(self._on_op_changed)
        self._value_editor: QWidget | None = None
        self._layout.addWidget(self._variable_name_editor, 0, 0)
        self._layout.addWidget(self._operator_editor, 0, 1)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 0)
        self._layout.setColumnStretch(2, 2)
        self.setContentsMargins(0, 0, 0, 0)
        self._process_model: ProcessModel | None = None

    def set_process_model(self, process_model: ProcessModel, current_var_def: VariableDef = None):
        self._process_model = process_model
        self._variable_name_editor.clear()
        self._variable_name_editor.addItem('--')
        for var_def in self._process_model.process_def.variables:
            if var_def.direction == VariableDirection.IN and (
                    current_var_def is None or current_var_def.name != var_def.name):
                self._variable_name_editor.addItem(var_def.name, var_def)
        self._variable_name_editor.setCurrentIndex(0)
        self._operator_editor.setCurrentIndex(0)
        if isinstance(self._value_editor, TextListEditor):
            self._value_editor.set_value([])
        elif isinstance(self._value_editor, QLineEdit):
            self._value_editor.setText("")

    @Slot(int)
    def _on_op_changed(self, index: int = 0):
        op: str = self._operator_editor.currentData()
        if op == VariableUiDependencyOperator.IN.value:
            if not isinstance(self._value_editor, TextListEditor):
                if self._value_editor is not None:
                    self._layout.removeWidget(self._value_editor)
                    self._value_editor.deleteLater()
                self._value_editor = TextListEditor(gettext("Add value"))
                self._layout.addWidget(self._value_editor, 0, 2)
        elif op == VariableUiDependencyOperator.EQUALS.value:
            if not isinstance(self._value_editor, QLineEdit):
                if self._value_editor is not None:
                    self._layout.removeWidget(self._value_editor)
                    self._value_editor.deleteLater()
                self._value_editor = QLineEdit()
                self._layout.addWidget(self._value_editor, 0, 2)
        else:
            if self._value_editor is not None:
                self._layout.removeWidget(self._value_editor)
                self._value_editor.deleteLater()

    def get_value(self):
        variable_def = self._variable_name_editor.currentData()
        op: str = self._operator_editor.currentData()
        if isinstance(self._value_editor, TextListEditor):
            value = self._value_editor.get_value()
        elif isinstance(self._value_editor, QLineEdit):
            value = self._value_editor.text()
        else:
            value = ''
        return VariableUiDependency(variable_def.name if variable_def else '', op if op else '', value)

    def set_value(self, value: VariableUiDependency):
        if value.variable_name:
            self._variable_name_editor.setCurrentIndex(self._variable_name_editor.findText(value.variable_name))
        else:
            self._variable_name_editor.setCurrentIndex(-1)
        if value.operator:
            self._operator_editor.setCurrentIndex(self._operator_editor.findData(value.operator))
        else:
            self._operator_editor.setCurrentIndex(-1)
        if isinstance(self._value_editor, TextListEditor):
            self._value_editor.set_value(value.value)
        elif isinstance(self._value_editor, QLineEdit):
            self._value_editor.setText(value.value)
