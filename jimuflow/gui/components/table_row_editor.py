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
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QToolButton

from jimuflow.datatypes import builtin_data_type_registry, DataTypeRegistry
from jimuflow.definition import VariableDef
from jimuflow.gui.expression_edit_v3 import ExpressionEditV3
from jimuflow.locales.i18n import gettext


class TableRowEditor(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._columns = []
        self._variables: list[VariableDef] = []
        self._type_registry = builtin_data_type_registry
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._add_column_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd), gettext("Add column"))
        self._layout.addWidget(self._add_column_button, 0, 0, 1, 2)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 1)
        self._layout.setColumnStretch(2, 0)
        self._add_column_button.clicked.connect(self._add_column)
        self._add_column()
        self.setContentsMargins(0, 0, 0, 0)


    @Slot()
    def _add_column(self):
        self._layout.removeWidget(self._add_column_button)
        column_no_editor = ExpressionEditV3()
        column_no_editor.setPlaceholderText(gettext("Column name/number"))
        column_no_editor.set_variables(self._variables, self._type_registry)
        column_value_editor = ExpressionEditV3()
        column_value_editor.setPlaceholderText(gettext("Cell value"))
        column_value_editor.set_variables(self._variables, self._type_registry)
        delete_column_button = QToolButton()
        delete_column_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListRemove))
        delete_column_button.clicked.connect(self._on_delete_column)
        self._columns.append((column_no_editor, column_value_editor, delete_column_button))
        row = self._layout.rowCount()
        self._layout.addWidget(column_no_editor, row, 0)
        self._layout.addWidget(column_value_editor, row, 1)
        self._layout.addWidget(delete_column_button, row, 2)
        self._layout.addWidget(self._add_column_button, row + 1, 0, 1, 2)

    @Slot()
    def _on_delete_column(self):
        delete_column_button = self.sender()
        for column in self._columns:
            if column[2] == delete_column_button:
                self._layout.removeWidget(column[0])
                self._layout.removeWidget(column[1])
                self._layout.removeWidget(column[2])
                column[0].deleteLater()
                column[1].deleteLater()
                column[2].deleteLater()
                self._columns.remove(column)
                break

    def validate(self):
        errors = []
        for column in self._columns:
            if not column[0].get_expression():
                errors.append(gettext("Column name/number is empty"))
            elif not column[0].validate_expression():
                errors.append(gettext("Column name/number expression is invalid"))
            if not column[1].get_expression():
                errors.append(gettext("Cell value is empty"))
            elif not column[1].validate_expression():
                errors.append(gettext("Cell value expression is invalid"))
        return errors

    def get_value(self):
        return [
            (column[0].get_expression(), column[1].get_expression())
            for column in self._columns
        ]

    def set_value(self, value):
        for i in range(len(value)):
            if i >= len(self._columns):
                self._add_column()
            column_no_editor, column_value_editor, _ = self._columns[i]
            column_no_editor.set_expression(value[i][0])
            column_value_editor.set_expression(value[i][1])

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._variables = variables
        self._type_registry = type_registry
        for column in self._columns:
            column[0].set_variables(self._variables, self._type_registry)
            column[1].set_variables(self._variables, self._type_registry)
