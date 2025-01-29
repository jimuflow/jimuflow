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

from PySide6.QtCore import QEvent
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class HoverWindowElementTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Click Window Element Test App")
        layout = QVBoxLayout(self)
        self._label = QLabel('Not Hovered')
        layout.addWidget(self._label)
        self._button = QPushButton("Hover Me")
        self._button.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self._button.setAccessibleName("HoverMeButton")
        self._button.installEventFilter(self)
        layout.addWidget(self._button)
        self.setGeometry(100, 100, 400, 300)
        self.show()

    def eventFilter(self, watched, event):
        if watched is self._button:
            if event.type() == QEvent.Type.HoverEnter:
                self._label.setText("Hovered")
                return True
            elif event.type() == QEvent.Type.HoverLeave:
                self._label.setText("Not Hovered")
                return True
        return False


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    test_windows_app = HoverWindowElementTestApp()
    sys.exit(app.exec())
