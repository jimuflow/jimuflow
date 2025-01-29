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

import sys
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel


class DragWindowElementTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag Window Element Test App")
        self.setGeometry(100, 100, 400, 300)

        # 创建一个按钮
        self.button = QPushButton("拖动我", self)
        self.button.setGeometry(150, 100, 100, 40)

        # 设置按钮可以接收鼠标事件
        self.button.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # 用于跟踪鼠标位置
        self.drag_position = QPoint()

        self.label=QLabel("拖到我这",self)
        self.label.setGeometry(250, 250, 100, 40)

    def mousePressEvent(self, event):
        # 检查鼠标是否按在按钮上
        pos=event.position().toPoint()
        if self.button.geometry().contains(pos):
            self.drag_position = pos - self.button.pos()

    def mouseMoveEvent(self, event):
        # 鼠标移动时更新按钮的位置
        if not self.drag_position.isNull():
            pos = event.position().toPoint()
            new_position = pos - self.drag_position
            self.button.move(new_position)

    def mouseReleaseEvent(self, event):
        # 鼠标释放时清除拖拽位置
        self.drag_position = QPoint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DragWindowElementTestApp()
    window.show()
    sys.exit(app.exec())
