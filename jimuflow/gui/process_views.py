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

import json

from PySide6.QtCore import QModelIndex, Slot, QItemSelectionModel, Qt, QUrl, QSize, QRect, QEvent, QTimer, \
    QItemSelection, Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction, QTextDocument, QPixmap, QPalette, QKeySequence, \
    QShortcut
from PySide6.QtWidgets import QTreeView, QDialog, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMenu, \
    QStyledItemDelegate, QStyle, QTableView, QAbstractItemView, QSizePolicy, QStylePainter, QMessageBox, QApplication, \
    QHeaderView

from jimuflow.common.mimetypes import mimetype_process_flow_nodes
from jimuflow.definition import FlowNode, ComponentDef, VariableDef, VariableDirection, ProcessDef
from jimuflow.definition.process_def import snapshot_flow_node, snapshot_flow_node_tree
from jimuflow.gui.app import ProcessModel, AppContext
from jimuflow.gui.component_dialog import ComponentDialog
from jimuflow.gui.create_variable import CreateVariableDialog
from jimuflow.gui.undo_redo_manager import Action
from jimuflow.locales.i18n import gettext


class RichTextDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # 获取数据
        text = self.item_rich_text(index)
        text = text.replace('$$NAME_COLOR$$', option.palette.text().color().name())
        if option.state & QStyle.State_Selected:
            text = text.replace('$$ROOT_STYLE$$', 'class="selected"')

        # 创建QTextDocument来处理富文本
        doc = self.create_document()
        doc.setHtml(text)

        # 设置文本文档的大小
        doc.setTextWidth(option.rect.width())

        # print(text, option.rect)

        # 保存 painter 的状态
        painter.save()

        # 如果项目被选中，绘制选中背景
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            bg_color = index.data(Qt.ItemDataRole.BackgroundRole)
            if bg_color:
                painter.fillRect(option.rect, bg_color)

        # 移动 painter 到目标矩形的左上角
        painter.translate(option.rect.topLeft())

        # 绘制文本
        painter.setClipRect(option.rect.translated(-option.rect.topLeft()))
        doc.drawContents(painter)

        # 恢复 painter 的状态
        painter.restore()

    def create_document(self):
        doc = QTextDocument()
        point_pixmap = QPixmap(':/icons/redpoint.png')
        doc.addResource(QTextDocument.ResourceType.ImageResource, QUrl("mydata://redpoint.png"), point_pixmap)
        return doc

    def item_rich_text(self, index):
        return index.data()

    def sizeHint(self, option, index):
        # 获取数据
        text = self.item_rich_text(index)

        # 创建QTextDocument来处理富文本
        doc = self.create_document()
        doc.setHtml(text)

        # 设置文本文档的宽度
        if index.column() == 0:
            depth = 0
            parent = index.parent()
            while parent.isValid():
                depth += 1
                parent = parent.parent()
            doc.setTextWidth(option.widget.columnWidth(0) - option.widget.indentation() * (depth + 1))
        else:
            doc.setTextWidth(option.widget.columnWidth(index.column()))

        # 返回文本文档的大小
        return doc.size().toSize()


class RecursiveSelectionModel(QItemSelectionModel):
    def select(self, selection: QItemSelection, mode: QItemSelectionModel.SelectionFlag):
        if isinstance(selection, QModelIndex):
            super().select(selection, mode)
        else:
            for index in selection.indexes():
                self.recursive_select(index, selection)
            super().select(selection, mode)

    def recursive_select(self, parent: QModelIndex, selection: QItemSelection):
        if not parent.isValid():
            return
        selection.select(parent, parent)
        model = self.model()
        row_count = model.rowCount(parent)
        for i in range(row_count):
            self.recursive_select(model.index(i, 0, parent), selection)


class ProcessFlowView(QTreeView):
    open_process_def = Signal(ProcessDef)

    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDropIndicatorShown(True)
        self.setHeaderHidden(True)
        self.setItemDelegate(RichTextDelegate())
        self.setUniformRowHeights(False)
        self.setExpandsOnDoubleClick(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.doubleClicked.connect(self.edit_node)
        self._create_actions()
        self._setup_shortcuts()

    def _setup_shortcuts(self):
        self._copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        self._copy_shortcut.activated.connect(self.copy_selected_nodes)

        self._cut_shortcut = QShortcut(QKeySequence.StandardKey.Cut, self)
        self._cut_shortcut.activated.connect(self.cut_selected_nodes)

        self._paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        self._paste_shortcut.activated.connect(self.paste_nodes_at_last)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.doItemsLayout()

    def setModel(self, model: ProcessModel):
        if self.model():
            self.model().component_dropped.disconnect(self.add_node)
            self.model().nodes_dropped.disconnect(self.drop_nodes)
        super().setModel(model)
        model.component_dropped.connect(self.add_node)
        model.nodes_dropped.connect(self.drop_nodes)

    @Slot(int, QModelIndex, ComponentDef)
    def add_node(self, row: int, parent: QModelIndex, comp_def: ComponentDef):
        model: ProcessModel = self.model()
        if any(v.direction != VariableDirection.LOCAL for v in comp_def.variables) or comp_def.supports_error_handling:
            comp_dialog = ComponentDialog(model, comp_def, parent=self)
            if comp_dialog.exec() == QDialog.DialogCode.Accepted:
                flow_node = comp_dialog.get_flow_node()
            else:
                return
        else:
            flow_node = {
                "component": comp_def.id(model.process_def.package),
                "inputs": {},
                "outputs": {}
            }
        outer_self = self
        parent_locator = model.index_locator(parent)

        class AddNodeAction(Action):
            def __init__(self, description):
                super().__init__(description)
                self._added_variables = []

            def execute(self):
                parent = model.locate_index(*parent_locator)
                model.insertRow(row, parent)
                index = model.index(row, 0, parent)
                model.setData(index, flow_node)
                self._added_variables = outer_self.add_variables_if_not_exist(index.internalPointer(), comp_def)
                model.update_line_no()

            def undo(self):
                if self._added_variables:
                    for var_def in self._added_variables:
                        var_def = model.process_def.get_variable(var_def.name)
                        model.remove_variable(var_def)
                parent = model.locate_index(*parent_locator)
                model.removeRow(row, parent)
                model.update_line_no()

        model.undo_redo_manager.perform_action(AddNodeAction(gettext("Add Instruction")))

    @Slot(Qt.DropAction, int, QModelIndex, dict)
    def drop_nodes(self, action: Qt.DropAction, row: int, parent: QModelIndex, nodes_data: dict):
        model: ProcessModel = self.model()
        outer_self = self
        parent_locator = model.index_locator(parent)

        class DropNodesAction(Action):
            def __init__(self, description):
                super().__init__(description)
                self._added_variables = []
                self._added_locator_list = []
                self._undo_count = 0

            def execute(self):
                node_data_list = nodes_data['node_data_list']
                # 如果是移动节点操作，则先记录一下被移动的节点ID
                to_deleted_ids = []
                if action == Qt.DropAction.MoveAction:
                    for node_data in node_data_list:
                        index_parent = model.locate_index(*node_data['source_parent_index_locator'])
                        index_row = node_data['source_row']
                        index = model.index(index_row, 0, index_parent)
                        to_deleted_ids.append(index.internalPointer().id)
                # 在新位置插入节点
                parent = model.locate_index(*parent_locator)
                added_ids = []
                for i, node_data in enumerate(node_data_list):
                    added_ids.append(self.insert_subtree(node_data, row + i, parent).internalPointer().id)
                # 删除被移动的节点
                if to_deleted_ids:
                    for id in reversed(to_deleted_ids):
                        index = model.get_index_by_node_id(id)
                        model.removeRow(index.row(), index.parent())
                # 记录新插入的节点位置，用于撤销操作
                self._added_locator_list = [model.index_locator(model.get_index_by_node_id(id)) for id in added_ids]
                model.update_line_no()

            def undo(self):
                # 回滚新增的变量
                if self._added_variables:
                    for var_def in self._added_variables:
                        var_def = model.process_def.get_variable(var_def.name)
                        model.remove_variable(var_def)
                    self._added_variables = []
                # 回滚新插入的节点
                for locator in reversed(self._added_locator_list):
                    index = model.locate_index(*locator)
                    model.removeRow(index.row(), index.parent())
                self._added_locator_list = []
                # 回滚移动操作删除的原节点
                if action == Qt.DropAction.MoveAction:
                    node_data_list = nodes_data['node_data_list']
                    for node_data in node_data_list:
                        parent = model.locate_index(*node_data['source_parent_index_locator'])
                        row = node_data['source_row']
                        self.insert_subtree(node_data, row, parent)
                model.update_line_no()
                self._undo_count += 1

            def insert_subtree(self, root_node_data: dict, row, parent):
                comp_def = AppContext.engine().get_component_def(AppContext.app().app_package,
                                                                 root_node_data["component"])
                model.insertRow(row, parent)
                index = model.index(row, 0, parent)
                model.setData(index, root_node_data)
                flow_node = index.internalPointer()
                self._added_variables.extend(outer_self.add_variables_if_not_exist(flow_node, comp_def))
                if 'flow' in root_node_data:
                    for i, child_node_data in enumerate(root_node_data['flow']):
                        self.insert_subtree(child_node_data, i, index)
                return index

        model.undo_redo_manager.perform_action(DropNodesAction(
            gettext("Move instructions") if action == Qt.DropAction.MoveAction else gettext("Copy instructions")))

    def append_node(self, comp_def: ComponentDef):
        parent = QModelIndex()
        self.add_node(self.model().rowCount(parent), parent, comp_def)

    @Slot(QModelIndex)
    def edit_node(self, index: QModelIndex):
        flow_node: FlowNode = index.internalPointer()
        model: ProcessModel = self.model()
        comp_def = AppContext.engine().get_component_def(model.process_def.package, flow_node.component)
        if comp_def is None:
            QMessageBox.warning(self, gettext('Error'),
                                gettext('Unknown instruction or process config {config}').format(
                                    config=json.dumps(flow_node.to_json(False), ensure_ascii=False)))
            return
        if any(v.direction != VariableDirection.LOCAL for v in comp_def.variables) or comp_def.supports_error_handling:
            comp_dialog = ComponentDialog(model, comp_def, flow_node, self)
            if comp_dialog.exec() == QDialog.DialogCode.Accepted:
                flow_node_json = comp_dialog.get_flow_node()

                outer_self = self
                index_locator = model.index_locator(index)

                class EditNodeAction(Action):
                    def __init__(self, description):
                        super().__init__(description)
                        self._old_node_json = None
                        self._added_variables = []

                    def execute(self):
                        index = model.locate_index(*index_locator)
                        flow_node: FlowNode = index.internalPointer()
                        self._old_node_json = snapshot_flow_node(flow_node)
                        model.setData(index, flow_node_json)
                        self._added_variables = outer_self.add_variables_if_not_exist(flow_node, comp_def)
                        model.update_line_no()

                    def undo(self):
                        if self._added_variables:
                            for var_def in self._added_variables:
                                var_def = model.process_def.get_variable(var_def.name)
                                model.remove_variable(var_def)
                        index = model.locate_index(*index_locator)
                        model.setData(index, self._old_node_json)
                        model.update_line_no()

                model.undo_redo_manager.perform_action(EditNodeAction(gettext("Edit Instruction")))

    def add_variables_if_not_exist(self, flow_node: FlowNode, component_def: ComponentDef):
        model: ProcessModel = self.model()
        added = []
        for k, v in flow_node.outputs.items():
            if not v:
                continue
            v_var_def = model.process_def.get_variable(v)
            if v_var_def is None:
                k_var_def = component_def.get_variable(k)
                v_var_def = VariableDef()
                v_var_def.name = v
                v_var_def.type = k_var_def.type
                v_var_def.direction = VariableDirection.LOCAL
                v_var_def.elementType = k_var_def.elementType
                model.add_variable(v_var_def)
                added.append(v_var_def)
        return added

    def _create_actions(self):
        deactivate_breakpoint_action = QAction(gettext('Remove Breakpoint'), self)
        deactivate_breakpoint_action.triggered.connect(self.deactivate_current_index_breakpoint)
        self._deactivate_breakpoint_action = deactivate_breakpoint_action

        activate_breakpoint_action = QAction(gettext('Add Breakpoint'), self)
        activate_breakpoint_action.triggered.connect(self.activate_current_index_breakpoint)
        self._activate_breakpoint_action = activate_breakpoint_action

        copy_action = QAction(gettext('Copy'), self)
        copy_action.triggered.connect(self.copy_selected_nodes)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.setShortcutVisibleInContextMenu(True)
        copy_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._copy_action = copy_action

        cut_action = QAction(gettext('Cut'), self)
        cut_action.triggered.connect(self.cut_selected_nodes)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.setShortcutVisibleInContextMenu(True)
        cut_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._cut_action = cut_action

        paste_before_action = QAction(gettext('Paste Before'), self)
        paste_before_action.triggered.connect(self.paste_nodes_before)
        self._paste_before_action = paste_before_action

        paste_inside_action = QAction(gettext('Paste Inside'), self)
        paste_inside_action.triggered.connect(self.paste_nodes_inside)
        self._paste_inside_action = paste_inside_action

        paste_after_action = QAction(gettext('Paste After'), self)
        paste_after_action.triggered.connect(self.paste_nodes_after)
        self._paste_after_action = paste_after_action

        paste_action = QAction(gettext('Paste'), self)
        paste_action.triggered.connect(self.paste_nodes_at_last)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.setShortcutVisibleInContextMenu(True)
        paste_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._paste_action = paste_action

        delete_action = QAction(gettext('Delete'), self)
        delete_action.triggered.connect(self.remove_selected_nodes)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.setShortcutVisibleInContextMenu(True)
        delete_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._delete_action = delete_action

        open_process_action = QAction(gettext('Open Process'), self)
        open_process_action.triggered.connect(self._open_process)
        self._open_process_action = open_process_action

    @Slot()
    def _open_process(self):
        component_def = self._get_current_component_def()
        if isinstance(component_def, ProcessDef):
            self.open_process_def.emit(component_def)

    def contextMenuEvent(self, event):
        # 获取鼠标点击位置对应的QModelIndex
        index = self.indexAt(event.pos())

        # 创建上下文菜单
        context_menu = QMenu(self)

        if isinstance(self._get_current_component_def(), ProcessDef):
            context_menu.addAction(self._open_process_action)

        if index.isValid():
            node: FlowNode = index.internalPointer()
            # 添加菜单项
            if node.breakpoint:
                context_menu.addAction(self._deactivate_breakpoint_action)
            else:
                context_menu.addAction(self._activate_breakpoint_action)

        if self.selectedIndexes():
            context_menu.addAction(self._copy_action)
            context_menu.addAction(self._cut_action)

        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasFormat(mimetype_process_flow_nodes):
            if index.isValid():
                context_menu.addAction(self._paste_before_action)
                context_menu.addAction(self._paste_inside_action)
                context_menu.addAction(self._paste_after_action)
            else:
                context_menu.addAction(self._paste_action)

        if self.selectedIndexes():
            context_menu.addAction(self._delete_action)

        # 在鼠标点击位置显示上下文菜单
        context_menu.exec_(event.globalPos())

    def _get_current_component_def(self):
        index = self.currentIndex()
        if index.isValid():
            node: FlowNode = index.internalPointer()
            return AppContext.engine().get_component_def(node.process_def.package, node.component)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            self.remove_selected_nodes()
            event.accept()
        else:
            super().keyPressEvent(event)

    @Slot()
    def remove_selected_nodes(self):
        if self.selectedIndexes():
            self.remove_nodes(self.selectedIndexes())

    @Slot()
    def copy_selected_nodes(self):
        if self.selectedIndexes():
            self.copy_nodes(self.selectedIndexes())

    @Slot()
    def cut_selected_nodes(self):
        if self.selectedIndexes():
            self.cut_nodes(self.selectedIndexes())

    def copy_nodes(self, indexes: list[QModelIndex]):
        model: ProcessModel = self.model()
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(model.mimeData(indexes))

    def cut_nodes(self, indexes):
        model: ProcessModel = self.model()
        clipboard = QApplication.clipboard()
        clipboard.setMimeData(model.mimeData(indexes))
        self.remove_nodes(indexes)

    @Slot()
    def paste_nodes_before(self):
        index = self.currentIndex()
        if index.isValid():
            self.paste_nodes(index.row(), index.parent())

    @Slot()
    def paste_nodes_inside(self):
        index = self.currentIndex()
        if index.isValid():
            self.paste_nodes(self.model().rowCount(index), index)

    @Slot()
    def paste_nodes_after(self):
        index = self.currentIndex()
        if index.isValid():
            self.paste_nodes(index.row() + 1, index.parent())

    @Slot()
    def paste_nodes_at_last(self):
        self.paste_nodes(self.model().rowCount(), QModelIndex())

    @Slot(int, QModelIndex)
    def paste_nodes(self, row: int, parent: QModelIndex):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if not mime_data.hasFormat(mimetype_process_flow_nodes):
            return
        nodes_data = json.loads(mime_data.data(mimetype_process_flow_nodes).data().decode('utf-8'))
        model: ProcessModel = self.model()
        outer_self = self
        parent_locator = model.index_locator(parent)

        class PasteNodesAction(Action):
            def __init__(self, description):
                super().__init__(description)
                self._added_variables = []
                self._added_locator_list = []

            def execute(self):
                node_data_list = nodes_data['node_data_list']
                parent = model.locate_index(*parent_locator)
                for i, node_data in enumerate(node_data_list):
                    index = self.insert_subtree(node_data, row + i, parent)
                    self._added_locator_list.append(model.index_locator(index))
                model.update_line_no()

            def undo(self):
                # 回滚新增的变量
                if self._added_variables:
                    for var_def in self._added_variables:
                        var_def = model.process_def.get_variable(var_def.name)
                        model.remove_variable(var_def)
                    self._added_variables = []
                # 回滚新插入的节点
                for locator in reversed(self._added_locator_list):
                    index = model.locate_index(*locator)
                    model.removeRow(index.row(), index.parent())
                self._added_locator_list = []
                model.update_line_no()

            def insert_subtree(self, root_node_data: dict, row, parent):
                comp_def = AppContext.engine().get_component_def(AppContext.app().app_package,
                                                                 root_node_data["component"])
                model.insertRow(row, parent)
                index = model.index(row, 0, parent)
                model.setData(index, root_node_data)
                flow_node = index.internalPointer()
                self._added_variables.extend(outer_self.add_variables_if_not_exist(flow_node, comp_def))
                if 'flow' in root_node_data:
                    for i, child_node_data in enumerate(root_node_data['flow']):
                        self.insert_subtree(child_node_data, i, index)
                return index

        model.undo_redo_manager.perform_action(PasteNodesAction(gettext("Paste Instructions")))

    @Slot()
    def deactivate_current_index_breakpoint(self):
        index = self.currentIndex()
        if index.isValid():
            self.deactivate_breakpoint(index)

    def deactivate_breakpoint(self, index: QModelIndex):
        model = self.model()
        model.setData(index, {"breakpoint": False})

    @Slot()
    def activate_current_index_breakpoint(self):
        index = self.currentIndex()
        if index.isValid():
            self.activate_breakpoint(index)

    def activate_breakpoint(self, index: QModelIndex):
        model = self.model()
        model.setData(index, {"breakpoint": True})

    def remove_nodes(self, indexes: list[QModelIndex]):
        model: ProcessModel = self.model()
        subtree_indexes = model.get_subtree_indexes(indexes)
        subtree_data_list = []
        for index in subtree_indexes:
            subtree_data_list.append((model.index_locator(index), snapshot_flow_node_tree(index.internalPointer())))

        class RemoveNodesAction(Action):
            def execute(self):
                for locator, node_json in reversed(subtree_data_list):
                    index = model.locate_index(*locator)
                    model.removeRow(index.row(), index.parent())
                model.update_line_no()

            def undo(self):
                for locator, node_json in subtree_data_list:
                    parent, row = model.locate_parent_index(*locator)
                    self.insert_subtree(node_json, row, parent)
                model.update_line_no()

            def insert_subtree(self, root_node_data: dict, row, parent):
                model.insertRow(row, parent)
                index = model.index(row, 0, parent)
                model.setData(index, root_node_data)
                if 'flow' in root_node_data:
                    for i, child_node_data in enumerate(root_node_data['flow']):
                        self.insert_subtree(child_node_data, i, index)
                return index

        model.undo_redo_manager.perform_action(RemoveNodesAction(gettext("Remove Instructions")))


class ProcessSidebar(QWidget):
    def __init__(self, process_view: ProcessFlowView, process_model: ProcessModel):
        super().__init__()
        self.setMouseTracking(True)
        self._process_view = process_view
        self._process_model = process_model
        self._dot_width = 12
        self._h_padding = 2
        # self._process_view.installEventFilter(self)
        self._process_model.rowsInserted.connect(self._on_rows_inserted)
        self._process_model.rowsRemoved.connect(self._on_rows_removed)
        self._process_model.dataChanged.connect(self._on_data_changed)
        self._process_view.horizontalScrollBar().valueChanged.connect(self._on_scrollbar_value_changed)
        self._process_view.verticalScrollBar().valueChanged.connect(self._on_scrollbar_value_changed)
        self._process_view.collapsed.connect(self._on_row_collapsed)
        self._process_view.expanded.connect(self._on_row_collapsed)
        self._items = []

    @Slot(QModelIndex, int, int)
    def _on_rows_inserted(self, parent: QModelIndex, first: int, last: int):
        self.updateGeometry()

    @Slot(QModelIndex, int, int)
    def _on_rows_removed(self, parent: QModelIndex, first: int, last: int):
        self.updateGeometry()

    @Slot(int)
    def _on_scrollbar_value_changed(self, value: int):
        self.updateGeometry()

    @Slot(QModelIndex)
    def _on_row_collapsed(self, index: QModelIndex):
        self.updateGeometry()

    @Slot(QModelIndex, QModelIndex, list)
    def _on_data_changed(self, topLeft: QModelIndex, bottomRight: QModelIndex, roles: list[int]):
        self.updateGeometry()

    def eventFilter(self, watched, event):
        if watched == self._process_view:
            if event.type() == QEvent.Type.Paint:
                QTimer.singleShot(0, lambda: self.updateGeometry())
                return False
        return super().eventFilter(watched, event)

    def sizeHint(self):
        # 宽度=max(最大行号文字宽度, 断点宽度)
        self.ensurePolished()
        font_metrics = self.fontMetrics()
        stack = [QModelIndex()]
        max_line_no = 0
        while len(stack) > 0:
            node_index = stack.pop()
            if node_index.isValid():
                max_line_no += 1
            for i in range(0, self._process_model.rowCount(node_index)):
                stack.append(self._process_model.index(i, 0, node_index))
        width = max(len(str(max_line_no)) * font_metrics.maxWidth(), self._dot_width)
        ## 高度=行高
        s = QSize(width + self._h_padding * 2, font_metrics.height())
        return s

    def sizePolicy(self):
        return QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.MinimumExpanding)

    def paintEvent(self, event):
        painter = QStylePainter(self)
        content_rect = self.rect()
        pal = self.palette()
        painter.fillRect(content_rect, pal.color(QPalette.ColorRole.Base))
        padding_rect = content_rect.adjusted(self._h_padding, 0, -self._h_padding, 0)
        stack = [QModelIndex()]
        line_no = 0
        y_offset = self._process_view.viewport().geometry().y()
        self._items = []
        while len(stack) > 0:
            node_index = stack.pop()
            if node_index.isValid():
                line_no += 1
                row_rect = self._process_view.visualRect(node_index)
                if row_rect.isValid():
                    node: FlowNode = node_index.internalPointer()
                    row_rect.translate(0, y_offset)
                    label_padding_rect = QRect(padding_rect.x(), row_rect.y(), padding_rect.width(), row_rect.height())
                    self._items.append((node_index, label_padding_rect))
                    if label_padding_rect.intersects(content_rect):
                        if node.breakpoint:
                            # painter.fillRect(label_rect, Qt.gray)
                            pic_rect = QRect(label_padding_rect.right() - self._dot_width,
                                             label_padding_rect.center().y() - self._dot_width / 2,
                                             self._dot_width, self._dot_width)
                            # painter.fillRect(pic_rect, Qt.white)
                            painter.drawPixmap(pic_rect, QPixmap(":/icons/redpoint.png"))
                        else:
                            old_pen = painter.pen()
                            painter.setPen(pal.placeholderText().color())
                            painter.drawText(label_padding_rect,
                                             Qt.TextFlag.TextSingleLine | Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                                             str(line_no))
                            painter.setPen(old_pen)
            for i in range(self._process_model.rowCount(node_index) - 1, -1, -1):
                stack.append(self._process_model.index(i, 0, node_index))

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        for item in self._items:
            node_index, label_rect = item
            if label_rect.contains(event.pos()):
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                return
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            for item in self._items:
                node_index, label_rect = item
                if label_rect.contains(event.pos()):
                    node: FlowNode = node_index.internalPointer()
                    if node.breakpoint:
                        self._process_view.deactivate_breakpoint(node_index)
                    else:
                        self._process_view.activate_breakpoint(node_index)
                    return


class ProcessFlowWidget(QWidget):
    open_process_def = Signal(ProcessDef)

    def __init__(self, process_model: ProcessModel):
        super().__init__()
        self.process_model = process_model
        self.process_def = process_model.process_def
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        self.process_view = ProcessFlowView()
        self.process_view.setModel(self.process_model)
        self.process_view.setSelectionModel(RecursiveSelectionModel(self.process_model))
        self.process_view.expandAll()
        self.process_view.open_process_def.connect(self._open_process_def)
        sidebar = ProcessSidebar(self.process_view, self.process_model)
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.process_view)

    def select_node(self, node: FlowNode):
        if node.process_def.name != self.process_def.name:
            return
        index = self.process_model.node_index(node)
        self.process_view.scrollTo(index)
        self.process_view.selectionModel().select(index,
                                                  QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows)

    @Slot(ProcessDef)
    def _open_process_def(self, ProcessDef):
        self.open_process_def.emit(ProcessDef)


class ProcessVariablesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._process_model: ProcessModel | None = None
        main_layout = QVBoxLayout(self)

        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton(gettext("Add variable"))
        self.add_button.setDisabled(True)
        self.delete_button = QPushButton(gettext("Delete variable"))
        self.delete_button.setDisabled(True)
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.delete_button)
        main_layout.addLayout(buttons_layout)
        self.add_button.clicked.connect(self.add_var)
        self.delete_button.clicked.connect(self.delete_var)

        # 添加输入列表
        self.list_model = QStandardItemModel(0, 3)
        self.list_model.setHorizontalHeaderLabels([gettext("Direction"), gettext("Name"), gettext("Type")])
        self.list_view = QTableView()
        self.list_view.setModel(self.list_model)
        self.list_view.verticalHeader().hide()
        self.list_view.setColumnWidth(0, 55)
        self.list_view.setColumnWidth(2, 70)
        self.list_view.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.list_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.list_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list_view.doubleClicked.connect(self.edit_var)
        main_layout.addWidget(self.list_view)

    def set_process_model(self, process_model: ProcessModel | None):
        if self._process_model:
            self._process_model.variable_added.disconnect(self.on_var_added)
            self._process_model.variable_updated.disconnect(self.on_var_updated)
            self._process_model.variable_removed.disconnect(self.on_var_removed)
        self._process_model = process_model
        row_count = self.list_model.rowCount()
        if row_count:
            self.list_model.removeRows(0, row_count)

        if self._process_model is None:
            self.add_button.setDisabled(True)
            self.delete_button.setDisabled(True)
        else:
            for var_def in process_model.process_def.variables:
                self.list_model.appendRow(self._create_variable_row(var_def))
            self.add_button.setDisabled(False)
            self.delete_button.setDisabled(False)
            self._process_model.variable_added.connect(self.on_var_added)
            self._process_model.variable_updated.connect(self.on_var_updated)
            self._process_model.variable_removed.connect(self.on_var_removed)

    def _create_variable_row(self, var_def: VariableDef) -> list[QStandardItem]:
        direction_desc = {
            VariableDirection.IN: gettext("IN"),
            VariableDirection.OUT: gettext("OUT"),
            VariableDirection.LOCAL: gettext("LOCAL")
        }
        type_def = AppContext.engine().type_registry.get_data_type(var_def.type)
        type_desc = type_def.display_name if type_def else var_def.type
        row = []
        for column in [direction_desc[var_def.direction], var_def.name, type_desc]:
            item = QStandardItem(column)
            item.setData(var_def, Qt.ItemDataRole.UserRole)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            row.append(item)
        return row

    @Slot()
    def add_var(self):
        jin_dialog = CreateVariableDialog(self._process_model, None, self)
        outer_self = self
        if jin_dialog.exec() == QDialog.DialogCode.Accepted:
            var_def = jin_dialog.new_var_def

            class AddVarAction(Action):

                def execute(self):
                    outer_self._process_model.add_variable(var_def)

                def undo(self):
                    flush_var_def = outer_self._process_model.process_def.get_variable(var_def.name)
                    outer_self._process_model.remove_variable(flush_var_def)

            self._process_model.undo_redo_manager.perform_action(AddVarAction(gettext("Add variable")))

    @Slot(VariableDef)
    def on_var_added(self, var_def: VariableDef):
        self.list_model.appendRow(self._create_variable_row(var_def))

    @Slot(QModelIndex)
    def edit_var(self, index: QModelIndex):
        var_def = self._process_model.process_def.variables[index.row()]
        jin_dialog = CreateVariableDialog(self._process_model, var_def, self)
        if jin_dialog.exec() == QDialog.DialogCode.Accepted:
            new_var_def = jin_dialog.new_var_def

            outer_self = self

            class UpdateVarAction(Action):

                def execute(self):
                    flush_var_def = outer_self._process_model.process_def.get_variable(var_def.name)
                    outer_self._process_model.update_variable(new_var_def, flush_var_def)

                def undo(self):
                    flush_var_def = outer_self._process_model.process_def.get_variable(new_var_def.name)
                    outer_self._process_model.update_variable(var_def, flush_var_def)

            self._process_model.undo_redo_manager.perform_action(UpdateVarAction(gettext("Update variable")))

    @Slot(int, VariableDef, VariableDef)
    def on_var_updated(self, row: int, new_var_def: VariableDef, old_var_def: VariableDef):
        row_items = self._create_variable_row(new_var_def)
        for i, item in enumerate(row_items):
            self.list_model.setItem(row, i, item)

    @Slot()
    def delete_var(self):
        selected_vars = [index.data(Qt.ItemDataRole.UserRole) for index in
                         self.list_view.selectionModel().selectedRows()]
        outer_self = self

        class DeleteVarAction(Action):

            def execute(self):
                for var_def in selected_vars:
                    var_def = outer_self._process_model.process_def.get_variable(var_def.name)
                    outer_self._process_model.remove_variable(var_def)

            def undo(self):
                for var_def in selected_vars:
                    outer_self._process_model.add_variable(var_def)

        self._process_model.undo_redo_manager.perform_action(DeleteVarAction(gettext("Delete variable")))

    @Slot(int, VariableDef)
    def on_var_removed(self, row: int, var_def: VariableDef):
        self.list_model.removeRow(row)
