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

from PySide6.QtWidgets import QComboBox

from jimuflow.datatypes import DataTypeRegistry


class VariableTypeComboBox(QComboBox):
    def __init__(self, type_registry: DataTypeRegistry, parent=None):
        super().__init__(parent)
        for data_type in type_registry.data_types:
            self.addItem(data_type.display_name, data_type)

    def validate(self):
        return []

    def get_value(self):
        return self.currentData().name if self.currentIndex() >= 0 else None

    def set_value(self, value):
        if value is None:
            self.setCurrentIndex(-1)
            return
        for i in range(self.count()):
            if self.itemData(i).name == value:
                self.setCurrentIndex(i)
                break
