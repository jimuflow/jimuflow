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

import tempfile
from pathlib import Path

from PySide6.QtCore import QModelIndex, Slot, QPoint, Signal
from PySide6.QtGui import QIcon, Qt, QPixmap, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeView, QDialog, QMenu, QLabel, QFrame

from jimuflow.common.uri_utils import build_web_element_uri
from jimuflow.gui.app import App, AppContext
from jimuflow.gui.web_element_capture_tool import WebElementCaptureTool
from jimuflow.locales.i18n import gettext


class CaptureElementButton(QPushButton):
    element_added = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText(gettext("Capture Element"))
        self.clicked.connect(self._capture_element)

    @Slot()
    def _capture_element(self):
        tool = WebElementCaptureTool()
        if tool.exec_until_closed() == QDialog.DialogCode.Accepted and tool.element_info:
            element_info = tool.element_info
            app_package = AppContext.app().app_package
            group_icon: QIcon = element_info["groupIcon"]
            group_icon_path = None
            if group_icon and not group_icon.isNull():
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as icon_file:
                    group_icon.pixmap(group_icon.availableSizes()[0]).save(icon_file.name)
                    group_icon_path = Path(icon_file.name)
            group_name, group_icon = app_package.add_web_element_group(element_info["groupName"], group_icon_path)
            element_id = app_package.add_web_element(group_name, element_info, Path(element_info['snapshot']))
            model = AppContext.app().web_elements_model
            for group_row in range(model.rowCount()):
                group_item = model.item(group_row)
                if group_item.text() == group_name:
                    break
            else:
                group_item = QStandardItem(group_name)
                if group_icon:
                    group_item.setIcon(QIcon(group_icon))
                group_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                model.appendRow(group_item)
            element_item = QStandardItem(element_info["name"])
            element_item.setIcon(AppContext.app().element_icon)
            element_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            element_item.setData(element_id, Qt.ItemDataRole.UserRole)
            element_info['id'] = element_id
            element_item.setData(build_web_element_uri(element_info), Qt.ItemDataRole.UserRole + 1)
            group_item.appendRow(element_item)
            self.element_added.emit(element_id)


class ElementsWidget(QWidget):
    """
    元素库组件
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._app: App | None = None
        main_layout = QVBoxLayout(self)
        buttons_layout = QHBoxLayout()
        capture_element_button = CaptureElementButton()
        capture_element_button.element_added.connect(self._on_element_added)
        capture_element_button.setDisabled(True)
        buttons_layout.addWidget(capture_element_button)
        self._capture_element_button = capture_element_button
        main_layout.addLayout(buttons_layout)
        tree_view = QTreeView()
        tree_view.doubleClicked.connect(self._edit_element)
        tree_view.header().hide()
        tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree_view.customContextMenuRequested.connect(self._on_context_menu_requested)
        main_layout.addWidget(tree_view, 1)
        preview_label = QLabel()
        preview_label.setFrameShape(QFrame.Shape.StyledPanel)
        preview_label.setFrameShadow(QFrame.Shadow.Raised)
        preview_label.setMinimumHeight(100)
        main_layout.addWidget(preview_label)
        self._preview_label = preview_label
        self._tree_view = tree_view
        self._element_icon = QIcon(":/icons/web_element.png")

    def set_app(self, app: App):
        if not app:
            self._tree_view.setModel(None)
            self._capture_element_button.setDisabled(True)
            self._app = None
            return
        self._app = app
        self._tree_view.setModel(app.web_elements_model)
        self._tree_view.selectionModel().currentChanged.connect(self._on_current_changed)
        self._capture_element_button.setEnabled(True)
        self._tree_view.expandAll()

    @Slot(str)
    def _on_element_added(self, element_id):
        model: QStandardItemModel = self._tree_view.model()
        element_info = self._app.app_package.get_web_element_by_id(element_id)
        group_name = element_info['groupName']
        for group_row in range(model.rowCount()):
            group_item = model.item(group_row)
            if group_item.text() == group_name:
                break
        else:
            return
        group_index = group_item.index()
        element_index = model.index(group_item.rowCount() - 1, 0, group_index)
        self._tree_view.expand(group_index)
        self._tree_view.setCurrentIndex(element_index)
        self._tree_view.scrollTo(element_index)

    @Slot(QModelIndex)
    def _edit_element(self, index: QModelIndex):
        if not index.parent().isValid():
            return
        model: QStandardItemModel = self._tree_view.model()
        element_item = model.itemFromIndex(index)
        element_id = index.data(Qt.ItemDataRole.UserRole)
        app_package = self._app.app_package
        element_info = app_package.get_web_element_by_id(element_id)
        group_name = element_info['groupName']
        tool = WebElementCaptureTool(element_info=element_info, parent=self)
        if tool.exec_until_closed() == QDialog.DialogCode.Accepted and tool.element_info:
            element_info = tool.element_info
            app_package.update_web_element(group_name, element_id, element_info)
            element_item.setText(element_info['name'])

    def _remove_element(self, index: QModelIndex):
        element_id = index.data(Qt.ItemDataRole.UserRole)
        app_package = self._app.app_package
        element_info = app_package.get_web_element_by_id(element_id)
        group_name = element_info['groupName']
        app_package.remove_web_element(group_name, element_id)
        self._tree_view.model().removeRow(index.row(), index.parent())

    def _remove_group(self, index: QModelIndex):
        group_name = index.data(Qt.ItemDataRole.DisplayRole)
        app_package = self._app.app_package
        app_package.remove_web_element_group(group_name)
        self._tree_view.model().removeRow(index.row(), index.parent())

    @Slot(QPoint)
    def _on_context_menu_requested(self, pos):
        index = self._tree_view.indexAt(pos)
        if not index.isValid():
            return
        context_menu = QMenu(self)
        if index.parent().isValid():
            edit_action = context_menu.addAction(gettext("Edit Element"))
            edit_action.triggered.connect(lambda: self._edit_element(index))
            remove_action = context_menu.addAction(gettext("Remove"))
            remove_action.triggered.connect(lambda: self._remove_element(index))
        else:
            remove_action = context_menu.addAction(gettext("Remove"))
            remove_action.triggered.connect(lambda: self._remove_group(index))
        context_menu.exec(self._tree_view.mapToGlobal(pos))

    @Slot(QModelIndex, QModelIndex)
    def _on_current_changed(self, current: QModelIndex, previous: QModelIndex):
        if not current.isValid() or not current.parent().isValid():
            self._preview_label.clear()
            return
        element_id = current.data(Qt.ItemDataRole.UserRole)
        element_info = self._app.app_package.get_web_element_by_id(element_id)
        snapshot = element_info.get('snapshot', None)
        if not snapshot:
            self._preview_label.clear()
            return
        pixmap = QPixmap(snapshot)
        if pixmap.isNull():
            self._preview_label.clear()
            return
        pixmap_size = pixmap.size()
        label_size = self._preview_label.contentsRect().size()
        if pixmap_size.width() > label_size.width() or pixmap_size.height() > label_size.height():
            pixmap = pixmap.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
        self._preview_label.setPixmap(pixmap)
