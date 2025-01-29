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

from PySide6.QtCore import Signal, QModelIndex, Slot, QSortFilterProxyModel, QPoint, QSize
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt, QIcon
from PySide6.QtWidgets import QListView, QLineEdit, QVBoxLayout, QWidget, QMenu

from jimuflow.definition import ProcessDef
from jimuflow.gui.app import App
from jimuflow.locales.i18n import gettext


class AppProcessListView(QWidget):
    open_process_def = Signal(ProcessDef)
    config_process_def_requested = Signal(ProcessDef)
    delete_process_def_requested = Signal(ProcessDef)

    def __init__(self):
        super().__init__()
        self._main_process_icon = QIcon.fromTheme(QIcon.ThemeIcon.GoHome)
        self.app: App | None = None
        self._list_model = QStandardItemModel(self)
        self._list_proxy_model = QSortFilterProxyModel(self)
        self._list_proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._list_proxy_model.setSourceModel(self._list_model)
        self._list_view = QListView()
        self._list_view.setIconSize(QSize(16, 16))
        self._list_view.setModel(self._list_proxy_model)
        self._list_view.doubleClicked.connect(self.on_double_clicked)
        self._list_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list_view.customContextMenuRequested.connect(self._on_context_menu_requested)
        self._keyword_edit = QLineEdit()
        self._keyword_edit.setPlaceholderText(gettext("Search process"))
        self._keyword_edit.textChanged.connect(self._search)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._keyword_edit)
        layout.addWidget(self._list_view)

    def set_app(self, app: App | None):
        if self.app:
            self.app.process_def_files_changed.disconnect(self.reload_process_files)
            self.app.main_process_changed.disconnect(self._on_main_process_changed)
        self._keyword_edit.setText("")
        self.app = app
        self.reload_process_files()
        if self.app:
            self.app.process_def_files_changed.connect(self.reload_process_files)
            self.app.main_process_changed.connect(self._on_main_process_changed)

    @Slot(str)
    def _search(self, keyword):
        self._list_proxy_model.setFilterFixedString(keyword)

    @Slot()
    def reload_process_files(self):
        self._list_model.clear()
        if not self.app:
            return
        for process_def in self.app.get_all_process_defs():
            item = QStandardItem(process_def.name)
            item.setData(process_def, Qt.ItemDataRole.UserRole)
            item.setData(gettext('Double click to open the process'), Qt.ItemDataRole.ToolTipRole)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            if self.app.is_main_process_def(process_def.name):
                item.setIcon(self._main_process_icon)
            self._list_model.appendRow([item])

    @Slot(str, str)
    def _on_main_process_changed(self, old_name: str, current_name: str):
        for i in range(self._list_model.rowCount()):
            item = self._list_model.item(i)
            if item.text() == old_name:
                item.setIcon(QIcon())
            elif item.text() == current_name:
                item.setIcon(self._main_process_icon)

    @Slot(QModelIndex)
    def on_double_clicked(self, index: QModelIndex):
        process_def = index.data(Qt.ItemDataRole.UserRole)
        self.open_process_def.emit(process_def)

    @Slot(QPoint)
    def _on_context_menu_requested(self, pos):
        index = self._list_view.indexAt(pos)
        if not index.isValid():
            return
        process_def = index.data(Qt.ItemDataRole.UserRole)
        context_menu = QMenu(self)
        open_action = context_menu.addAction(gettext("Open"))
        open_action.triggered.connect(lambda: self.open_process_def.emit(process_def))
        if not self.app.is_main_process_def(process_def.name):
            set_main_process_action = context_menu.addAction(gettext("Set As Main Process"))
            set_main_process_action.triggered.connect(lambda: self._set_main_process(process_def))
        config_action = context_menu.addAction(gettext("Config"))
        config_action.triggered.connect(lambda: self.config_process_def_requested.emit(process_def))
        remove_action = context_menu.addAction(gettext("Remove"))
        remove_action.triggered.connect(lambda: self.delete_process_def_requested.emit(process_def))
        context_menu.exec(self._list_view.mapToGlobal(pos))

    def _set_main_process(self, process_def: ProcessDef):
        self.app.set_main_process_def(process_def.name)
