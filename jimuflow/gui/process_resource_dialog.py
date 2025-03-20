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

import os.path
import sys
from pathlib import Path

from PySide6.QtCore import Slot, QModelIndex, QPoint
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QTreeView, QLineEdit, \
    QApplication, QGridLayout, QLabel, QPushButton, QMessageBox, QMenu

from jimuflow.gui.app import AppContext
from jimuflow.gui.process_resource_widget import ProcessResourceModel
from jimuflow.locales.i18n import gettext


class ProcessResourceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.accepted_value = None
        self.setWindowTitle(gettext("Select Resource"))
        main_layout = QVBoxLayout(self)
        self._create_content_widgets(main_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_ok)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        main_layout.addWidget(button_box)
        self.resize(600, 350)

    def _create_content_widgets(self, main_layout: QVBoxLayout):
        tree_view = QTreeView()
        model = ProcessResourceModel()
        root_path = AppContext.app().app_package.path / "resources"
        if not root_path.is_dir():
            root_path.mkdir()
        model.setRootPath(str(root_path))

        tree_view.setModel(model)
        tree_view.setRootIndex(model.index(str(root_path)))
        tree_view.doubleClicked.connect(self._on_double_clicked)
        main_layout.addWidget(tree_view)
        self._tree_view = tree_view
        self._tree_model = model
        self._tree_view.setColumnWidth(0, 200)

    @Slot(QModelIndex)
    def _on_double_clicked(self, index):
        self.accepted_value = os.path.relpath(self._tree_model.filePath(index),
                                              self._tree_model.rootPath())
        self.accept()

    @Slot()
    def _on_ok(self):
        selected_indexes = self._tree_view.selectedIndexes()
        if len(selected_indexes) > 0:
            self.accepted_value = os.path.relpath(self._tree_model.filePath(selected_indexes[0]),
                                                  self._tree_model.rootPath())
        else:
            self.accepted_value = None
        self.accept()


class SaveProcessResourceDialog(QDialog):
    def __init__(self, default_file_name='', file_suffix='', parent=None):
        super().__init__(parent)
        self._file_suffix = file_suffix
        self._back_stack = []
        self._forward_stack = []
        self.accepted_value = None
        self.setWindowTitle(gettext("Save Resource"))
        main_layout = QVBoxLayout(self)
        self._create_content_widgets(main_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self._ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_button.setText(gettext('Ok'))
        self._ok_button.setDisabled(True)
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        main_layout.addWidget(button_box)

        # 设置默认文件名
        if default_file_name:
            file_name = default_file_name
            file_name_index = 1
            file_path = os.path.join(self._tree_model.rootPath(), file_name + self._file_suffix)
            while os.path.exists(file_path):
                file_name = default_file_name + str(file_name_index)
                file_name_index += 1
                file_path = os.path.join(self._tree_model.rootPath(), file_name + self._file_suffix)
            self._name_edit.setText(file_name + self._file_suffix)
            self._name_edit.setSelection(0, len(file_name))

        self.resize(600, 350)

    def _create_content_widgets(self, main_layout: QVBoxLayout):
        top_layout = QGridLayout()
        top_layout.addWidget(QLabel(gettext("Resource Name")), 0, 0)
        self._name_edit = QLineEdit()
        self._name_edit.textChanged.connect(self._on_name_changed)
        top_layout.addWidget(self._name_edit, 0, 1)
        back_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious), '')
        back_button.setDisabled(True)
        back_button.clicked.connect(self._back)
        self._back_button = back_button
        top_layout.addWidget(back_button, 0, 2)
        forward_button = QPushButton(QIcon.fromTheme(QIcon.ThemeIcon.GoNext), '')
        forward_button.setDisabled(True)
        forward_button.clicked.connect(self._forward)
        self._forward_button = forward_button
        top_layout.addWidget(forward_button, 0, 3)

        create_folder_button = QPushButton(gettext("Create Folder"))
        create_folder_button.clicked.connect(self._create_folder)
        top_layout.addWidget(create_folder_button, 0, 4)

        main_layout.addLayout(top_layout)

        tree_view = QTreeView()
        model = ProcessResourceModel()
        root_path = AppContext.app().app_package.path / "resources"
        if not root_path.is_dir():
            root_path.mkdir()
        model.setRootPath(str(root_path))
        model.setReadOnly(False)

        tree_view.setModel(model)
        tree_view.setRootIndex(model.index(str(root_path)))
        tree_view.setExpandsOnDoubleClick(False)
        tree_view.doubleClicked.connect(self._on_double_clicked)
        tree_view.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree_view.customContextMenuRequested.connect(self._on_context_menu_requested)
        tree_view.selectionModel().currentChanged.connect(self._on_current_changed)
        main_layout.addWidget(tree_view)
        self._tree_view = tree_view
        self._tree_model = model
        self._tree_view.setColumnWidth(0, 200)

    @Slot(str)
    def _on_name_changed(self, value: str):
        self._ok_button.setDisabled(value.strip() == '')

    @Slot(QModelIndex)
    def _on_current_changed(self, index):
        if not index.isValid() or self._tree_model.isDir(index):
            return
        file_path = self._tree_model.filePath(index)
        file_name = os.path.basename(file_path)
        if not file_name.lower().endswith(self._file_suffix):
            return
        self._name_edit.setText(file_name)

    def _back(self):
        if self._back_stack:
            self._forward_stack.append(self._tree_model.filePath(self._tree_view.rootIndex()))
            self._forward_button.setEnabled(True)
            self._tree_view.setRootIndex(self._tree_model.index(self._back_stack.pop()))
            if not self._back_stack:
                self._back_button.setDisabled(True)

    def _forward(self):
        if self._forward_stack:
            self._back_stack.append(self._tree_model.filePath(self._tree_view.rootIndex()))
            self._back_button.setEnabled(True)
            self._tree_view.setRootIndex(self._tree_model.index(self._forward_stack.pop()))
            if not self._forward_stack:
                self._forward_button.setDisabled(True)

    def _create_folder(self):
        folder_name = gettext('New Folder')
        parent = Path(self._tree_model.filePath(self._tree_view.rootIndex()))
        folder_path = parent / folder_name
        name_index = 1
        while folder_path.exists():
            folder_path = parent / (folder_name + str(name_index))
            name_index += 1
        folder_path.mkdir()
        self._tree_view.edit(self._tree_model.index(str(folder_path)))

    @Slot(QPoint)
    def _on_context_menu_requested(self, pos: QPoint):
        index = self._tree_view.indexAt(pos)
        if not index.isValid() or not self._tree_model.isDir(index):
            return
        context_menu = QMenu(self)
        rename_action = context_menu.addAction(gettext("Rename"))
        rename_action.triggered.connect(lambda: self._rename_folder(index))
        context_menu.exec(self._tree_view.mapToGlobal(pos))

    def _rename_folder(self, index: QModelIndex):
        self._tree_view.edit(index)

    def _on_double_clicked(self, index):
        self._back_stack.append(self._tree_model.filePath(self._tree_view.rootIndex()))
        self._forward_stack.clear()
        self._back_button.setEnabled(True)
        self._forward_button.setDisabled(True)
        if self._tree_model.isDir(index):
            self._tree_view.setRootIndex(index)
        else:
            self.accepted_value = os.path.relpath(self._tree_model.filePath(index),
                                                  self._tree_model.rootPath())
            self.accept()

    @Slot()
    def accept(self):
        file_name = self._name_edit.text().strip()
        if not file_name.lower().endswith(self._file_suffix):
            file_name += self._file_suffix
        file_path = Path(self._tree_model.filePath(self._tree_view.rootIndex())) / file_name
        if file_path.exists():
            if QMessageBox.question(self, gettext("Overwrite"),
                                    gettext("The file already exists, do you want to overwrite it?"),
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No:
                return
        self.accepted_value = os.path.relpath(file_path, self._tree_model.rootPath())
        super().accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = SaveProcessResourceDialog()
    widget.show()
    sys.exit(app.exec())
