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

import ctypes
from ctypes import wintypes

import pywinauto
from PySide6.QtCore import Slot, Qt, QRect
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox, QApplication, QGridLayout, \
    QLineEdit, QPushButton
from pywinauto.base_wrapper import BaseWrapper
from pywinauto.uia_element_info import UIAElementInfo
from pywinauto.win32structures import RECT

from jimuflow.common.web_element_utils import build_xpath, get_full_element_xpath, get_relative_xpath
from jimuflow.common.win32_functions import GetCursorPos, GetSystemMetrics
from jimuflow.components.windows_automation.pywinauto_utill import find_elements_by_xpath, get_control_by_position
from jimuflow.gui.window_element_capture_tool import Highlighter, Hooker, get_element_path, HighlightItem
from jimuflow.locales.i18n import gettext


class WindowElementRelativeXpathTool(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pick_mode = None
        self.accepted_xpath = ''
        self._source_element_info = None
        self._target_element_info = None
        self._captured_elements = []
        self.setWindowTitle(gettext("Window Element Relative XPath Tool"))
        main_layout = QVBoxLayout(self)
        help_label = QLabel(gettext(
            'Operation instructions: Ctrl+left-click to get a single element.'))
        help_label.setVisible(False)
        self._help_label = help_label
        main_layout.addWidget(help_label)

        source_element_layout, source_xpath_edit, source_matches_count_label = self._create_source_element_layout()
        main_layout.addLayout(source_element_layout)
        self._source_xpath_edit = source_xpath_edit
        self._source_matches_count_label = source_matches_count_label

        target_element_layout, target_xpath_edit, target_matches_count_label = self._create_target_element_layout()
        main_layout.addLayout(target_element_layout)
        self._target_xpath_edit = target_xpath_edit
        self._target_matches_count_label = target_matches_count_label

        result_layout, result_xpath_edit = self._create_result_layout()
        main_layout.addLayout(result_layout)
        self._result_xpath_edit = result_xpath_edit

        self._highlighter_timer_id = 0
        self._desktop = pywinauto.Desktop(backend='uia')
        monitor = wintypes.RECT()
        monitor.left = 0
        monitor.top = 0
        monitor.right = GetSystemMetrics(0)
        monitor.bottom = GetSystemMetrics(1)
        self._screen_scale = QApplication.primaryScreen().size().width() / monitor.right
        self._monitor = monitor
        self.hooker = None
        self._hover_highlighter = Highlighter()
        self._check_highlighter = Highlighter()
        self._check_highlighter_timer_id = 0
        self.setMinimumWidth(800)

    def _create_source_element_layout(self):
        source_element_layout = QGridLayout()
        source_element_layout.setSpacing(4)
        xpath_label = QLabel(gettext('Source Element XPath: '))
        xpath_edit = QLineEdit()
        xpath_edit.setPlaceholderText(
            gettext('Click the Capture Element button to obtain the XPath of the source element'))
        xpath_edit.editingFinished.connect(self._update_result)
        matches_count_label = QLabel()
        pick_button = QPushButton(gettext('Capture Source Element'))
        pick_button.setToolTip(gettext('Capture the source element'))
        pick_button.clicked.connect(self._pick_source_element_xpath)
        match_button = QPushButton(gettext('Match'))
        match_button.setToolTip(gettext('Match the source element'))
        match_button.clicked.connect(self._on_source_match_button_clicked)
        self._set_matches_count(matches_count_label, 0)
        source_element_layout.addWidget(xpath_label, 0, 0, 1, 1)
        source_element_layout.addWidget(xpath_edit, 0, 1, 1, 1)
        source_element_layout.addWidget(matches_count_label, 0, 2, 1, 1)
        source_element_layout.addWidget(pick_button, 0, 3, 1, 1)
        source_element_layout.addWidget(match_button, 0, 4, 1, 1)
        return source_element_layout, xpath_edit, matches_count_label

    def _create_target_element_layout(self):
        target_element_layout = QGridLayout()
        target_element_layout.setSpacing(4)
        xpath_label = QLabel(gettext('Target Element XPath: '))
        xpath_edit = QLineEdit()
        xpath_edit.setPlaceholderText(
            gettext('Click the Capture Element button to obtain the XPath of the target element'))
        xpath_edit.editingFinished.connect(self._update_result)
        matches_count_label = QLabel()
        pick_button = QPushButton(gettext('Capture Target Element'))
        pick_button.setToolTip(gettext('Capture the target element'))
        pick_button.clicked.connect(self._pick_target_element_xpath)
        match_button = QPushButton(gettext('Match'))
        match_button.setToolTip(gettext('Match the target element'))
        match_button.clicked.connect(self._on_target_match_button_clicked)
        self._set_matches_count(matches_count_label, 0)
        target_element_layout.addWidget(xpath_label, 0, 0, 1, 1)
        target_element_layout.addWidget(xpath_edit, 0, 1, 1, 1)
        target_element_layout.addWidget(matches_count_label, 0, 2, 1, 1)
        target_element_layout.addWidget(pick_button, 0, 3, 1, 1)
        target_element_layout.addWidget(match_button, 0, 4, 1, 1)
        return target_element_layout, xpath_edit, matches_count_label

    def _create_result_layout(self):
        result_layout = QGridLayout()
        result_layout.setSpacing(4)
        xpath_label = QLabel(gettext('Relative XPath: '))
        xpath_edit = QLineEdit()
        xpath_edit.setReadOnly(True)
        xpath_edit.setPlaceholderText(gettext('Relative XPath of the target element relative to the source element'))
        accept_button = QPushButton(gettext('Accept'))
        accept_button.setToolTip(gettext('Accept the relative XPath and close the dialog'))
        accept_button.clicked.connect(self._accept_result_xpath)
        close_button = QPushButton(gettext('Close'))
        close_button.clicked.connect(self.reject)
        result_layout.addWidget(xpath_label, 0, 0, 1, 1)
        result_layout.addWidget(xpath_edit, 0, 1, 1, 1)
        result_layout.addWidget(accept_button, 0, 2, 1, 1)
        result_layout.addWidget(close_button, 0, 3, 1, 1)
        return result_layout, xpath_edit

    @Slot()
    def _pick_source_element_xpath(self):
        self._pick_mode = 'pick_source'
        self._start_capture()

    @Slot()
    def _pick_target_element_xpath(self):
        self._pick_mode = 'pick_target'
        self._start_capture()

    def _set_matches_count(self, label: QLabel, count: int):
        label.setText(gettext('Matches count: {}').format(count))

    @Slot()
    def _update_result(self):
        self._result_xpath_edit.setText(
            get_relative_xpath(self._source_xpath_edit.text(), self._target_xpath_edit.text()))

    def _start_hooker(self):
        if self.hooker is not None:
            return
        self.hooker = Hooker(self)
        self.hooker.ctrl_left_clicked.connect(self.on_ctrl_left_clicked)
        self.hooker.start()

    def _stop_hooker(self):
        if self.hooker is None:
            return
        self.hooker.quit()
        self.hooker.wait()
        self.hooker = None

    def _start_highlighter(self):
        if self._highlighter_timer_id != 0:
            return
        self._highlighter_timer_id = self.startTimer(300)

    def _stop_highlighter(self):
        if self._highlighter_timer_id == 0:
            return
        self.killTimer(self._highlighter_timer_id)
        self._highlighter_timer_id = 0
        self._hover_highlighter.clear()

    def timerEvent(self, event):
        if event.timerId() == self._highlighter_timer_id:
            self._do_highlight()
        elif event.timerId() == self._check_highlighter_timer_id:
            self._stop_check_highlighter_timer()

    def _do_highlight(self):
        cursor_point = wintypes.POINT()
        GetCursorPos(ctypes.byref(cursor_point))
        control = get_control_by_position(cursor_point.x, cursor_point.y)
        if control and control.is_visible():
            self._hover_highlighter.highlight([HighlightItem.from_control(control)])
        else:
            self._hover_highlighter.highlight([])

    def _get_control_rect(self, control: BaseWrapper):
        rect: RECT = control.rectangle()
        return QRect(round(rect.left * self._screen_scale), round(rect.top * self._screen_scale),
                     round(rect.width() * self._screen_scale),
                     round(rect.height() * self._screen_scale))

    def closeEvent(self, e):
        self._stop_capture()
        self._stop_check_highlighter_timer()
        super().closeEvent(e)

    def done(self, r):
        self._stop_capture()
        self._stop_check_highlighter_timer()
        super().done(r)

    def _start_capture(self):
        self._help_label.setVisible(True)
        self._start_hooker()
        self._start_highlighter()

    def _stop_capture(self):
        self._stop_hooker()
        self._stop_highlighter()
        self._help_label.setVisible(False)

    @Slot(int, int)
    def on_ctrl_left_clicked(self, x, y):
        element_info = self._capture_element_by_position(x, y)
        full_xpath = get_full_element_xpath(element_info['windowPath'] + element_info['elementPath'])
        if self._pick_mode == 'pick_source':
            self._source_element_info = element_info
            self._source_xpath_edit.setText(full_xpath)
            self._set_matches_count(self._source_matches_count_label, 1)
        else:
            self._target_element_info = element_info
            self._target_xpath_edit.setText(full_xpath)
            self._set_matches_count(self._target_matches_count_label, 1)
        self._update_result()
        self._stop_capture()
        self._pick_mode = None
        self.raise_()
        self.activateWindow()

    def _capture_element_by_position(self, x, y):
        control: BaseWrapper = get_control_by_position(x, y)
        control.set_focus()
        element: UIAElementInfo = control.element_info
        window_path, element_path = get_element_path(element)
        element_info = {
            "windowXPath": build_xpath(window_path),
            "elementXPath": build_xpath(element_path),
            "windowPath": window_path,
            "elementPath": element_path,
        }
        return element_info

    @Slot()
    def _on_source_match_button_clicked(self):
        if self._source_element_info:
            self._check_element_info(self._source_element_info)

    @Slot()
    def _on_target_match_button_clicked(self):
        if self._target_element_info:
            self._check_element_info(self._target_element_info)

    @Slot()
    def _check_element_info(self, element_info: dict):
        self._stop_check_highlighter_timer()
        controls = find_elements_by_xpath(element_info['windowXPath'], element_info['elementXPath'])
        if not controls:
            QMessageBox.warning(self, gettext("Error"), gettext("Elements not found!"))
            return
        items = [HighlightItem.from_control(control) for control in controls if control.is_visible()]
        self._check_highlighter.highlight(items)
        self._check_highlighter_timer_id = self.startTimer(2000)

    def _stop_check_highlighter_timer(self):
        if self._check_highlighter_timer_id != 0:
            self.killTimer(self._check_highlighter_timer_id)
            self._check_highlighter_timer_id = 0
        self._check_highlighter.clear()

    @Slot()
    def _accept_result_xpath(self):
        self.accepted_xpath = self._result_xpath_edit.text().strip()
        self.accept()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = WindowElementRelativeXpathTool()
    window.show()
    sys.exit(app.exec())
