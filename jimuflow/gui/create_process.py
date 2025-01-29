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

from PySide6.QtCore import Slot, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, \
    QDialogButtonBox, QMessageBox

from jimuflow.definition import ProcessDef
from jimuflow.gui.app import App
from jimuflow.locales.i18n import gettext


class CreateProcessDialog(QDialog):
    def __init__(self, app: App, process_def: ProcessDef | None, parent=None):
        super().__init__(parent)
        self._app = app
        self.process_def = process_def

        self.setWindowTitle(gettext("Config Process") if app else gettext('New Process'))
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        form_layout = QFormLayout()
        self._name_edit = QLineEdit()
        self._name_edit.setFixedWidth(200)
        self._name_edit.setToolTip(
            gettext('Any non blank characters and underscores other than punctuation can be used, and the length cannot exceed 100 characters.'))
        self._name_edit.setValidator(
            QRegularExpressionValidator(QRegularExpression(R"([^\s\p{P}]|_)+"), self))
        if process_def:
            self._name_edit.setText(process_def.name)
        form_layout.addRow(QLabel(gettext("Process name:")), self._name_edit)

        self.layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.create_process)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        self.layout.addWidget(button_box)

    @Slot()
    def create_process(self):
        name = self._name_edit.text()
        if not name:
            QMessageBox.warning(self, gettext('Tips'), gettext('Process name cannot be empty'))
            return

        if self.process_def is None:
            self.process_def = self._app.create_process_def(name)
        else:
            self._app.update_process_def_config(self.process_def, name)
        self.accept()
