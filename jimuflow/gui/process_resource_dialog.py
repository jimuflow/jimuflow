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

from PySide6.QtCore import Slot, QModelIndex
from PySide6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QTreeView

from jimuflow.gui.app import AppContext
from jimuflow.gui.process_resource_widget import ProcessResourceModel
from jimuflow.locales.i18n import gettext


class ProcessResourceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_resource = None
        self.setWindowTitle("Resource")
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
        self._selected_resource = os.path.relpath(self._tree_model.filePath(index),
                                                  self._tree_model.rootPath())
        self.accept()

    @Slot()
    def _on_ok(self):
        selected_indexes = self._tree_view.selectedIndexes()
        if len(selected_indexes) > 0:
            self._selected_resource = os.path.relpath(self._tree_model.filePath(selected_indexes[0]),
                                                      self._tree_model.rootPath())
        else:
            self._selected_resource = None
        self.accept()
