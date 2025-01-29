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

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class GetRelativeWindowElementTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Get Relative Window Element Test App")
        layout = QVBoxLayout(self)
        level1=QGroupBox("Level 1")
        level1_layout=QVBoxLayout(level1)
        layout.addWidget(level1)
        for i in range(3):
            level1_layout.addWidget(QLabel(f"Level 1 - {i}"))
        level2=QGroupBox("Level 2")
        level2.setAccessibleName("Level 2")
        level2_layout=QVBoxLayout(level2)
        level1_layout.addWidget(level2)
        for i in range(3):
            level2_layout.addWidget(QLabel(f"Level 2 - {i}"))
        self.setGeometry(200, 100, 400, 300)
        self.show()



if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    test_windows_app = GetRelativeWindowElementTestApp()
    sys.exit(app.exec())
