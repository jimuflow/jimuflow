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

from datetime import datetime

from PySide6.QtCore import Signal, Slot, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt
from PySide6.QtWidgets import QTableView

from jimuflow.definition import ProcessDef
from jimuflow.gui.app import AppContext
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.log import Logger, LogEntry, LogLevel


class LogWidget(QTableView):
    add_log = Signal(LogEntry)
    log_double_clicked = Signal(str, int)

    def __init__(self, max_logs=500, parent=None):
        super().__init__(parent)
        self._model = QStandardItemModel(self)
        self.setModel(self._model)
        self.add_log.connect(self.on_add_log)
        self.doubleClicked.connect(self._on_double_clicked)
        self.max_logs = max_logs
        self._model.setHorizontalHeaderLabels(
            [gettext('Timestamp'), gettext('Level'), gettext('Process'), gettext('Line No'), gettext('Instruction'),
             gettext('Message')])
        self.setColumnWidth(0, 70)
        self.setColumnWidth(1, 40)
        self.setColumnWidth(2, 100)
        self.setColumnWidth(3, 40)
        self.setColumnWidth(4, 100)
        self.horizontalHeader().setStretchLastSection(True)

    def clear(self):
        row_count = self._model.rowCount()
        if row_count:
            self._model.removeRows(0, row_count)

    @Slot(LogEntry)
    def on_add_log(self, log_entry: LogEntry):
        timestamp = QStandardItem(datetime.now().strftime("%H:%M:%S"))
        timestamp.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        level = QStandardItem(log_entry.level.display_name)
        level.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        engine = AppContext.engine()
        app = AppContext.app()
        if log_entry.process_id:
            process_name = QStandardItem(engine.get_component_def(app.app_package, log_entry.process_id).name)
        else:
            process_name = QStandardItem("")
        process_name.setData(log_entry.process_id)
        process_name.setData(process_name.text(), Qt.ItemDataRole.ToolTipRole)
        process_name.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        if log_entry.comp_id and log_entry.comp_id != log_entry.process_id:
            comp_def = engine.get_component_def(app.app_package, log_entry.comp_id)
            if isinstance(comp_def, ProcessDef):
                comp_name = QStandardItem(gettext('Process {name}').format(name=comp_def.name))
            else:
                comp_name = QStandardItem(gettext(comp_def.display_name))
        else:
            comp_name = QStandardItem("")
        comp_name.setData(comp_name.text(), Qt.ItemDataRole.ToolTipRole)
        comp_name.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        if log_entry.line_no is not None:
            line_no = QStandardItem(str(log_entry.line_no))
            line_no.setData(gettext("Double click to navigate to the corresponding process location"),
                            Qt.ItemDataRole.ToolTipRole)
        else:
            line_no = QStandardItem("")
        line_no.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        message_content = log_entry.message
        if log_entry.exception:
            message_content = message_content + ": " + f'{type(log_entry.exception).__name__}: {str(log_entry.exception)}'.replace(
                '\n', '')
        message = QStandardItem(message_content)
        message.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        message.setData(message_content, Qt.ItemDataRole.ToolTipRole)
        self._model.appendRow([timestamp, level, process_name, line_no, comp_name, message])
        if self._model.rowCount() > self.max_logs:
            self._model.removeRow(0)
        self.scrollToBottom()

    @Slot(QModelIndex)
    def _on_double_clicked(self, index: QModelIndex):
        process_id = self._model.data(self._model.index(index.row(), 2, index.parent()))
        line_no = self._model.data(self._model.index(index.row(), 3, index.parent()))
        if process_id and line_no:
            self.log_double_clicked.emit(process_id, int(line_no))


class LogWidgetLogger(Logger):
    def __init__(self, level: LogLevel, log_widget: LogWidget):
        super().__init__(level)
        self._log_widget = log_widget

    def do_log(self, log_entry: LogEntry):
        self._log_widget.add_log.emit(log_entry)
