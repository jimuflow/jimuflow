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
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from PySide6.QtWidgets import QTableView

from jimuflow.gui.app import ProcessModel, AppContext
from jimuflow.locales.i18n import gettext


class ErrorLogWidget(QTableView):
    log_double_clicked = Signal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = QStandardItemModel(self)
        self.setModel(self._model)
        self.doubleClicked.connect(self._on_double_clicked)
        self.process_models = []
        self._model.setHorizontalHeaderLabels(
            [gettext('Process'), gettext('Line No'), gettext('Error')])
        self.setColumnWidth(0, 120)
        self.setColumnWidth(1, 40)
        self.horizontalHeader().setStretchLastSection(True)

    def clear(self):
        for process_model in self.process_models:
            process_model.errors_updated.disconnect(self.reload_logs)
        self.process_models.clear()
        self.clear_logs()

    def clear_logs(self):
        row_count = self._model.rowCount()
        if row_count:
            self._model.removeRows(0, row_count)

    def add_process_model(self, process_model: ProcessModel):
        self.process_models.append(process_model)
        process_model.errors_updated.connect(self.reload_logs)
        self.reload_logs()

    def remove_process_model(self, process_model: ProcessModel):
        self.process_models.remove(process_model)
        process_model.errors_updated.disconnect(self.reload_logs)
        self.reload_logs()

    @Slot()
    def reload_logs(self):
        self.clear_logs()
        for process_model in self.process_models:
            for line_no, errors in process_model.errors:
                for error in errors:
                    self.add_log(process_model, line_no, error)

    def add_log(self, process_model: ProcessModel, line_no: int, error: str):
        process_name_item = QStandardItem(process_model.process_def.name)
        process_name_item.setData(process_model, Qt.ItemDataRole.UserRole)
        process_name_item.setData(process_name_item.text(), Qt.ItemDataRole.ToolTipRole)
        process_name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        line_no_item = QStandardItem(str(line_no))
        line_no_item.setData(line_no, Qt.ItemDataRole.UserRole)
        line_no_item.setData(gettext("Double click to navigate to the corresponding process location"),
                             Qt.ItemDataRole.ToolTipRole)
        line_no_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        message_item = QStandardItem(error)
        message_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        message_item.setData(error, Qt.ItemDataRole.ToolTipRole)
        self._model.appendRow([process_name_item, line_no_item, message_item])

    @Slot(QModelIndex)
    def _on_double_clicked(self, index: QModelIndex):
        process_model: ProcessModel = self._model.data(self._model.index(index.row(), 0, index.parent()),
                                                       Qt.ItemDataRole.UserRole)
        process_id = process_model.process_def.id(AppContext.app().app_package)
        line_no = self._model.data(self._model.index(index.row(), 1, index.parent()), Qt.ItemDataRole.UserRole)
        self.log_double_clicked.emit(process_id, line_no)
