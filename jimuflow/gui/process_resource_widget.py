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

import os
import shutil
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeView, QFileSystemModel, QFileDialog, \
    QMenu

from jimuflow.common.fs import copy_folder_overwrite, move_folder_overwrite
from jimuflow.gui.app import App
from jimuflow.locales.i18n import gettext


class ProcessResourceModel(QFileSystemModel):
    def dropMimeData(self, data, action, row, column, parent):
        if not parent.isValid() or self.isReadOnly():
            return False
        to = Path(self.filePath(parent))
        urls = data.urls()
        for url in urls:
            from_path = Path(url.toLocalFile())
            new_path = to / from_path.name
            if from_path == new_path:
                continue
            if from_path.is_file():
                new_path.parent.mkdir(exist_ok=True)
                if action == Qt.DropAction.MoveAction:
                    shutil.move(from_path, new_path)
                else:
                    shutil.copy(from_path, new_path)
            else:
                if action == Qt.DropAction.MoveAction:
                    move_folder_overwrite(from_path, new_path)
                else:
                    copy_folder_overwrite(from_path, new_path)
        return True

    def supportedDragActions(self):
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole or orientation != Qt.Orientation.Horizontal:
            return super().headerData(section, orientation, role)
        if section == 0:
            return gettext("Name")
        elif section == 1:
            return gettext("Size")
        elif section == 2:
            return gettext("Type")
        elif section == 3:
            return gettext("Date Modified")


class ProcessResourceWidget(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        add_file_action = QAction(gettext("Add File"))
        add_file_action.triggered.connect(self._add_file)
        self._add_file_action = add_file_action

        add_folder_action = QAction(gettext("Add Folder"))
        add_folder_action.triggered.connect(self._add_folder)
        self._add_folder_action = add_folder_action

        add_button = QPushButton(gettext("Add"))
        add_menu = QMenu(add_button)
        add_menu.addAction(add_file_action)
        add_menu.addAction(add_folder_action)
        add_button.setMenu(add_menu)
        add_button.setDisabled(True)
        self._add_button = add_button

        delete_button = QPushButton(gettext("Delete"))
        delete_button.clicked.connect(self._delete_selected_files)
        delete_button.setDisabled(True)
        self._delete_button = delete_button
        open_folder_button = QPushButton(gettext("Resource Folder"))
        open_folder_button.clicked.connect(self._open_resources_folder)
        open_folder_button.setDisabled(True)
        open_folder_button.setToolTip(gettext("Open resources folder in Finder"))
        self._open_folder_button = open_folder_button
        top_layout.addWidget(add_button)
        top_layout.addWidget(delete_button)
        top_layout.addWidget(open_folder_button)
        main_layout.addLayout(top_layout)
        tree_view = QTreeView()
        tree_view.setAcceptDrops(True)
        tree_view.setDragEnabled(True)
        tree_view.setDropIndicatorShown(True)
        tree_view.setDefaultDropAction(Qt.DropAction.MoveAction)
        main_layout.addWidget(tree_view)
        self._tree_view = tree_view
        self._app = None

    def set_app(self, app: App):
        self._app = app
        if app is None:
            self._tree_view.setModel(None)
            self._add_button.setDisabled(True)
            self._delete_button.setDisabled(True)
            self._open_folder_button.setDisabled(True)
            return
        model = ProcessResourceModel()
        model.setReadOnly(False)
        root_path = app.app_package.path / "resources"
        if not root_path.is_dir():
            root_path.mkdir()
        model.setRootPath(str(root_path))
        self._tree_view.setModel(model)
        self._tree_view.setRootIndex(model.index(str(root_path)))
        self._add_button.setDisabled(False)
        self._delete_button.setDisabled(False)
        self._open_folder_button.setDisabled(False)
        self._tree_view.setColumnWidth(0, 160)

    @Slot()
    def _add_file(self):
        file, _ = QFileDialog.getOpenFileName(self)
        if file:
            dest = self._app.app_package.path / "resources" / Path(file).name
            dest.parent.mkdir(exist_ok=True)
            shutil.copy(file, dest)

    @Slot()
    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self)
        if folder:
            dest = self._app.app_package.path / "resources" / Path(folder).name
            dest.parent.mkdir(exist_ok=True)
            move_folder_overwrite(folder, dest)

    @Slot()
    def _delete_selected_files(self):
        model = self._tree_view.model()
        for index in self._tree_view.selectedIndexes():
            if index.column() != 0:
                continue
            path = model.filePath(index)
            if Path(path).is_file():
                Path(path).unlink()
            else:
                shutil.rmtree(path)

    @Slot()
    def _open_resources_folder(self):
        path = str(self._app.app_package.path / "resources")
        if os.name == 'nt':  # Windows
            subprocess.run(['explorer', path])
        elif os.name == 'posix':  # macOS or Linux
            subprocess.run(['open', path])  # macOS
