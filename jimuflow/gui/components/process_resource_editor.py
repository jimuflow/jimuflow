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
from jimuflow.gui.app import AppContext
from jimuflow.gui.expression_edit_v3 import ExpressionEditV3
from jimuflow.gui.process_resource_dialog import ProcessResourceDialog, SaveProcessResourceDialog
from jimuflow.gui.screenshot_tool import ScreenshotWidget
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.expression import escape_string


class ProcessResourceEdit(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._value_editor = ExpressionEditV3()
        button = QPushButton(gettext('Select Resource'))
        button.clicked.connect(self._open_tool)
        self._layout.addWidget(self._value_editor, 0, 0)
        self._layout.addWidget(button, 0, 1)

    def get_value(self):
        return self._value_editor.get_expression()

    def set_value(self, value: str):
        self._value_editor.set_expression(value)

    def setPlaceholderText(self, text):
        self._value_editor.setPlaceholderText(text)

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._value_editor.set_variables(variables, type_registry)

    @Slot()
    def _open_tool(self):
        tool = ProcessResourceDialog(self)
        if tool.exec() == QDialog.DialogCode.Accepted:
            self.set_value(escape_string(tool._selected_resource))


class ImageResourceEdit(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._screenshot_tool = None
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._value_editor = ExpressionEditV3()
        self._layout.addWidget(self._value_editor, 0, 0)

        select_button = QPushButton(gettext('Select Resource'))
        select_button.clicked.connect(self._open_tool)
        self._layout.addWidget(select_button, 0, 1)

        screenshot_button = QPushButton(gettext('Screenshot'))
        screenshot_button.clicked.connect(self._open_screenshot_tool)
        self._layout.addWidget(screenshot_button, 0, 2)

    def get_value(self):
        return self._value_editor.get_expression()

    def set_value(self, value: str):
        self._value_editor.set_expression(value)

    def setPlaceholderText(self, text):
        self._value_editor.setPlaceholderText(text)

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._value_editor.set_variables(variables, type_registry)

    @Slot()
    def _open_tool(self):
        tool = ProcessResourceDialog(self)
        if tool.exec() == QDialog.DialogCode.Accepted:
            self.set_value(escape_string(tool.accepted_value))

    @Slot()
    def _open_screenshot_tool(self):
        self._screenshot_tool = ScreenshotWidget()
        self._screenshot_tool.finished.connect(self._on_screenshot_tool_finished)
        self._screenshot_tool.show()

    @Slot(int)
    def _on_screenshot_tool_finished(self, result):
        self._screenshot_tool.finished.disconnect(self._on_screenshot_tool_finished)
        if result == QDialog.DialogCode.Accepted and not self._screenshot_tool.accepted_value.isNull():
            screenshot = self._screenshot_tool.accepted_value
            save_tool = SaveProcessResourceDialog(default_file_name='screenshot', file_suffix='.png', parent=self)
            if save_tool.exec() == QDialog.DialogCode.Accepted:
                root_path = AppContext.app().app_package.path / "resources"
                resource_name = save_tool.accepted_value
                screenshot.save(str(root_path / resource_name), "PNG")
                self.set_value(escape_string(resource_name))
        self._screenshot_tool = None
