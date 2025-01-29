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

from PySide6.QtCore import Slot, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class WaitWindowElementTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Click Window Element Test App")
        layout = QVBoxLayout(self)
        self._button1 = QPushButton("Add Label")
        self._button2 = QPushButton("Remove Label")
        self._label1 = QLabel("Label to remove")
        self._label2 = None
        layout.addWidget(self._button1)
        layout.addWidget(self._button2)
        layout.addWidget(self._label1)
        self._button1.clicked.connect(self._add_label)
        self._button2.clicked.connect(self._remove_label)
        self.setGeometry(100, 100, 400, 300)
        self.show()

    @Slot()
    def _add_label(self):
        if self._label2:
            return
        QTimer.singleShot(2000, self._do_add_label)

    @Slot()
    def _do_add_label(self):
        if self._label2:
            return
        self._label2 = QLabel("Added Label")
        self.layout().addWidget(self._label2)

    @Slot()
    def _remove_label(self):
        if self._label1:
            QTimer.singleShot(2000, self._do_remove_label)

    @Slot()
    def _do_remove_label(self):
        if self._label1:
            self.layout().removeWidget(self._label1)
            self._label1.deleteLater()
            self._label1 = None


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    test_windows_app = WaitWindowElementTestApp()
    sys.exit(app.exec())
