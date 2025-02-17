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

import subprocess
import sys

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QDialog, QLabel, QDialogButtonBox, QFormLayout, QComboBox, QMessageBox, QVBoxLayout, \
    QApplication

from jimuflow.gui.utils import Utils
from jimuflow.locales.i18n import gettext


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(gettext("Settings"))
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        self._language_label = QLabel(gettext("Language"))
        self._language_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._language_combobox = QComboBox()
        for language, label in Utils.get_supported_languages().items():
            self._language_combobox.addItem(label, language)
        self._language_combobox.setCurrentIndex(self._language_combobox.findData(Utils.get_language()))
        form_layout.addRow(self._language_label, self._language_combobox)
        layout.addLayout(form_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        layout.addWidget(button_box)

    def accept(self):
        if self._language_combobox.currentData() != Utils.get_language():
            Utils.set_language(self._language_combobox.currentData())
            # 提示用户是否现在重启已应用新的语言设置
            if QMessageBox.question(self, gettext("Restart required"),
                                    gettext(
                                        "Restart required to apply the new language setting. Do you want to restart now?"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                program = sys.executable
                args = sys.argv

                @Slot()
                def start_new_process():
                    command = [program] + args

                    if sys.platform == 'win32':
                        subprocess.Popen(
                            command,
                            creationflags=subprocess.DETACHED_PROCESS,
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    else:
                        subprocess.Popen(
                            command,
                            start_new_session=True,
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )

                # 当应用即将退出时，启动新进程
                QApplication.instance().aboutToQuit.connect(start_new_process)

                QApplication.quit()  # 退出应用
        super().accept()
