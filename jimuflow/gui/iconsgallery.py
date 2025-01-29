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

from PySide6.QtCore import QSize
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtWidgets import QListView


class IconsGallery(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setViewMode(QListView.IconMode)
        self.setGridSize(QSize(128, 64))
        list_model = QStandardItemModel(0, 1, self)
        for theme in QIcon.ThemeIcon:
            list_model.appendRow(QStandardItem(QIcon.fromTheme(theme), theme.name))
        self.setModel(list_model)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication()
    gallery = IconsGallery()
    gallery.resize(QSize(600, 600))
    gallery.show()
    app.exec()
