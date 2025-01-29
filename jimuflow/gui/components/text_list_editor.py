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

from PySide6.QtWidgets import QWidget, QLineEdit

from jimuflow.gui.components.list_editor import ListEditor


class TextListEditor(ListEditor):
    def __init__(self, add_button_label: str, parent: QWidget = None):
        super().__init__(add_button_label, parent)

    def create_row_editor(self) -> QLineEdit:
        return QLineEdit()

    def get_editor_value(self, editor: QLineEdit):
        return editor.text()

    def set_editor_value(self, editor: QLineEdit, value):
        editor.setText(value)

    def clear_editor_value(self, editor: QLineEdit):
        editor.clear()
