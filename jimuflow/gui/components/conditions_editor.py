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
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QToolButton, QComboBox

from jimuflow.components.core.condition_utils import is_binary_op
from jimuflow.components.core.if_component import op_i18n
from jimuflow.datatypes import DataTypeRegistry, builtin_data_type_registry
from jimuflow.definition import VariableDef
from jimuflow.gui.expression_edit_v3 import ExpressionEditV3
from jimuflow.locales.i18n import gettext


class ConditionsEditor(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._conditions = []
        self._variables: list[VariableDef] = []
        self._type_registry = builtin_data_type_registry
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._add_condition_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd), gettext("Add condition"))
        self._layout.addWidget(self._add_condition_button, 0, 0, 1, 3)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 0)
        self._layout.setColumnStretch(2, 1)
        self._layout.setColumnStretch(3, 0)
        self._add_condition_button.clicked.connect(self._add_condition)
        self._add_condition()
        self.setContentsMargins(0, 0, 0, 0)

    @Slot()
    def _add_condition(self):
        self._layout.removeWidget(self._add_condition_button)
        operand1_editor = ExpressionEditV3()
        operand1_editor.setPlaceholderText(gettext("The first operand"))
        operand1_editor.set_variables(self._variables, self._type_registry)
        op_editor = QComboBox()
        for key, label in op_i18n.items():
            op_editor.addItem(label, key)
        op_editor.currentIndexChanged.connect(self._on_op_changed)
        operand2_editor = ExpressionEditV3()
        operand2_editor.setPlaceholderText(gettext("The second operand"))
        operand2_editor.set_variables(self._variables, self._type_registry)
        delete_condition_button = QToolButton()
        delete_condition_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListRemove))
        delete_condition_button.clicked.connect(self._on_delete_condition)
        self._conditions.append((operand1_editor, op_editor, operand2_editor, delete_condition_button))
        row = self._layout.rowCount()
        self._layout.addWidget(operand1_editor, row, 0)
        self._layout.addWidget(op_editor, row, 1)
        self._layout.addWidget(operand2_editor, row, 2)
        self._layout.addWidget(delete_condition_button, row, 3)
        self._layout.addWidget(self._add_condition_button, row + 1, 0, 1, 3)

    @Slot(int)
    def _on_op_changed(self, index: int):
        op_editor = self.sender()
        for condition in self._conditions:
            if condition[1] == op_editor:
                if op_editor.currentData() in ["is_empty", "not_empty"]:
                    condition[2].hide()
                else:
                    condition[2].show()
                break

    @Slot()
    def _on_delete_condition(self):
        delete_condition_button = self.sender()
        for condition in self._conditions:
            if condition[3] == delete_condition_button:
                self._layout.removeWidget(condition[0])
                self._layout.removeWidget(condition[1])
                self._layout.removeWidget(condition[2])
                self._layout.removeWidget(condition[3])
                condition[0].deleteLater()
                condition[1].deleteLater()
                condition[2].deleteLater()
                condition[3].deleteLater()
                self._conditions.remove(condition)
                break

    def validate(self):
        errors = []
        for condition in self._conditions:
            if not condition[0].get_expression():
                errors.append(gettext("The first operand is empty"))
            elif not condition[0].validate_expression():
                errors.append(gettext("The first operand expression is invalid"))
            if is_binary_op(condition[1].currentData()):
                if not condition[2].get_expression():
                    errors.append(gettext("The second operand is empty"))
                elif not condition[2].validate_expression():
                    errors.append(gettext("The second operand expression is invalid"))
        return errors

    def get_value(self):
        return [{'operand1': condition[0].get_expression(),
                 'op': condition[1].currentData(),
                 'operand2': condition[2].get_expression() if is_binary_op(condition[1].currentData()) else None}
                for condition in self._conditions]

    def set_value(self, value):
        for i in range(len(value)):
            if i >= len(self._conditions):
                self._add_condition()
            operand1_editor, op_editor, operand2_editor, _ = self._conditions[i]
            operand1_editor.set_expression(value[i]['operand1'])
            op_editor.setCurrentIndex(list(op_i18n.keys()).index(value[i]['op']))
            if is_binary_op(value[i]['op']):
                operand2_editor.set_expression(value[i]['operand2'])

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._variables = variables
        self._type_registry = type_registry
        for condition in self._conditions:
            condition[0].set_variables(self._variables, self._type_registry)
            condition[2].set_variables(self._variables, self._type_registry)
