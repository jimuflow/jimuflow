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

from PySide6.QtCore import Signal, Slot, QModelIndex, QAbstractItemModel
from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, \
    QButtonGroup, QSplitter, QTableView, QTextEdit, QCheckBox, QFrame

from jimuflow.common.web_element_utils import build_node_xpath, build_xpath
from jimuflow.gui.web_element_attributes_table import WebElementAttributesTable
from jimuflow.locales.i18n import gettext


class NodePathModel(QAbstractItemModel):
    def __init__(self, node_path: list, parent=None):
        super().__init__(parent)
        self._node_path = node_path
        self._headers = [gettext('Element Node')]

    def set_node_path(self, node_path: list):
        self.beginResetModel()
        self._node_path = node_path
        self.endResetModel()

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        node = self._node_path[row]
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return build_node_xpath(node)
        elif role == Qt.ItemDataRole.CheckStateRole:
            return Qt.CheckState.Checked if node['enabled'] else Qt.CheckState.Unchecked

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False
        column = index.column()
        if column == 0 and role == Qt.ItemDataRole.CheckStateRole:
            row = index.row()
            node = self._node_path[row]
            node['enabled'] = value == Qt.CheckState.Checked.value
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        else:
            return len(self._node_path)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        return self.createIndex(row, column, self._node_path[row])

    def parent(self, index: QModelIndex):
        return QModelIndex()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() == 0:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags


class WebElementEditor(QWidget):
    check_element_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._element_info = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        line1_layout = QHBoxLayout()
        line1_layout.addWidget(QLabel(gettext('Element Name')))
        self._element_name_edit = QLineEdit()
        self._element_name_edit.editingFinished.connect(self._on_element_name_editing_finished)
        line1_layout.addWidget(self._element_name_edit)
        check_button = QPushButton(gettext('Check Element'))
        check_button.clicked.connect(self.check_element_clicked)
        line1_layout.addWidget(check_button)
        main_layout.addLayout(line1_layout)
        tab_widget = QTabWidget()
        tab_widget.addTab(self._create_edit_widget(), gettext('Element Editing'))
        self._preview_label = QLabel()
        self._preview_label.resize(200, 400)
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
        iframe_button = QPushButton(gettext('IFrame'))
        iframe_button.setCheckable(True)
        switch_button_group.addButton(element_button, 1)
        switch_button_group.addButton(iframe_button, 2)
        switch_button_group.setExclusive(True)
        switch_button_group.idClicked.connect(self._on_switch_button_clicked)
        switch_button_layout.addWidget(element_button)
        switch_button_layout.addWidget(iframe_button)
        top_layout.addLayout(switch_button_layout)
        top_layout.addStretch(1)
        custom_element_xpath_checkbox = QCheckBox(gettext('Use Custom Element XPath'))
        custom_element_xpath_checkbox.clicked.connect(self._on_custom_element_xpath_checkbox_clicked)
        self._custom_element_xpath_checkbox = custom_element_xpath_checkbox
        top_layout.addWidget(custom_element_xpath_checkbox)
        custom_iframe_xpath_checkbox = QCheckBox(gettext('Use Custom IFrame XPath'))
        custom_iframe_xpath_checkbox.clicked.connect(self._on_custom_iframe_xpath_checkbox_clicked)
        custom_iframe_xpath_checkbox.setVisible(False)
        self._custom_iframe_xpath_checkbox = custom_iframe_xpath_checkbox
        top_layout.addWidget(custom_iframe_xpath_checkbox)
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

        iframe_path_splitter = QSplitter()
        iframe_path_splitter.setVisible(False)
        iframe_node_view = QTableView()
        iframe_node_view.verticalHeader().hide()
        iframe_node_model = NodePathModel([], self)
        iframe_node_model.dataChanged.connect(self._on_iframe_node_model_data_changed)
        iframe_node_view.setModel(iframe_node_model)
        iframe_node_view.selectionModel().currentRowChanged.connect(self._on_current_iframe_node_changed)
        # iframe_node_view.horizontalHeader().resizeSection(0, 250)
        iframe_node_view.horizontalHeader().setStretchLastSection(True)
        iframe_path_splitter.addWidget(iframe_node_view)
        self._iframe_node_view = iframe_node_view
        iframe_attr_table = WebElementAttributesTable()
        iframe_attr_table.attributes_edited.connect(self._on_current_iframe_node_attributes_edited)
        iframe_path_splitter.addWidget(iframe_attr_table)
        iframe_path_splitter.setSizes([250, 480])
        self._iframe_attr_table = iframe_attr_table
        self._iframe_path_splitter = iframe_path_splitter
        main_layout.addWidget(iframe_path_splitter)
        self._iframe_xpath_preview_label = QLabel(gettext("Element XPath Preview:"))
        self._iframe_xpath_preview_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._iframe_xpath_preview_label.setWordWrap(True)
        self._iframe_xpath_preview_label.setVisible(False)
        main_layout.addWidget(self._iframe_xpath_preview_label)

        custom_element_xpath_edit = QTextEdit()
        custom_element_xpath_edit.setPlaceholderText(gettext('Enter Custom Element XPath'))
        custom_element_xpath_edit.setVisible(False)
        self._custom_element_xpath_edit = custom_element_xpath_edit
        main_layout.addWidget(custom_element_xpath_edit)

        element_in_iframe_checkbox = QCheckBox(gettext('Element in IFrame'))
        element_in_iframe_checkbox.setVisible(False)
        element_in_iframe_checkbox.clicked.connect(self._on_element_in_iframe_checkbox_clicked)
        self._element_in_iframe_checkbox = element_in_iframe_checkbox
        main_layout.addWidget(element_in_iframe_checkbox)
        self._custom_iframe_xpath_edit = QTextEdit()
        self._custom_iframe_xpath_edit.setPlaceholderText(gettext('Enter Custom IFrame XPath'))
        self._custom_iframe_xpath_edit.setVisible(False)
        main_layout.addWidget(self._custom_iframe_xpath_edit)

        return edit_widget

    @Slot(int)
    def _on_switch_button_clicked(self, id):
        if id == 1:
            # 隐藏iframe编辑相关界面
            self._custom_iframe_xpath_checkbox.setVisible(False)
            self._iframe_path_splitter.setVisible(False)
            self._iframe_xpath_preview_label.setVisible(False)
            self._element_in_iframe_checkbox.setVisible(False)
            self._custom_iframe_xpath_edit.setVisible(False)
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
            # 显示iframe编辑相关界面
            self._custom_iframe_xpath_checkbox.setVisible(True)
            if self._custom_iframe_xpath_checkbox.isChecked():
                # 自定义iframe路径
                self._iframe_path_splitter.setVisible(False)
                self._element_in_iframe_checkbox.setVisible(True)
                self._custom_iframe_xpath_edit.setVisible(True)
                self._iframe_xpath_preview_label.setVisible(False)
            else:
                # 编辑iframe路径
                self._iframe_path_splitter.setVisible(True)
                self._element_in_iframe_checkbox.setVisible(False)
                self._custom_iframe_xpath_edit.setVisible(False)
                self._iframe_xpath_preview_label.setVisible(True)

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
    def _on_custom_iframe_xpath_checkbox_clicked(self):
        # iframe编辑模式
        if self._custom_iframe_xpath_checkbox.isChecked():
            # 自定义iframe路径
            self._iframe_path_splitter.setVisible(False)
            self._element_in_iframe_checkbox.setVisible(True)
            self._custom_iframe_xpath_edit.setVisible(self._element_in_iframe_checkbox.isChecked())
            self._iframe_xpath_preview_label.setVisible(False)
        else:
            # 编辑iframe路径
            self._iframe_path_splitter.setVisible(True)
            self._element_in_iframe_checkbox.setVisible(False)
            self._custom_iframe_xpath_edit.setVisible(False)
            self._iframe_xpath_preview_label.setVisible(True)

    @Slot()
    def _on_element_in_iframe_checkbox_clicked(self):
        self._custom_iframe_xpath_edit.setVisible(self._element_in_iframe_checkbox.isChecked())

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
    def _on_current_iframe_node_changed(self, current: QModelIndex, previous: QModelIndex):
        node = current.internalPointer()
        self._iframe_attr_table.set_attributes(node["predicates"])

    @Slot()
    def _on_current_iframe_node_attributes_edited(self):
        index = self._iframe_node_view.currentIndex()
        index.model().dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])

    @Slot(QModelIndex, QModelIndex, list)
    def _on_iframe_node_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list):
        self._element_info['iframeXPath'] = build_xpath(self._element_info['iframePath'])
        self._update_iframe_xpath_preview()

    def _update_iframe_xpath_preview(self):
        self._iframe_xpath_preview_label.setText(
            gettext("IFrame XPath Preview: \n{}").format(self._element_info['iframeXPath']))

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
        iframe_node_model: NodePathModel = self._iframe_node_view.model()
        iframe_node_model.set_node_path(element_info['iframePath'])
        self._update_iframe_xpath_preview()
        self._custom_iframe_xpath_edit.setText(element_info['iframeXPath'])
        self._custom_element_xpath_checkbox.setChecked(element_info['useCustomElementXPath'])
        self._custom_iframe_xpath_checkbox.setChecked(element_info['useCustomIframeXPath'])
        self._element_in_iframe_checkbox.setChecked(element_info['inIframe'])
        if self._switch_button_group.checkedId() == 1:
            self._on_custom_element_xpath_checkbox_clicked()
        else:
            self._on_custom_iframe_xpath_checkbox_clicked()
        self._show_element_preview()
        if element_info['elementPath']:
            self._element_node_view.setCurrentIndex(element_node_model.index(element_node_model.rowCount() - 1, 0))
        if element_info['iframePath']:
            self._iframe_node_view.setCurrentIndex(iframe_node_model.index(iframe_node_model.rowCount() - 1, 0))

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
