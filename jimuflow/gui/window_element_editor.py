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

from PySide6.QtCore import Signal, Slot, QModelIndex
from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, \
    QButtonGroup, QSplitter, QTableView, QTextEdit, QCheckBox, QFrame, QDialog, QDialogButtonBox

from jimuflow.common.web_element_utils import build_xpath
from jimuflow.components.core.os_utils import is_windows
from jimuflow.gui.web_element_attributes_table import WebElementAttributesTable
from jimuflow.gui.web_element_editor import NodePathModel
from jimuflow.locales.i18n import gettext


class WindowElementEditor(QWidget):
    check_element_clicked = Signal()
    capture_element_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._element_info = None
        self._init_ui()
        self.setMinimumWidth(800)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        line1_layout = QHBoxLayout()
        line1_layout.addWidget(QLabel(gettext('Element Name')))
        self._element_name_edit = QLineEdit()
        self._element_name_edit.editingFinished.connect(self._on_element_name_editing_finished)
        line1_layout.addWidget(self._element_name_edit)
        if is_windows():
            capture_button = QPushButton(gettext('Capture Element'))
            capture_button.clicked.connect(self.capture_element_clicked)
            line1_layout.addWidget(capture_button)
            check_button = QPushButton(gettext('Check Element'))
            check_button.clicked.connect(self.check_element_clicked)
            line1_layout.addWidget(check_button)
        main_layout.addLayout(line1_layout)
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_edit_widget(), gettext('Element Editing'))
        self._preview_label = QLabel()
        self._preview_label.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        tab_widget.addTab(self._preview_label, gettext('Element Preview'))
        main_layout.addWidget(tab_widget)

    def _create_edit_widget(self):
        edit_widget = QWidget()
        main_layout = QVBoxLayout(edit_widget)
        top_layout = QHBoxLayout()
        switch_button_layout = QHBoxLayout()
        switch_button_group = QButtonGroup()
        self._switch_button_group = switch_button_group
        element_button = QPushButton(gettext('Element'))
        element_button.setCheckable(True)
        element_button.setChecked(True)
        window_button = QPushButton(gettext('Window'))
        window_button.setCheckable(True)
        switch_button_group.addButton(element_button, 1)
        switch_button_group.addButton(window_button, 2)
        switch_button_group.setExclusive(True)
        switch_button_group.idClicked.connect(self._on_switch_button_clicked)
        switch_button_layout.addWidget(element_button)
        switch_button_layout.addWidget(window_button)
        top_layout.addLayout(switch_button_layout)
        top_layout.addStretch(1)
        custom_element_xpath_checkbox = QCheckBox(gettext('Use Custom Element XPath'))
        custom_element_xpath_checkbox.clicked.connect(self._on_custom_element_xpath_checkbox_clicked)
        self._custom_element_xpath_checkbox = custom_element_xpath_checkbox
        top_layout.addWidget(custom_element_xpath_checkbox)
        custom_window_xpath_checkbox = QCheckBox(gettext('Use Custom Window XPath'))
        custom_window_xpath_checkbox.clicked.connect(self._on_custom_window_xpath_checkbox_clicked)
        custom_window_xpath_checkbox.setVisible(False)
        self._custom_window_xpath_checkbox = custom_window_xpath_checkbox
        top_layout.addWidget(custom_window_xpath_checkbox)
        main_layout.addLayout(top_layout)

        element_path_splitter = QSplitter()
        element_node_view = QTableView()
        element_node_view.verticalHeader().hide()
        element_node_model = NodePathModel([], self)
        element_node_model.dataChanged.connect(self._on_element_node_model_data_changed)
        element_node_view.setModel(element_node_model)
        element_node_view.selectionModel().currentRowChanged.connect(self._on_current_element_node_changed)
        # element_node_view.horizontalHeader().resizeSection(0, 250)
        element_node_view.horizontalHeader().setStretchLastSection(True)
        element_path_splitter.addWidget(element_node_view)
        self._element_node_view = element_node_view
        element_attr_table = WebElementAttributesTable()
        element_attr_table.attributes_edited.connect(self._on_current_element_node_attributes_edited)
        element_path_splitter.addWidget(element_attr_table)
        element_path_splitter.setSizes([250, 480])
        self._element_attr_table = element_attr_table
        self._element_path_splitter = element_path_splitter
        main_layout.addWidget(element_path_splitter)
        self._element_xpath_preview_label = QLabel(gettext("Element XPath Preview:"))
        self._element_xpath_preview_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._element_xpath_preview_label.setWordWrap(True)
        main_layout.addWidget(self._element_xpath_preview_label)

        window_path_splitter = QSplitter()
        window_path_splitter.setVisible(False)
        window_node_view = QTableView()
        window_node_view.verticalHeader().hide()
        window_node_model = NodePathModel([], self)
        window_node_model.dataChanged.connect(self._on_window_node_model_data_changed)
        window_node_view.setModel(window_node_model)
        window_node_view.selectionModel().currentRowChanged.connect(self._on_current_window_node_changed)
        window_node_view.horizontalHeader().resizeSection(0, 250)
        window_path_splitter.addWidget(window_node_view)
        self._window_node_view = window_node_view
        window_attr_table = WebElementAttributesTable()
        window_attr_table.attributes_edited.connect(self._on_current_window_node_attributes_edited)
        window_path_splitter.addWidget(window_attr_table)
        window_path_splitter.setSizes([250, 480])
        self._window_attr_table = window_attr_table
        self._window_path_splitter = window_path_splitter
        main_layout.addWidget(window_path_splitter)
        self._window_xpath_preview_label = QLabel(gettext("Element XPath Preview:"))
        self._window_xpath_preview_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._window_xpath_preview_label.setWordWrap(True)
        self._window_xpath_preview_label.setVisible(False)
        main_layout.addWidget(self._window_xpath_preview_label)

        custom_element_xpath_edit = QTextEdit()
        custom_element_xpath_edit.setPlaceholderText(gettext('Enter Custom Element XPath'))
        custom_element_xpath_edit.setVisible(False)
        self._custom_element_xpath_edit = custom_element_xpath_edit
        main_layout.addWidget(custom_element_xpath_edit)

        self._custom_window_xpath_edit = QTextEdit()
        self._custom_window_xpath_edit.setPlaceholderText(gettext('Enter Custom Window XPath'))
        self._custom_window_xpath_edit.setVisible(False)
        main_layout.addWidget(self._custom_window_xpath_edit)

        return edit_widget

    @Slot(int)
    def _on_switch_button_clicked(self, id):
        if id == 1:
            # 隐藏window编辑相关界面
            self._custom_window_xpath_checkbox.setVisible(False)
            self._window_path_splitter.setVisible(False)
            self._window_xpath_preview_label.setVisible(False)
            self._custom_window_xpath_edit.setVisible(False)
            # 显示元素编辑相关界面
            self._custom_element_xpath_checkbox.setVisible(True)
            if self._custom_element_xpath_checkbox.isChecked():
                # 自定义元素路径
                self._custom_element_xpath_edit.setVisible(True)
                self._element_path_splitter.setVisible(False)
                self._element_xpath_preview_label.setVisible(False)
            else:
                # 编辑元素路径
                self._custom_element_xpath_edit.setVisible(False)
                self._element_path_splitter.setVisible(True)
                self._element_xpath_preview_label.setVisible(True)
        else:
            # 隐藏元素编辑相关界面
            self._custom_element_xpath_checkbox.setVisible(False)
            self._element_path_splitter.setVisible(False)
            self._element_xpath_preview_label.setVisible(False)
            self._custom_element_xpath_edit.setVisible(False)
            # 显示window编辑相关界面
            self._custom_window_xpath_checkbox.setVisible(True)
            if self._custom_window_xpath_checkbox.isChecked():
                # 自定义window路径
                self._window_path_splitter.setVisible(False)
                self._custom_window_xpath_edit.setVisible(True)
                self._window_xpath_preview_label.setVisible(False)
            else:
                # 编辑window路径
                self._window_path_splitter.setVisible(True)
                self._custom_window_xpath_edit.setVisible(False)
                self._window_xpath_preview_label.setVisible(True)

    @Slot()
    def _on_custom_element_xpath_checkbox_clicked(self):
        # 元素编辑模式
        if self._custom_element_xpath_checkbox.isChecked():
            # 自定义元素路径
            self._custom_element_xpath_edit.setVisible(True)
            self._element_path_splitter.setVisible(False)
            self._element_xpath_preview_label.setVisible(False)
        else:
            # 编辑元素路径
            self._custom_element_xpath_edit.setVisible(False)
            self._element_path_splitter.setVisible(True)
            self._element_xpath_preview_label.setVisible(True)

    @Slot()
    def _on_custom_window_xpath_checkbox_clicked(self):
        # window编辑模式
        if self._custom_window_xpath_checkbox.isChecked():
            # 自定义window路径
            self._window_path_splitter.setVisible(False)
            self._custom_window_xpath_edit.setVisible(True)
            self._window_xpath_preview_label.setVisible(False)
        else:
            # 编辑window路径
            self._window_path_splitter.setVisible(True)
            self._custom_window_xpath_edit.setVisible(False)
            self._window_xpath_preview_label.setVisible(True)

    @Slot(QModelIndex, QModelIndex)
    def _on_current_element_node_changed(self, current: QModelIndex, previous: QModelIndex):
        node = current.internalPointer()
        self._element_attr_table.set_attributes(node["predicates"])

    @Slot()
    def _on_current_element_node_attributes_edited(self):
        index = self._element_node_view.currentIndex()
        index.model().dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

    @Slot(QModelIndex, QModelIndex, list)
    def _on_element_node_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list):
        self._element_info['elementXPath'] = build_xpath(self._element_info['elementPath'])
        self._update_element_xpath_preview()

    def _update_element_xpath_preview(self):
        self._element_xpath_preview_label.setText(
            gettext("Element XPath Preview: \n{}").format(self._element_info['elementXPath']))

    @Slot(QModelIndex, QModelIndex)
    def _on_current_window_node_changed(self, current: QModelIndex, previous: QModelIndex):
        node = current.internalPointer()
        self._window_attr_table.set_attributes(node["predicates"])

    @Slot()
    def _on_current_window_node_attributes_edited(self):
        index = self._window_node_view.currentIndex()
        index.model().dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

    @Slot(QModelIndex, QModelIndex, list)
    def _on_window_node_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list):
        self._element_info['windowXPath'] = build_xpath(self._element_info['windowPath'])
        self._update_window_xpath_preview()

    def _update_window_xpath_preview(self):
        self._window_xpath_preview_label.setText(
            gettext("Window XPath Preview: \n{}").format(self._element_info['windowXPath']))

    @Slot()
    def _on_element_name_editing_finished(self):
        self._element_info['name'] = self._element_name_edit.text()

    def set_element_info(self, element_info: dict):
        self._element_info = element_info
        self._element_name_edit.setText(element_info['name'])
        element_node_model: NodePathModel = self._element_node_view.model()
        element_node_model.set_node_path(element_info['elementPath'])
        self._custom_element_xpath_edit.setText(element_info['elementXPath'])
        self._update_element_xpath_preview()
        window_node_model: NodePathModel = self._window_node_view.model()
        window_node_model.set_node_path(element_info['windowPath'])
        self._update_window_xpath_preview()
        self._custom_window_xpath_edit.setText(element_info['windowXPath'])
        self._custom_element_xpath_checkbox.setChecked(element_info['useCustomElementXPath'])
        self._custom_window_xpath_checkbox.setChecked(element_info['useCustomWindowXPath'])
        if self._switch_button_group.checkedId() == 1:
            self._on_custom_element_xpath_checkbox_clicked()
        else:
            self._on_custom_window_xpath_checkbox_clicked()
        self._show_element_preview()
        if element_info['elementPath']:
            self._element_node_view.setCurrentIndex(element_node_model.index(element_node_model.rowCount() - 1, 0))
        if element_info['windowPath']:
            self._window_node_view.setCurrentIndex(window_node_model.index(window_node_model.rowCount() - 1, 0))

    def _show_element_preview(self):
        if self._element_info["snapshot"]:
            pixmap = QPixmap(self._element_info["snapshot"])
            if pixmap.isNull():
                self._preview_label.setPixmap(QPixmap())
            else:
                label_size = self._preview_label.size()
                pixmap_size = pixmap.size()
                if label_size.width() >= pixmap_size.width() and label_size.height() >= pixmap_size.height():
                    self._preview_label.setPixmap(pixmap)
                else:
                    self._preview_label.setPixmap(
                        pixmap.scaled(label_size, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self._preview_label.setPixmap(QPixmap())


class WindowElementEditorDialog(QDialog):
    def __init__(self, element_info: dict, parent=None):
        super().__init__(parent)
        self.element_info = element_info
        main_layout = QVBoxLayout(self)
        self._element_editor = WindowElementEditor()
        main_layout.addWidget(self._element_editor)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        main_layout.addWidget(button_box)
        self._element_editor.set_element_info(element_info)
