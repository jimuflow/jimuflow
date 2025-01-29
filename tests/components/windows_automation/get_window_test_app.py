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

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class GetWindowTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Get Window Test App")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Get Window Test"))
        self.setGeometry(200, 100, 400, 300)
        self.show()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    test_windows_app = GetWindowTestApp()
    sys.exit(app.exec())
