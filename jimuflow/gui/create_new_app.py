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

from pathlib import Path

from PySide6.QtCore import Slot, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QLabel, \
    QFileDialog, QDialogButtonBox, QMessageBox

from jimuflow.definition import Package
from jimuflow.gui.app import App
from jimuflow.gui.utils import Utils
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import ExecutionEngine


class CreateNewAppDialog(QDialog):
    def __init__(self, app: App = None, parent=None):
        super().__init__(parent)
        self.app = app

        self.setWindowTitle(gettext('Config Application') if app else gettext('New Application'))
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        form_layout = QFormLayout()
        self._namespace = QLineEdit()
        self._namespace.setMinimumWidth(400)
        self._namespace.setMaxLength(100)
        self._namespace.setValidator(
            QRegularExpressionValidator(QRegularExpression(R"([^\s\p{P}]|_)+(\.([^\s\p{P}]|_)+)*"), self))
        self._namespace.setToolTip(gettext(
            "The namespace is used to distinguish processes with the same name written by different people, using a format similar to a reverse domain name, such as foo, foo.bar.\n"
            "Each part of the namespace consists of any non blank characters and underscores other than punctuation, and the total length cannot exceed 100 characters."))
        if app:
            self._namespace.setText(app.app_package.namespace)
        form_layout.addRow(QLabel(gettext("Namespace:")), self._namespace)
        self._name = QLineEdit()
        self._name.setMinimumWidth(400)
        self._name.setMaxLength(100)
        self._name.setValidator(
            QRegularExpressionValidator(QRegularExpression(R"([^\s\p{P}]|_)+"), self))
        self._name.setToolTip(
            gettext(
                "Consists of any non blank characters and underscores other than punctuation, and the total length cannot exceed 100 characters."))
        if app:
            self._name.setText(app.app_package.name)
        form_layout.addRow(QLabel(gettext("Application name:")), self._name)

        self._version = QLineEdit()
        self._version.setMinimumWidth(400)
        self._version.setMaxLength(50)
        self._version.setValidator(
            QRegularExpressionValidator(QRegularExpression(R"\d+(\.\d+){0,2}"), self))
        self._version.setToolTip(
            gettext(
                "Represent using numbers separated by periods in English, such as 1, 1.0, 1.0.0, with a maximum of 3 numbers and a total length of no more than 50 characters."))
        if app:
            self._version.setText(app.app_package.version)
        form_layout.addRow(QLabel(gettext("Application version:")), self._version)

        if app is None:
            self.app_dir_edit = QLineEdit()
            self.app_dir_edit.setMinimumWidth(400)
            self.app_dir_edit.setText(Utils.get_workspace_path())
            app_dir_layout = QHBoxLayout()
            app_dir_layout.addWidget(self.app_dir_edit)
            choose_dir_button = QPushButton("...")
            choose_dir_button.clicked.connect(self.choose_dir)
            app_dir_layout.addWidget(choose_dir_button)
            form_layout.addRow(QLabel(gettext("Save directory:")), app_dir_layout)

        self.layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.create_app)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        self.layout.addWidget(button_box)

    @Slot()
    def choose_dir(self):
        save_dir = QFileDialog.getExistingDirectory(self, gettext("Save application"), self.app_dir_edit.text())
        if save_dir:
            self.app_dir_edit.setText(save_dir)

    @Slot()
    def create_app(self):
        namespace = self._namespace.text()
        if not namespace:
            QMessageBox.warning(self, gettext('Tips'), gettext('The namespace cannot be empty'))
            return
        name = self._name.text()
        if not name:
            QMessageBox.warning(self, gettext('Tips'), gettext('The application name cannot be empty'))
            return
        app_version = self._version.text()
        if not app_version:
            QMessageBox.warning(self, gettext('Tips'), gettext('The application version cannot be empty'))
            return
        if self.app is None:
            app_dir = self.app_dir_edit.text()
            if not app_dir:
                QMessageBox.warning(self, gettext('Tips'), gettext('Save directory cannot be empty'))
                return
            app_package_path = Path(app_dir) / name
            if app_package_path.exists():
                QMessageBox.warning(self, gettext('Tips'), gettext('The application already exists'))
                return
            app = App()
            app.app_package = Package()
            app.app_package.name = name
            app.app_package.namespace = namespace
            app.app_package.version = app_version
            app.app_package.path = app_package_path
            app.engine = ExecutionEngine([])
            app.save()
            self.app = app
        else:
            self.app.app_package.name = name
            self.app.app_package.namespace = namespace
            self.app.app_package.version = app_version
            self.app.save()
        self.accept()
