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

from jimuflow.gui.setup_logging import setup_logging_and_redirect

setup_logging_and_redirect()
import sys

sys.coinit_flags = 2

from jimuflow.gui.window_elements_widget import WindowElementsWidget

import asyncio
import logging
import os
import traceback
from asyncio import AbstractEventLoop
from pathlib import Path

from PySide6.QtCore import Slot, QThreadPool, QThread, Signal, QSize
from PySide6.QtGui import QAction, Qt, QIcon, QKeySequence
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QTabWidget, QSplitter, QVBoxLayout, QWidget, \
    QFileDialog, QDialog, QMessageBox

from jimuflow.definition import ProcessDef, ComponentDef
from jimuflow.gui.about_dialog import AboutDialog
from jimuflow.gui.app import App, AppContext, ProcessModel
from jimuflow.gui.app_widget import AppProcessListView
from jimuflow.gui.component_list_widget import ComponentListWidget
from jimuflow.gui.create_new_app import CreateNewAppDialog
from jimuflow.gui.create_process import CreateProcessDialog
from jimuflow.gui.debug_variables_view import DebugVariablesWidget
from jimuflow.gui.elements_widget import ElementsWidget
from jimuflow.gui.error_log_widget import ErrorLogWidget
from jimuflow.gui.help_dialog import HelpDialog
from jimuflow.gui.log_widget import LogWidget, LogWidgetLogger
from jimuflow.gui.process_resource_widget import ProcessResourceWidget
from jimuflow.gui.process_views import ProcessFlowWidget, ProcessVariablesWidget
from jimuflow.gui.start_process_dialog import StartProcessDialog
from jimuflow.gui.utils import Utils
from jimuflow.locales.i18n import gettext
from jimuflow.resource import load_resource
from jimuflow.runtime.execution_engine import Process, Component, ProcessStoppedException
from jimuflow.runtime.log import LogLevel
from jimuflow.runtime.process_debugger import ProcessDebugger, DebugListener

load_resource()
logger = logging.getLogger(__name__)


class CoroutineThread(QThread):
    def __init__(self, coro):
        super().__init__()
        self._coro = coro
        self.result = None
        self.exception = None
        self.loop: AbstractEventLoop | None = None

    @Slot()
    def run(self):
        logger.debug('CoroutineThread running...')
        try:
            self.result = asyncio.run(self._async_run())
        except ProcessStoppedException:
            pass
        except Exception as e:
            self.exception = e
            traceback.print_exc()
        logger.debug('CoroutineThread finished')

    async def _async_run(self):
        self.loop = asyncio.get_running_loop()
        return await self._coro


class MainWindow(QMainWindow, DebugListener):
    debugger_paused = Signal(Component)
    debugger_ended = Signal()
    debugger_resumed = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("JimuFlow")
        self.app: App | None = None
        self._running_process: Process | None = None
        self._thread: CoroutineThread | None = None
        self._debugger: ProcessDebugger | None = None

        self.create_actions()
        self.create_menus()
        self.create_tool_bar()

        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.create_left_widget())
        self.splitter.addWidget(self.create_center_widget())
        self.splitter.addWidget(self.create_right_widget())
        self.splitter.setSizes([250, 650, 300])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(0, 0)

        self.setCentralWidget(self.splitter)

        self.statusBar().showMessage(gettext("Ready"))
        self._threadpool = QThreadPool()
        self.debugger_paused.connect(self.handle_debugger_paused)
        self.debugger_ended.connect(self.stop_process)
        self.debugger_resumed.connect(self.handle_debugger_resumed)

    def create_actions(self):
        self._new_app_act = QAction(gettext('New App'), self)
        self._new_app_act.triggered.connect(self.create_app)

        self._open_app_act = QAction(gettext('Open App'), self)
        self._open_app_act.triggered.connect(self.open_app)
        self._open_app_act.setShortcut(QKeySequence.StandardKey.Open)

        self._config_app_act = QAction(gettext('Config App'), self)
        self._config_app_act.setEnabled(False)
        self._config_app_act.triggered.connect(self.config_app)

        self._new_process_act = QAction(gettext('New Process'), self)
        self._new_process_act.setEnabled(False)
        self._new_process_act.triggered.connect(self.create_process)
        self._new_process_act.setShortcut(QKeySequence.StandardKey.New)

        self._config_process_act = QAction(gettext('Config Process'), self)
        self._config_process_act.setEnabled(False)
        self._config_process_act.triggered.connect(self.config_current_process)

        self._save_process_act = QAction(gettext('Save Process'), self)
        self._save_process_act.setEnabled(False)
        self._save_process_act.triggered.connect(self.save_process)
        self._save_process_act.setShortcut(QKeySequence.StandardKey.Save)

        self._delete_process_act = QAction(gettext('Delete Process'), self)
        self._delete_process_act.setEnabled(False)
        self._delete_process_act.triggered.connect(self.delete_current_process)

        self._undo_act = QAction(gettext('Undo'), self)
        self._undo_act.setEnabled(False)
        self._undo_act.triggered.connect(self._undo)
        self._undo_act.setShortcut(QKeySequence.StandardKey.Undo)

        self._redo_act = QAction(gettext('Redo'), self)
        self._redo_act.setEnabled(False)
        self._redo_act.triggered.connect(self._redo)
        self._redo_act.setShortcut(QKeySequence.StandardKey.Redo)

        self._run_act = QAction(gettext('Run Process'), self)
        self._run_act.setEnabled(False)
        self._run_act.triggered.connect(self.run_process)

        self._start_debug_act = QAction(gettext('Debug Process'), self)
        self._start_debug_act.setEnabled(False)
        self._start_debug_act.triggered.connect(self.start_debug)

        self._debug_run_act = QAction(gettext('Resume Process'), self)
        self._debug_run_act.setEnabled(False)
        self._debug_run_act.triggered.connect(self.debug_run)

        self._stop_act = QAction(gettext('Stop Process'), self)
        self._stop_act.setEnabled(False)
        self._stop_act.triggered.connect(self.stop_process)

        self._step_over_act = QAction(gettext('Step Over'), self)
        self._step_over_act.setEnabled(False)
        self._step_over_act.triggered.connect(self.step_over)

        self._step_into_act = QAction(gettext('Step Into'), self)
        self._step_into_act.setEnabled(False)
        self._step_into_act.triggered.connect(self.step_into)

        self._step_out_act = QAction(gettext('Step Out'), self)
        self._step_out_act.setEnabled(False)
        self._step_out_act.triggered.connect(self.step_out)

        self._about_act = QAction(gettext('About JimuFlow'), self)
        self._about_act.triggered.connect(self.show_about_dialog)

        self._help_act = QAction(gettext('Help'), self)
        self._help_act.triggered.connect(self.show_help_dialog)

    def create_menus(self):
        file_menu = self.menuBar().addMenu(gettext('File'))
        file_menu.addAction(self._new_app_act)
        file_menu.addAction(self._open_app_act)
        file_menu.addAction(self._config_app_act)
        recent_apps = Utils.get_recent_apps()
        if len(recent_apps) > 0:
            recent_apps_menu = file_menu.addMenu(gettext('Recent Apps'))
            for app_path in recent_apps:
                action = QAction(Path(app_path).name, self)
                action.setData(app_path)
                action.triggered.connect(self.open_recent_app)
                recent_apps_menu.addAction(action)
        file_menu.addSeparator()
        file_menu.addAction(self._new_process_act)
        file_menu.addAction(self._config_process_act)
        file_menu.addAction(self._save_process_act)
        file_menu.addAction(self._delete_process_act)

        edit_menu = self.menuBar().addMenu(gettext('Edit'))
        edit_menu.addAction(self._undo_act)
        edit_menu.addAction(self._redo_act)

        run_menu = self.menuBar().addMenu(gettext('Run'))
        run_menu.addAction(self._run_act)
        run_menu.addAction(self._start_debug_act)
        run_menu.addAction(self._debug_run_act)
        run_menu.addAction(self._step_over_act)
        run_menu.addAction(self._step_into_act)
        run_menu.addAction(self._step_out_act)
        run_menu.addAction(self._stop_act)

        help_menu = self.menuBar().addMenu(gettext('Help'))
        help_menu.addAction(self._about_act)
        help_menu.addAction(self._help_act)

    def create_tool_bar(self):
        tool_bar = self.addToolBar('Main')
        tool_bar.setMovable(False)
        tool_bar.setFloatable(False)
        tool_bar.addAction(self._new_app_act)
        tool_bar.addAction(self._open_app_act)
        tool_bar.addAction(self._config_app_act)
        tool_bar.addSeparator()
        tool_bar.addAction(self._new_process_act)
        tool_bar.addAction(self._config_process_act)
        tool_bar.addAction(self._save_process_act)
        tool_bar.addAction(self._delete_process_act)
        tool_bar.addSeparator()
        tool_bar.addAction(self._run_act)
        tool_bar.addAction(self._start_debug_act)
        tool_bar.addAction(self._debug_run_act)
        tool_bar.addAction(self._step_over_act)
        tool_bar.addAction(self._step_into_act)
        tool_bar.addAction(self._step_out_act)
        tool_bar.addAction(self._stop_act)

    def create_left_widget(self):
        left_widget = QSplitter()
        left_widget.setOrientation(Qt.Orientation.Vertical)
        left_widget.addWidget(self.create_process_list_widget())
        left_widget.addWidget(self.create_component_list_widget())
        left_widget.setSizes([100, 300])
        return left_widget

    def create_process_list_widget(self):
        process_list_widget = QWidget()
        layout = QVBoxLayout(process_list_widget)
        layout.addWidget(QLabel(gettext('Process List')))
        self._process_list_view = AppProcessListView()
        self._process_list_view.open_process_def.connect(self.do_open_process)
        self._process_list_view.config_process_def_requested.connect(self.config_process)
        self._process_list_view.delete_process_def_requested.connect(self.delete_process)
        layout.addWidget(self._process_list_view)
        return process_list_widget

    def create_component_list_widget(self):
        label = QLabel(gettext("Instruction List"))
        self.component_list_widget = ComponentListWidget()
        self.component_list_widget.component_double_clicked.connect(self.on_component_double_clicked)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(label)
        layout.addWidget(self.component_list_widget)
        return widget

    @Slot(ComponentDef)
    def on_component_double_clicked(self, comp_def: ComponentDef):
        process_widget: ProcessFlowWidget = self.process_tab_widget.currentWidget()
        if process_widget is not None:
            process_widget.process_view.append_node(comp_def)

    def create_center_widget(self):
        self.process_tab_widget = QTabWidget()
        self.process_tab_widget.setTabsClosable(True)
        self.process_tab_widget.currentChanged.connect(self.process_tab_changed)
        self.process_tab_widget.tabCloseRequested.connect(self.close_process_tab)

        tab_widget = QTabWidget()
        tab_widget.currentChanged.connect(self.bottom_tab_changed)
        tab_widget.setTabPosition(QTabWidget.TabPosition.South)
        self.errors = ErrorLogWidget()
        self.errors.log_double_clicked.connect(self.navigator_to_process_node)
        tab_widget.addTab(self.errors, gettext("Error List"))
        self.log = LogWidget()
        self.log.log_double_clicked.connect(self.navigator_to_process_node)
        tab_widget.addTab(self.log, gettext("Running logs"))
        self.variables_tab = DebugVariablesWidget()
        self.variables_tab.call_stack_double_clicked.connect(self.navigator_to_process_node)
        tab_widget.addTab(self.variables_tab, gettext("Variable Value"))
        self._bottom_tab_widget = tab_widget

        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(self.process_tab_widget)
        splitter.addWidget(tab_widget)
        splitter.setSizes([600, 200])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(0, 0)

        return splitter

    @Slot(int)
    def bottom_tab_changed(self, index):
        current_widget = self.sender().currentWidget()
        # if isinstance(current_widget, LogWidget):
        #     current_widget.widget().resize(current_widget.widget().sizeHint())

    def create_right_widget(self):
        left_widget = QTabWidget()
        left_widget.resize(QSize(310, 300))
        self.var_defs_tab = ProcessVariablesWidget()
        left_widget.addTab(self.var_defs_tab, gettext("Variables"))
        elements_tab_widget = QTabWidget()
        self._elements_widget = ElementsWidget()
        elements_tab_widget.addTab(self._elements_widget, gettext("Web Elements"))
        self._window_elements_widget = WindowElementsWidget()
        elements_tab_widget.addTab(self._window_elements_widget, gettext("Window Elements"))
        left_widget.addTab(elements_tab_widget, gettext("Element library"))
        self._resource_widget = ProcessResourceWidget()
        left_widget.addTab(self._resource_widget, gettext("Resource library"))
        return left_widget

    @Slot()
    def create_app(self):
        """创建应用"""
        dialog = CreateNewAppDialog(None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            app = dialog.app
            if not self._close_app():
                return
            # 创建主流程
            process_def = app.create_process_def('main')
            app.set_main_process_def(process_def.name)
            self.set_app(app)
            self.do_open_process(process_def)

    def set_app(self, app: App):
        AppContext.set_app(app)
        app.engine.set_logger(LogWidgetLogger(LogLevel.INFO, self.log))
        self.setWindowTitle(f'JimuFlow - {app.app_package.name}')
        self.app = app
        self.component_list_widget.set_app(app)
        self._process_list_view.set_app(app)
        self._config_app_act.setEnabled(True)
        self._new_process_act.setEnabled(True)
        self.app.process_def_config_updated.connect(self.process_def_config_updated)
        self._resource_widget.set_app(app)
        self._elements_widget.set_app(app)
        self._window_elements_widget.set_app(app)

    @Slot()
    def config_app(self):
        """配置应用"""
        dialog = CreateNewAppDialog(self.app, self)
        dialog.exec()
        self.setWindowTitle(f'JimuFlow - {self.app.app_package.name}')

    @Slot()
    def open_app(self):
        workspace_path = Utils.get_workspace_path()
        app_dir = QFileDialog.getExistingDirectory(self, gettext("Open Application"), workspace_path)
        if not app_dir:
            return
        if not self._close_app():
            return
        app = App()
        app.load(Path(app_dir))
        self.set_app(app)
        Utils.set_workspace_path(os.path.dirname(app_dir))
        Utils.add_recent_app(app_dir)

        if app.app_package.main_process:
            main_process_def = app.engine.get_component_def(app.app_package, app.app_package.main_process)
            if main_process_def:
                self.do_open_process(main_process_def)

    @Slot()
    def open_recent_app(self):
        app_path = self.sender().data()
        app = App(self)
        app.load(Path(app_path))
        self.set_app(app)

    @Slot()
    def create_process(self):
        """创建流程"""
        dialog = CreateProcessDialog(self.app, None, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            process_def = dialog.process_def
            self.do_open_process(process_def)

    @Slot()
    def config_current_process(self):
        """配置流程"""
        process_widget = self.process_tab_widget.currentWidget()
        process_def = process_widget.process_def
        self.config_process(process_def)

    @Slot(ProcessDef)
    def config_process(self, process_def: ProcessDef):
        dialog = CreateProcessDialog(self.app, process_def, self)
        dialog.exec()

    @Slot(str)
    def process_def_config_updated(self, process_def: ProcessDef):
        for i in range(self.process_tab_widget.count()):
            process_widget = self.process_tab_widget.widget(i)
            if process_widget.process_def == process_def:
                self.process_tab_widget.setTabText(i, process_def.name + (
                    "*" if process_widget.process_model.dirty else ""))
                return

    @Slot(int)
    def process_tab_changed(self, index: int):
        if index == -1:
            self.var_defs_tab.set_process_model(None)
            self._config_process_act.setEnabled(False)
            self._save_process_act.setEnabled(False)
            self._delete_process_act.setEnabled(False)
            self._run_act.setEnabled(False)
            self._start_debug_act.setEnabled(False)
            self._undo_act.setEnabled(False)
            self._redo_act.setEnabled(False)
            return
        process_widget = self.process_tab_widget.widget(index)
        process_model: ProcessModel = process_widget.process_model
        self.var_defs_tab.set_process_model(process_model)
        self._config_process_act.setEnabled(True)
        self._save_process_act.setEnabled(True)
        self._delete_process_act.setEnabled(True)
        process_model.undo_redo_manager.stack_updated.connect(self._on_undo_redo_stack_updated)
        process_model.undo_redo_manager.notify_stack_updated()
        for i in range(self.process_tab_widget.count()):
            if i == index:
                continue
            other_process_widget = self.process_tab_widget.widget(i)
            other_process_model: ProcessModel = other_process_widget.process_model
            other_process_model.undo_redo_manager.stack_updated.disconnect(self._on_undo_redo_stack_updated)
        if not self.is_debugging():
            self._run_act.setEnabled(True)
            self._start_debug_act.setEnabled(True)

    def _on_undo_redo_stack_updated(self, undo_action: str, redo_action: str):
        if undo_action:
            self._undo_act.setText(gettext("Undo {action}").format(action=undo_action))
            self._undo_act.setEnabled(True)
        else:
            self._undo_act.setText(gettext("Undo"))
            self._undo_act.setEnabled(False)
        if redo_action:
            self._redo_act.setText(gettext("Redo {action}").format(action=redo_action))
            self._redo_act.setEnabled(True)
        else:
            self._redo_act.setText(gettext("Redo"))
            self._redo_act.setEnabled(False)

    @Slot()
    def save_process(self):
        process_widget = self.process_tab_widget.currentWidget()
        process_model: ProcessModel = process_widget.process_model
        process_model.save()

    @Slot(ProcessDef)
    def do_open_process(self, process_def: ProcessDef):
        process_widget, i = self.find_process_widget(process_def)
        if process_widget:
            self.process_tab_widget.setCurrentIndex(i)
            return
        process_model = self.app.open_process_def(process_def)
        process_widget = ProcessFlowWidget(process_model)
        self.process_tab_widget.addTab(process_widget, process_def.name)
        self.process_tab_widget.setCurrentIndex(self.process_tab_widget.count() - 1)
        process_model.dirty_changed.connect(self.on_process_model_dirty_changed)
        self.errors.add_process_model(process_model)
        process_widget.open_process_def.connect(self.do_open_process)

    @Slot(bool)
    def on_process_model_dirty_changed(self, dirty: bool):
        process_model: ProcessModel = self.sender()
        process_widget, index = self.find_process_widget(process_model.process_def)
        if process_widget:
            self.process_tab_widget.setTabText(index, process_model.process_def.name + ("*" if dirty else ""))

    @Slot(int)
    def close_process_tab(self, index: int):
        process_widget = self.process_tab_widget.widget(index)
        process_model: ProcessModel = process_widget.process_model
        if process_model.dirty:
            if QMessageBox.warning(self, gettext("Warning"),
                                   gettext(
                                       'Process {name} has not been saved. Do you want to save this process?').format(
                                       name=process_model.process_def.name),
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.Yes) == QMessageBox.StandardButton.Yes:
                process_model.process_def.save_to_file(process_model.process_def.path)
        self.process_tab_widget.removeTab(index)
        self.errors.remove_process_model(process_model)
        self.app.close_process_def(process_model)

    @Slot()
    def delete_current_process(self):
        process_widget = self.process_tab_widget.currentWidget()
        process_model = process_widget.process_model
        self.delete_process(process_model.process_def)

    @Slot(ProcessDef)
    def delete_process(self, process_def: ProcessDef):
        if QMessageBox.warning(self, gettext("Warning"),
                               gettext('Are you sure you want to delete process {name}?').format(
                                   name=process_def.name),
                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                               QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        process_widget, index = self.find_process_widget(process_def)
        if process_widget:
            self.process_tab_widget.removeTab(index)
            self.errors.remove_process_model(process_widget.process_model)
        self.app.delete_process_def(process_def)

    @Slot()
    def run_process(self):
        if self._running_process:
            return
        process_widget = self.process_tab_widget.currentWidget()
        process_model: ProcessModel = process_widget.process_model
        process = self._create_process(process_model)
        if not process:
            return
        self.log.clear()
        AppContext.engine().logger.level = LogLevel.INFO
        self._running_process = process
        self._run_act.setEnabled(False)
        self._start_debug_act.setEnabled(False)
        self._stop_act.setEnabled(True)

        self._thread = CoroutineThread(process.invoke())
        self._thread.finished.connect(self.on_process_finished)
        self._thread.start()
        self._bottom_tab_widget.setCurrentIndex(1)

    def _create_process(self, process_model: ProcessModel):
        if len(process_model.errors) > 0:
            QMessageBox.warning(self, gettext("Error"), gettext("Process has errors, please fix them first"))
            return
        process_def: ProcessDef = process_model.process_def
        supported, supported_platforms = AppContext.engine().is_process_platform_supported(process_def)
        if not supported:
            QMessageBox.warning(self, gettext("Error"),
                                gettext("Process {name} only supports running on platform {platforms}").format(
                                    name=process_def.name,
                                    platforms=", ".join([i.localized_name() for i in supported_platforms])))
            return
        if len(process_def.input_variables()) == 0:
            inputs = {}
        else:
            process_dialog = StartProcessDialog(process_def, parent=self)
            if process_dialog.exec() != QDialog.DialogCode.Accepted:
                return
            inputs = process_dialog.get_inputs()
        process = AppContext.engine().create_process(process_def, inputs)
        return process

    @Slot()
    def on_process_finished(self):
        self._thread.deleteLater()
        self._thread = None
        self._running_process = None
        self._run_act.setEnabled(True)
        self._start_debug_act.setEnabled(True)
        self._stop_act.setEnabled(False)

    @Slot()
    def start_debug(self):
        if self._running_process:
            return
        process_widget = self.process_tab_widget.currentWidget()
        process_model: ProcessModel = process_widget.process_model
        process = self._create_process(process_model)
        if not process:
            return
        self.log.clear()
        AppContext.engine().logger.level = LogLevel.DEBUG
        self._running_process = process
        self._debugger = ProcessDebugger(process, self)
        self._run_act.setEnabled(False)
        self._start_debug_act.setEnabled(False)
        self._stop_act.setEnabled(True)
        self._thread = CoroutineThread(self._debugger.run())
        self._thread.finished.connect(lambda: self._thread.deleteLater())
        self._thread.start()
        self._bottom_tab_widget.setCurrentIndex(1)

    def is_debugging(self):
        return self._debugger is not None

    @Slot()
    def stop_process(self):
        if self._running_process:
            self._running_process.stop()
            self._running_process = None
        if self._debugger:
            if not self._thread.isFinished():
                debugger = self._debugger
                if not debugger.end:
                    self._thread.loop.call_soon_threadsafe(lambda: debugger.stop())
            self._debugger = None
            self.variables_tab.set_component(None)
        self._run_act.setEnabled(True)
        self._start_debug_act.setEnabled(True)
        self._debug_run_act.setEnabled(False)
        self._stop_act.setEnabled(False)
        self._step_over_act.setEnabled(False)
        self._step_into_act.setEnabled(False)
        self._step_out_act.setEnabled(False)

    def on_debugger_paused(self, step: Component):
        self.debugger_paused.emit(step)

    def on_debugger_resumed(self):
        self.debugger_resumed.emit()

    @Slot()
    def handle_debugger_resumed(self):
        self._debug_run_act.setEnabled(False)
        self._step_over_act.setEnabled(False)
        self._step_into_act.setEnabled(False)
        self._step_out_act.setEnabled(False)

    @Slot(Component)
    def handle_debugger_paused(self, step: Component):
        self._debug_run_act.setEnabled(True)
        self._step_over_act.setEnabled(True)
        self._step_into_act.setEnabled(True)
        self._step_out_act.setEnabled(True)
        self.navigator_to_process_node(step.process.component_id(), step.node.line_no)
        self.variables_tab.set_component(step)

    def find_process_widget(self, process_def: ProcessDef):
        for i in range(self.process_tab_widget.count()):
            process_widget: ProcessFlowWidget = self.process_tab_widget.widget(i)
            if process_widget.process_def == process_def:
                return process_widget, i
        return None, None

    @Slot(str, int)
    def navigator_to_process_node(self, process_id: str, line_no: int):
        process_def: ProcessDef = AppContext.engine().get_component_def(AppContext.app().app_package, process_id)
        process_widget, index = self.find_process_widget(process_def)
        if process_widget is None:
            self.do_open_process(process_def)
            process_widget, _ = self.find_process_widget(process_def)
        else:
            self.process_tab_widget.setCurrentIndex(index)
        node = process_def.get_node_by_line_no(line_no)
        process_widget.select_node(node)

    def on_debugger_ended(self):
        self.debugger_ended.emit()

    @Slot()
    def debug_run(self):
        if self._debugger is None:
            return
        self._thread.loop.call_soon_threadsafe(lambda: self._debugger.run_to_next_breakpoint())

    @Slot()
    def step_over(self):
        if self._debugger is None:
            return
        self._thread.loop.call_soon_threadsafe(lambda: self._debugger.step_over())

    @Slot()
    def step_into(self):
        if self._debugger is None:
            return
        self._thread.loop.call_soon_threadsafe(lambda: self._debugger.step_into())

    @Slot()
    def step_out(self):
        if self._debugger is None:
            return
        self._thread.loop.call_soon_threadsafe(lambda: self._debugger.step_out())

    def dump_dict(self, d):
        if isinstance(d, dict):
            return {k: self.dump_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [self.dump_dict(v) for v in d]
        elif isinstance(d, set):
            return {self.dump_dict(v) for v in d}
        elif isinstance(d, tuple):
            return tuple(self.dump_dict(v) for v in d)
        elif isinstance(d, str):
            return d
        elif isinstance(d, int):
            return d
        elif isinstance(d, float):
            return d
        elif isinstance(d, bool):
            return d
        else:
            return repr(d)

    def _close_app(self):
        if self.app is None:
            return True
        if self._running_process is not None:
            message = gettext('Process {name} is running, do you want to terminate the process?').format(
                name=self._running_process.component_def.name)
            if QMessageBox.warning(self, gettext('Tips'), message,
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.Yes) == QMessageBox.StandardButton.Yes:
                self.stop_process()
                if self._thread:
                    self._thread.wait()
            else:
                return False
        for i in range(self.process_tab_widget.count()):
            self.close_process_tab(0)
        self.setWindowTitle('JimuFlow')
        self.component_list_widget.set_app(None)
        self._process_list_view.set_app(None)
        self.var_defs_tab.set_process_model(None)
        self.log.clear()
        self.variables_tab.set_component(None)
        self._config_app_act.setEnabled(False)
        self._new_process_act.setEnabled(False)
        self.app.process_def_config_updated.disconnect(self.process_def_config_updated)
        self._resource_widget.set_app(None)
        self._elements_widget.set_app(None)
        self._window_elements_widget.set_app(None)
        self.app.deleteLater()
        self.app = None
        AppContext.set_app(None)
        return True

    def closeEvent(self, event):
        if not self._close_app():
            return event.ignore()
        QApplication.quit()
        event.accept()

    @Slot()
    def show_about_dialog(self):
        dialog = AboutDialog()
        dialog.exec()

    @Slot()
    def show_help_dialog(self):
        HelpDialog.show_help('index.html')

    @Slot()
    def _undo(self):
        process_widget = self.process_tab_widget.currentWidget()
        process_model: ProcessModel = process_widget.process_model
        process_model.undo_redo_manager.undo()

    @Slot()
    def _redo(self):
        process_widget = self.process_tab_widget.currentWidget()
        process_model: ProcessModel = process_widget.process_model
        process_model.undo_redo_manager.redo()


def main():
    QApplication.setStyle("Fusion")
    app = QApplication()
    app.setApplicationName("JimuFlow")
    app.setWindowIcon(QIcon(":/icons/jimuflow.png"))
    main_window = MainWindow()
    main_window.resize(1200, 700)
    screen = QApplication.primaryScreen()
    screen_geometry = screen.geometry()
    x = (screen_geometry.width() - main_window.width()) / 2
    y = (screen_geometry.height() - main_window.height()) / 2
    main_window.move(x, y)
    main_window.show()

    old_excepthook = sys.excepthook

    # 异常处理函数
    def handle_exception(exc_type, exc_value, exc_tb):
        old_excepthook(exc_type, exc_value, exc_tb)
        # 如果是未捕获的异常，弹出错误对话框
        if issubclass(exc_type, KeyboardInterrupt):
            return  # 忽略 KeyboardInterrupt（Ctrl+C）

        # 获取异常的详细信息
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

        # 创建一个错误对话框并显示异常信息
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(gettext("Error"))
        msg_box.setText(gettext("An error has occurred!"))
        msg_box.setDetailedText(error_msg)
        msg_box.exec()

    # 设置全局异常处理
    sys.excepthook = handle_exception

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
