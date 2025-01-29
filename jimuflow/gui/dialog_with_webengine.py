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

from PySide6.QtWidgets import QDialog


class DialogWithWebEngine(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.closed = False

    def closeEvent(self, e):
        super().closeEvent(e)
        self.closed = e.isAccepted()

    def done(self, r):
        super().done(r)
        self.closed = True

    def exec_until_closed(self):
        r = self.result()
        while not self.closed:
            r = self.exec()
        return r
