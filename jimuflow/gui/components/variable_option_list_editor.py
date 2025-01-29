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

from PySide6.QtWidgets import QWidget, QLineEdit, QGridLayout

from jimuflow.definition.variable_def import VariableUiInputOption
from jimuflow.gui.components.list_editor import ListEditor
from jimuflow.locales.i18n import gettext


class VariableOptionEditor(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 1)
        self._label_editor = QLineEdit()
        self._label_editor.setPlaceholderText(gettext("Option label"))
        self._value_editor = QLineEdit()
        self._value_editor.setPlaceholderText(gettext("Option value"))
        self._layout.addWidget(self._label_editor, 0, 0)
        self._layout.addWidget(self._value_editor, 0, 1)
        self.setContentsMargins(0, 0, 0, 0)

    def get_value(self):
        return VariableUiInputOption(self._label_editor.text(), self._value_editor.text())

    def set_value(self, value: VariableUiInputOption):
        self._label_editor.setText(value.label)
        self._value_editor.setText(value.value)

    def clear(self):
        self._label_editor.clear()
        self._value_editor.clear()


class VariableOptionsEditor(ListEditor):
    def __init__(self, add_button_label: str, parent: QWidget = None):
        super().__init__(add_button_label, parent)

    def create_row_editor(self) -> VariableOptionEditor:
        return VariableOptionEditor()

    def get_editor_value(self, editor: VariableOptionEditor):
        return editor.get_value()

    def set_editor_value(self, editor: VariableOptionEditor, value):
        editor.set_value(value)

    def clear_editor_value(self, editor: VariableOptionEditor):
        editor.clear()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    editor = VariableOptionsEditor("Add")
    editor.show()
    app.exec()
