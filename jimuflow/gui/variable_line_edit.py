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

import sys

from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QStandardItemModel, QStandardItem, QRegularExpressionValidator
from PySide6.QtWidgets import QLineEdit, QCompleter, QApplication

from jimuflow.definition import VariableDef


class VariableLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._completer_model = QStandardItemModel()
        self._completer = QCompleter(self._completer_model, self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.setCompleter(self._completer)
        re = QRegularExpression("[_a-zA-Z\u4e00-\u9fa5](\\w|[\u4e00-\u9fa5])*")
        self.setValidator(QRegularExpressionValidator(re, self))

    def set_variables(self, variables: list[VariableDef]):
        self._completer_model.clear()
        for var_def in variables:
            item = QStandardItem(var_def.name)
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self._completer_model.appendRow(item)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down:
            self._completer.setCompletionPrefix("")
            self._completer.complete()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = VariableLineEdit()
    widget.set_variables([VariableDef("abc", "int"), VariableDef("变量1", "int")])
    widget.show()
    sys.exit(app.exec())
