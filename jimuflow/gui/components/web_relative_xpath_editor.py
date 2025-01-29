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
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QDialog

from jimuflow.datatypes import DataTypeRegistry
from jimuflow.definition import VariableDef
from jimuflow.gui.expression_edit_v3 import ExpressionEditV3
from jimuflow.gui.web_element_relative_xpath_tool import WebElementRelativeXpathTool
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.expression import escape_string


class WebRelativeXPathEdit(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._xpath_editor = ExpressionEditV3()
        button = QPushButton(gettext('Get Relative XPath'))
        button.clicked.connect(self._open_tool)
        self._layout.addWidget(self._xpath_editor, 0, 0)
        self._layout.addWidget(button, 0, 1)

    def get_value(self):
        return self._xpath_editor.get_expression()

    def set_value(self, value: str):
        self._xpath_editor.set_expression(value)

    def setPlaceholderText(self, text):
        self._xpath_editor.setPlaceholderText(text)

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._xpath_editor.set_variables(variables, type_registry)

    @Slot()
    def _open_tool(self):
        tool = WebElementRelativeXpathTool()
        if tool.exec_until_closed() == QDialog.DialogCode.Accepted:
            self.set_value(escape_string(tool.accepted_xpath))
