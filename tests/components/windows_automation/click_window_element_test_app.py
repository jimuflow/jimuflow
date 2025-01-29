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
from PySide6.QtGui import QMouseEvent, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel


class ClickWindowElementTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Click Window Element Test App")
        layout = QVBoxLayout(self)
        self._label = QLabel('Not Clicked')
        layout.addWidget(self._label)
        self._button = QPushButton("Click Me")
        self._button.setAccessibleName("ClickMeButton")
        self._button.installEventFilter(self)
        layout.addWidget(self._button)
        self.setGeometry(100, 100, 400, 300)
        self.show()

    def eventFilter(self, watched, event):
        if watched is self._button:
            if event.type() == QEvent.Type.MouseButtonDblClick:
                keys = self._get_keys(event)
                self._label.setText("+".join(keys) + " Double Clicked")
                return True
            elif event.type() == QEvent.Type.MouseButtonPress:
                keys = self._get_keys(event)
                self._label.setText("+".join(keys) + " Clicked")
                return True
        return False

    def _get_keys(self, mouse_event: QMouseEvent):
        keys = []
        if Qt.KeyboardModifier.AltModifier in mouse_event.modifiers():
            keys.append('Alt')
        if Qt.KeyboardModifier.ControlModifier in mouse_event.modifiers():
            keys.append('Ctrl')
        if Qt.KeyboardModifier.ShiftModifier in mouse_event.modifiers():
            keys.append('Shift')
        if Qt.MouseButton.LeftButton in mouse_event.buttons():
            keys.append('Left')
        if Qt.MouseButton.RightButton in mouse_event.buttons():
            keys.append('Right')
        if Qt.MouseButton.MiddleButton in mouse_event.buttons():
            keys.append('Middle')
        return keys


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    test_windows_app = ClickWindowElementTestApp()
    sys.exit(app.exec())
