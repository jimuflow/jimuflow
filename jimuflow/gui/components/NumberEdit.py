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

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QLineEdit


class NumberEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(QRegularExpression(R"-?\d+(\.\d*)?"), self))

    def get_value(self) -> int | float | None:
        if self.text() == "":
            return None
        elif '.' in self.text():
            return float(self.text())
        else:
            return int(self.text())

    def set_value(self, value: int | float | None):
        if value is None:
            self.setText("")
        else:
            self.setText(str(value))
