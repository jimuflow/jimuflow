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

from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox

from jimuflow.common.keyboard import keyboard_keys


class HotkeyEdit(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._key1 = self._create_key_combobox()
        self._key2 = self._create_key_combobox()
        self._key3 = self._create_key_combobox()
        self._key4 = self._create_key_combobox()
        layout.addWidget(self._key1)
        layout.addWidget(self._key2)
        layout.addWidget(self._key3)
        layout.addWidget(self._key4)

    def _create_key_combobox(self):
        combobox = QComboBox()
        combobox.addItem("--", "")
        for key, label in keyboard_keys.items():
            combobox.addItem(label, key)
        return combobox

    def get_value(self):
        value = []
        for key in [self._key1, self._key2, self._key3, self._key4]:
            if key.currentIndex() > 0:
                value.append(key.currentData())
        return value

    def set_value(self, value):
        for i, key in enumerate([self._key1, self._key2, self._key3, self._key4]):
            if value and i < len(value):
                key.setCurrentIndex(key.findData(value[i]))
            else:
                key.setCurrentIndex(0)
