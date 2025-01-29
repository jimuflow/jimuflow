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


class ListEditor(QWidget):
    def __init__(self, add_button_label: str, parent: QWidget = None):
        super().__init__(parent)
        self._rows = []
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._add_row_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd), add_button_label)
        self._layout.addWidget(self._add_row_button, 0, 0)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 0)
        self._add_row_button.clicked.connect(self._add_row)
        self._add_row()
        self.setContentsMargins(0, 0, 0, 0)

    @Slot()
    def _add_row(self):
        self._layout.removeWidget(self._add_row_button)
        row_editor = self.create_row_editor()
        delete_row_button = QToolButton()
        delete_row_button.setIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListRemove))
        delete_row_button.clicked.connect(self._on_delete_row)
        self._rows.append((row_editor, delete_row_button))
        row = self._layout.rowCount()
        self._layout.addWidget(row_editor, row, 0)
        self._layout.addWidget(delete_row_button, row, 1)
        self._layout.addWidget(self._add_row_button, row + 1, 0)

    def create_row_editor(self) -> QWidget:
        pass

    @Slot()
    def _on_delete_row(self):
        delete_row_button = self.sender()
        for row in self._rows:
            if row[1] == delete_row_button:
                self._delete_row(row)
                self._rows.remove(row)
                break

    def _delete_row(self, row):
        self._layout.removeWidget(row[0])
        self._layout.removeWidget(row[1])
        row[0].deleteLater()
        row[1].deleteLater()

    def validate(self):
        errors = []
        for row in self._rows:
            errors.extend(self.validate_editor(row[0]))
        return errors

    def validate_editor(self, editor: QWidget) -> list[str]:
        return []

    def get_value(self):
        return [self.get_editor_value(row[0]) for row in self._rows]

    def get_editor_value(self, editor: QWidget):
        pass

    def set_value(self, value: list):
        for i in range(len(value)):
            if i >= len(self._rows):
                self._add_row()
            self.set_editor_value(self._rows[i][0], value[i])
        if len(value) < len(self._rows):
            if len(value) == 0:
                self.clear_editor_value(self._rows[0][0])
                delete_from = 1
            else:
                delete_from = len(value)
            for row in self._rows[delete_from:]:
                self._delete_row(row)
            self._rows = self._rows[:delete_from]

    def set_editor_value(self, editor: QWidget, value):
        pass

    def clear_editor_value(self, editor: QWidget):
        pass
