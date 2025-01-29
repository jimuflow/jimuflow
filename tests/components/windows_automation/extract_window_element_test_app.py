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

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QCheckBox, QComboBox


class ExtractWindowElementTestApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extract Window Element Test App")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("label text"))
        layout.addWidget(QLineEdit("line edit"))
        layout.addWidget(QTextEdit("text edit"))
        layout.addWidget(QCheckBox("check box 1"))
        checkbox = QCheckBox("check box 2")
        checkbox.setChecked(True)
        layout.addWidget(checkbox)
        combobox = QComboBox()
        combobox.addItems(["item 1", "item 2", "item 3"])
        combobox.setCurrentIndex(1)
        layout.addWidget(combobox)
        self.setGeometry(200, 100, 400, 300)
        self.show()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    test_windows_app = ExtractWindowElementTestApp()
    sys.exit(app.exec())
