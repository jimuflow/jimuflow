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

from pathlib import Path

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QFileDialog

from jimuflow.datatypes import DataTypeRegistry
from jimuflow.definition import VariableDef
from jimuflow.gui.expression_edit_v3 import ExpressionEditV3
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.expression import evaluate, escape_string


class FilePathEdit(QWidget):
    def __init__(self, parent: QWidget = None, file_existing=True, button_text=gettext('Choose')):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._expression_editor = ExpressionEditV3()
        button = QPushButton(button_text)
        button.clicked.connect(self._open_tool)
        self._layout.addWidget(self._expression_editor, 0, 0)
        self._layout.addWidget(button, 0, 1)
        self._file_existing = file_existing

    def get_value(self):
        return self._expression_editor.get_expression()

    def set_value(self, value: str):
        self._expression_editor.set_expression(value)

    def setPlaceholderText(self, text):
        self._expression_editor.setPlaceholderText(text)

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._expression_editor.set_variables(variables, type_registry)

    @Slot()
    def _open_tool(self):
        try:
            init_path = evaluate(self.get_value(), {}, DataTypeRegistry())
        except:
            init_path = ''
        init_dir = None
        if init_path:
            file_path = Path(init_path)
            if file_path.parent.is_dir():
                init_dir = str(file_path.parent)
        if self._file_existing:
            new_file_path, _ = QFileDialog.getOpenFileName(self, dir=init_dir)
        else:
            new_file_path, _ = QFileDialog.getSaveFileName(self, dir=init_dir,
                                                           options=QFileDialog.Option.DontConfirmOverwrite)
        if new_file_path:
            self.set_value(escape_string(new_file_path))


class OpenFilePathEdit(FilePathEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent, file_existing=True)


class SaveFilePathEdit(FilePathEdit):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent, file_existing=False)


class FolderPathEdit(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._expression_editor = ExpressionEditV3()
        button = QPushButton(gettext('Choose'))
        button.clicked.connect(self._open_tool)
        self._layout.addWidget(self._expression_editor, 0, 0)
        self._layout.addWidget(button, 0, 1)

    def get_value(self):
        return self._expression_editor.get_expression()

    def set_value(self, value: str):
        self._expression_editor.set_expression(value)

    def setPlaceholderText(self, text):
        self._expression_editor.setPlaceholderText(text)

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._expression_editor.set_variables(variables, type_registry)

    @Slot()
    def _open_tool(self):
        try:
            init_folder = evaluate(self.get_value(), {}, DataTypeRegistry())
        except:
            init_folder = ''
        init_dir = None
        if init_folder:
            folder_path = Path(init_folder)
            if folder_path.parent.is_dir():
                init_dir = str(folder_path.parent)
        new_folder_path = QFileDialog.getExistingDirectory(self, dir=init_dir)
        if new_folder_path:
            self.set_value(escape_string(new_folder_path))


class FileOrFolderPathEdit(QWidget):
    def __init__(self, parent: QWidget = None, file_button_text=gettext('Choose File'),
                 folder_button_text=gettext('Choose Folder')):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._expression_editor = ExpressionEditV3()
        button = QPushButton(file_button_text)
        button.clicked.connect(self._choose_file)
        self._layout.addWidget(self._expression_editor, 0, 0)
        self._layout.addWidget(button, 0, 1)
        button = QPushButton(folder_button_text)
        button.clicked.connect(self._choose_folder)
        self._layout.addWidget(button, 0, 2)

    def get_value(self):
        return self._expression_editor.get_expression()

    def set_value(self, value: str):
        self._expression_editor.set_expression(value)

    def setPlaceholderText(self, text):
        self._expression_editor.setPlaceholderText(text)

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._expression_editor.set_variables(variables, type_registry)

    @Slot()
    def _choose_file(self):
        try:
            init_path = evaluate(self.get_value(), {}, DataTypeRegistry())
        except:
            init_path = ''
        init_dir = None
        if init_path:
            file_path = Path(init_path)
            if file_path.parent.is_dir():
                init_dir = str(file_path.parent)
        new_file_path, _ = QFileDialog.getOpenFileName(self, dir=init_dir)
        if new_file_path:
            self.set_value(escape_string(new_file_path))

    @Slot()
    def _choose_folder(self):
        try:
            init_path = evaluate(self.get_value(), {}, DataTypeRegistry())
        except:
            init_path = ''
        init_dir = None
        if init_path:
            file_path = Path(init_path)
            if file_path.parent.is_dir():
                init_dir = str(file_path.parent)
        new_file_path = QFileDialog.getExistingDirectory(self, dir=init_dir)
        if new_file_path:
            self.set_value(escape_string(new_file_path))
