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

from PySide6.QtCore import Slot, Signal, QModelIndex, QEvent, QMimeData
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt, QIcon
from PySide6.QtWidgets import QTreeView, QWidget, QGridLayout, QLineEdit, QAbstractItemView

from jimuflow.common.mimetypes import mimetype_component_def_ids
from jimuflow.definition import ProcessDef, ComponentDef
from jimuflow.gui.app import App, AppContext
from jimuflow.gui.components.vertical_nav_bar import VerticalNavBar
from jimuflow.gui.help_dialog import HelpDialog
from jimuflow.locales.i18n import gettext

categories = {
    "Process Control": {
        "title": gettext("Process Control"),
        "sort_no": 10
    },
    "Switch": {
        "title": gettext("Switch"),
        "sort_no": 20
    },
    "Loop": {
        "title": gettext("Loop"),
        "sort_no": 30
    },
    "Wait": {
        "title": gettext("Wait"),
        "sort_no": 35
    },
    "Web Automation": {
        "title": gettext("Web Automation"),
        "sort_no": 40
    },
    "Web Page Operation": {
        "title": gettext("Web Page Operation"),
        "sort_no": 41
    },
    "Web Element Operation": {
        "title": gettext("Web Element Operation"),
        "sort_no": 42
    },
    "Web Data Extraction": {
        "title": gettext("Web Data Extraction"),
        "sort_no": 43
    },
    "Web Dialog Operation": {
        "title": gettext("Web Dialog Operation"),
        "sort_no": 44
    },
    "Windows Automation": {
        "title": gettext("Windows Automation"),
        "sort_no": 45
    },
    "Data Process": {
        "title": gettext("Data Process"),
        "sort_no": 50
    },
    "Text Operation": {
        "title": gettext("Text Operation"),
        "sort_no": 51
    },
    "Number Operation": {
        "title": gettext("Number Operation"),
        "sort_no": 52
    },
    "List operation": {
        "title": gettext("List operation"),
        "sort_no": 53
    },
    "Dictionary operation": {
        "title": gettext("Dictionary operation"),
        "sort_no": 54
    },
    "Date Time Operation": {
        "title": gettext("Date Time Operation"),
        "sort_no": 55
    },
    "Process": {
        "title": gettext("Process"),
        "sort_no": 70
    },
    "Other": {
        "title": gettext("Other"),
        "sort_no": 10000
    }
}


class ComponentListModel(QStandardItemModel):

    def mimeTypes(self):
        return [mimetype_component_def_ids]

    def mimeData(self, indexes: list[QModelIndex]) -> QMimeData:
        mime_data = QMimeData()
        component_defs: list[ComponentDef] = [self.data(index, Qt.ItemDataRole.UserRole) for index in indexes]
        data = ",".join(component_def.id(AppContext.app().app_package) for component_def in component_defs)
        mime_data.setData(mimetype_component_def_ids, data.encode("utf-8"))
        return mime_data


class ComponentListWidget(QWidget):
    component_double_clicked = Signal(ComponentDef)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        main_layout = QGridLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        search_input = QLineEdit()
        search_input.setPlaceholderText(gettext("Search instruction"))
        search_input.textChanged.connect(self.search)
        self._search_input = search_input
        main_layout.addWidget(search_input, 0, 0, 1, 2)
        nav_bar = VerticalNavBar()
        nav_bar.item_clicked.connect(self._on_nav_item_clicked)
        self._nav_bar = nav_bar
        main_layout.addWidget(nav_bar, 1, 0, 1, 1)
        instruction_tree_view = QTreeView()
        instruction_tree_model = ComponentListModel()
        instruction_tree_view.setModel(instruction_tree_model)
        instruction_tree_view.setTextElideMode(Qt.TextElideMode.ElideNone)
        instruction_tree_view.setDragEnabled(True)
        instruction_tree_view.header().hide()
        instruction_tree_view.expandAll()
        instruction_tree_view.setRootIsDecorated(False)
        instruction_tree_view.doubleClicked.connect(self._on_component_double_clicked)
        instruction_tree_view.installEventFilter(self)
        self._instruction_tree_view = instruction_tree_view
        self._instruction_tree_model = instruction_tree_model
        main_layout.addWidget(instruction_tree_view, 1, 1, 1, 1)
        main_layout.setColumnStretch(1, 1)
        self.app: App | None = None
        self._component_defs = []

    def set_app(self, app: App | None):
        if self.app:
            self.app.process_def_files_changed.disconnect(self.reload)
        self.app = app
        if app is not None:
            self.app.process_def_files_changed.connect(self.reload)
        self.reload()

    @Slot()
    def reload(self):
        self._load_component_defs()
        self.search(self._search_input.text())

    def _load_component_defs(self):
        if self.app:
            self._component_defs = [self._build_component_item(component_def) for component_def in
                                    AppContext.engine().get_available_component_defs(self.app.app_package)]
        else:
            self._component_defs = []

    def _build_component_item(self, component_def: ComponentDef):
        categories = []
        if component_def.primary_category:
            if component_def.secondary_category:
                categories.append((component_def.primary_category, component_def.secondary_category))
            else:
                categories.append((component_def.primary_category,))
        elif isinstance(component_def, ProcessDef):
            categories.append(("Process",))
        else:
            categories.append(("Other",))
        categories.extend(component_def.categories)
        localized_categories = [tuple(gettext(name) for name in entry) for entry in categories]
        keywords = [component_def.name.lower()]
        if isinstance(component_def, ProcessDef):
            localized_display_name = component_def.name
        else:
            localized_display_name = gettext(component_def.display_name)
            keywords.append(component_def.display_name)
            keywords.append(localized_display_name)
        for entry in categories:
            keywords.extend(entry)
        for entry in localized_categories:
            keywords.extend(entry)
        return {
            "categories": categories,
            "localized_categories": localized_categories,
            "localized_display_name": localized_display_name,
            "keywords": "\n".join(keywords),
            "component_def": component_def,
        }

    @Slot(str)
    def search(self, keyword: str):
        self._instruction_tree_model.clear()
        self._nav_bar.clear()
        if self.app is None:
            return
        tree = {}
        keyword = keyword.lower() if keyword else ""
        for component_data in self._component_defs:
            if (keyword and keyword not in component_data['keywords']):
                continue
            for category, localized_category in zip(component_data['categories'],
                                                    component_data['localized_categories']):
                primary_category = category[0]
                secondary_category = category[1] if len(category) > 1 else ''
                primary_node = tree.get(primary_category, {
                    "name": primary_category,
                    "localized_name": localized_category[0],
                    "children": {}
                })
                tree[primary_category] = primary_node
                secondary_node = primary_node["children"].get(secondary_category, {
                    "name": secondary_category,
                    "localized_name": localized_category[1] if secondary_category else '',
                    "children": []
                })
                secondary_node["children"].append(component_data)
                primary_node["children"][secondary_category] = secondary_node
        primary_nodes = list(tree.values())
        primary_nodes.sort(key=lambda x: categories.get(x["name"], {"sort_no": 1000})["sort_no"])
        for primary_node in primary_nodes:
            primary_node_text = primary_node['localized_name']
            primary_node_item = QStandardItem(primary_node_text)
            primary_node_item.setData(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen), Qt.ItemDataRole.DecorationRole)
            primary_node_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self._instruction_tree_model.appendRow(primary_node_item)
            self._nav_bar.add_item(primary_node_text, primary_node_item)
            secondary_nodes = list(primary_node["children"].values())
            secondary_nodes.sort(
                key=lambda x: categories.get(x["name"], {"sort_no": 1000})["sort_no"] if x["name"] else 0)
            for secondary_node in secondary_nodes:
                if secondary_node["name"]:
                    secondary_node_item = QStandardItem(secondary_node["localized_name"])
                    secondary_node_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                    secondary_node_item.setData(QIcon.fromTheme(QIcon.ThemeIcon.DocumentOpen),
                                                Qt.ItemDataRole.DecorationRole)
                    primary_node_item.appendRow(secondary_node_item)
                else:
                    secondary_node_item = None
                secondary_node["children"].sort(key=lambda x: x['component_def'].sort_no)
                for component_data in secondary_node["children"]:
                    component_def = component_data["component_def"]
                    item = QStandardItem()
                    if isinstance(component_def, ProcessDef):
                        item.setText(gettext('Process {name}').format(name=component_def.name))
                    else:
                        item.setText(component_data['localized_display_name'])
                    item.setData(component_def, Qt.ItemDataRole.UserRole)
                    if component_def.is_supported_on_current_platform():
                        if component_def.help_url:
                            item.setData(gettext(
                                'Double click or drag to add to the current process, select and press F1 key to view help'),
                                Qt.ItemDataRole.ToolTipRole)
                        else:
                            item.setData(gettext('Double click or drag to add to the current process'),
                                         Qt.ItemDataRole.ToolTipRole)
                        item.setFlags(
                            Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    else:
                        item.setData(gettext('Only supported on {platforms}').format(
                            platforms=', '.join(i.localized_name() for i in component_def.platforms)),
                            Qt.ItemDataRole.ToolTipRole)
                        item.setFlags(Qt.ItemFlag.NoItemFlags)
                    if secondary_node_item:
                        secondary_node_item.appendRow(item)
                    else:
                        primary_node_item.appendRow(item)
        self._instruction_tree_view.expandAll()

    @Slot(object)
    def _on_nav_item_clicked(self, item):
        self._instruction_tree_view.scrollTo(item.index(), hint=QAbstractItemView.ScrollHint.PositionAtTop)

    @Slot(QModelIndex)
    def _on_component_double_clicked(self, index: QModelIndex):
        if index.flags() & Qt.ItemFlag.ItemIsEnabled:
            comp_def = index.data(Qt.ItemDataRole.UserRole)
            if isinstance(comp_def, ComponentDef):
                self.component_double_clicked.emit(comp_def)

    def eventFilter(self, watched, event):
        if isinstance(watched, QTreeView):
            if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_F1:
                current_index = watched.currentIndex()
                if current_index.isValid():
                    comp_def = current_index.data(Qt.ItemDataRole.UserRole)
                    if comp_def.help_url:
                        HelpDialog.show_help(comp_def.help_url)
                        return True
        return super().eventFilter(watched, event)
