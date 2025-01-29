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
import re
import tempfile
from ctypes import wintypes
from pathlib import Path

import psutil
import pywinauto
from PIL import Image
from PySide6.QtCore import QThread, Signal, Slot, Qt, QRect
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QMessageBox, QDialogButtonBox, QApplication
from pywinauto.base_wrapper import BaseWrapper
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.uia_element_info import UIAElementInfo
from pywinauto.win32defines import WM_GETICON, ICON_BIG, GCL_HICON
from pywinauto.win32functions import SendMessage

from jimuflow.common.web_element_utils import build_xpath
from jimuflow.common.win32_functions import GetCursorPos, GetSystemMetrics, GetClassLong
from jimuflow.components.windows_automation.pywinauto_utill import find_elements_by_xpath, get_control_by_position
from jimuflow.gui.window_element_editor import WindowElementEditor
from jimuflow.gui.window_utils import draw_outline_rect, get_control_rect
from jimuflow.gui.windows_hooks import Hook, KeyboardEvent, MouseEvent
from jimuflow.locales.i18n import gettext

localized_control_types = {
    "Button": gettext('Button'),
    "Calendar": gettext('Calendar'),
    "CheckBox": gettext('CheckBox'),
    "ComboBox": gettext('ComboBox'),
    "DataGrid": gettext('DataGrid'),
    "DataItem": gettext('DataItem'),
    "Document": gettext('Document'),
    "Edit": gettext('Edit'),
    "Group": gettext('Group'),
    "Header": gettext('Header'),
    "HeaderItem": gettext('HeaderItem'),
    "Hyperlink": gettext('Hyperlink'),
    "Image": gettext('Image'),
    "List": gettext('List'),
    "ListItem": gettext('ListItem'),
    "Menu": gettext('Menu'),
    "MenuBar": gettext('MenuBar'),
    "MenuItem": gettext('MenuItem'),
    "Pane": gettext('Pane'),
    "ProgressBar": gettext('ProgressBar'),
    "RadioButton": gettext('RadioButton'),
    "ScrollBar": gettext('ScrollBar'),
    "SemanticZoom": gettext('SemanticZoom'),
    "Separator": gettext('Separator'),
    "Slider": gettext('Slider'),
    "Spinner": gettext('Spinner'),
    "SplitButton": gettext('SplitButton'),
    "StatusBar": gettext('StatusBar'),
    "Tab": gettext('Tab'),
    "TabItem": gettext('TabItem'),
    "Table": gettext('Table'),
    "Text": gettext('Text'),
    "Thumb": gettext('Thumb'),
    "TitleBar": gettext('TitleBar'),
    "ToolBar": gettext('ToolBar'),
    "ToolTip": gettext('ToolTip'),
    "Tree": gettext('Tree'),
    "TreeItem": gettext('TreeItem'),
    "Window": gettext('Window'),
}


class Hooker(QThread):
    ctrl_left_clicked = Signal(int, int)
    shift_left_clicked = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hk = Hook()
        self.hk.handler = self._on_hook_event
        self.down_keys = {}

    def is_ctrl_down(self):
        return self.down_keys.get('Lcontrol', False) or self.down_keys.get('Rcontrol', False) or self.down_keys.get(
            'CONTROL', False) or self.down_keys.get('Ctrl', False)

    def is_shift_down(self):
        return self.down_keys.get('Lshift', False) or self.down_keys.get('Rshift', False) or self.down_keys.get(
            'SHIFT', False) or self.down_keys.get('Shift', False)

    def _on_hook_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.event_type == 'key down':
                self.down_keys[event.current_key] = True
            elif event.event_type == 'key up':
                self.down_keys[event.current_key] = False
        elif isinstance(event, MouseEvent):
            if event.current_key == 'LButton':
                if self.is_ctrl_down():
                    if event.event_type == 'key up':
                        self.ctrl_left_clicked.emit(event.mouse_x, event.mouse_y)
                    return True
                elif self.is_shift_down():
                    if event.event_type == 'key up':
                        self.shift_left_clicked.emit(event.mouse_x, event.mouse_y)
                    return True

    def run(self):
        self.hk.hook(keyboard=True, mouse=True)

    def quit(self):
        self.hk.stop()
        super().quit()


def get_element_node(element: UIAElementInfo, with_position=True):
    path_node = {
        "element": element.control_type,
        "enabled": True,
        "predicates": []
    }
    automation_id = element.automation_id
    if automation_id:
        path_node["predicates"].append(['automation_id', '=', automation_id, True])
    class_name = element.class_name
    if class_name:
        path_node["predicates"].append(['class_name', '=', class_name, True])
    control_id = element.control_id
    if control_id:
        path_node["predicates"].append(['control_id', '=', control_id, False])
    framework_id = element.framework_id
    if framework_id:
        path_node["predicates"].append(['framework_id', '=', framework_id, False])
    name = element.name
    if name:
        path_node["predicates"].append(['name', '=', name, True])
    parent = element.parent
    if parent == UIAElementInfo():
        path_node["handle"] = element.handle
    if with_position:
        siblings = parent.children()
        if len(siblings) == 1:
            path_node["predicates"].append(['position()', '=', '1', False])
        else:
            count = 0
            position = 0
            for i in range(len(siblings)):
                if siblings[i].control_type == element.control_type:
                    count += 1
                if siblings[i] == element:
                    position = count
            path_node["predicates"].append(['position()', '=', str(position), count > 1])
    return parent, path_node


def get_element_path(element: UIAElementInfo):
    window_path = []
    element_path = []
    root = UIAElementInfo()
    in_window_path = False
    while element != root:
        if not in_window_path:
            in_window_path = UIAWrapper(element).is_dialog()
        parent, path_node = get_element_node(element, not in_window_path)
        if in_window_path:
            window_path.append(path_node)
        else:
            element_path.append(path_node)
        element = parent
    window_path.reverse()
    element_path.reverse()
    return window_path, element_path


class ICONINFO(ctypes.Structure):
    _fields_ = [
        ("fIcon", wintypes.BOOL),
        ("xHotspot", wintypes.DWORD),
        ("yHotspot", wintypes.DWORD),
        ("hbmMask", wintypes.HBITMAP),
        ("hbmColor", wintypes.HBITMAP),
    ]


class BITMAP(ctypes.Structure):
    _fields_ = [
        ("bmType", wintypes.LONG),
        ("bmWidth", wintypes.LONG),
        ("bmHeight", wintypes.LONG),
        ("bmWidthBytes", wintypes.LONG),
        ("bmPlanes", wintypes.WORD),
        ("bmBitsPixel", wintypes.WORD),
        ("bmBits", wintypes.LPVOID),
    ]


# WM_GETICON = 0x007F
# ICON_BIG = 1
# GCL_HICON = -14


def get_window_icon(hwnd):
    # 尝试获取窗口的图标
    # hicon = win32gui.SendMessage(hwnd, WM_GETICON, ICON_BIG, 0)
    hicon = SendMessage(hwnd, WM_GETICON, ICON_BIG, 0)
    if not hicon:
        # hicon = win32gui.GetClassLong(hwnd, GCL_HICON)
        hicon = GetClassLong(hwnd, GCL_HICON)

    if not hicon:
        return None

    return extract_icon_to_file(hicon)


def extract_icon_to_file(hicon):
    # 获取图标信息
    icon_info = ICONINFO()
    if not ctypes.windll.user32.GetIconInfo(hicon, ctypes.byref(icon_info)):
        return None

    # 获取位图信息
    bitmap = BITMAP()
    hbmColor = icon_info.hbmColor

    if not hbmColor:
        return None
    ctypes.windll.gdi32.GetObjectW(ctypes.wintypes.HANDLE(hbmColor), ctypes.sizeof(BITMAP), ctypes.byref(bitmap))

    # 读取位图数据
    width = bitmap.bmWidth
    height = bitmap.bmHeight
    size = bitmap.bmWidthBytes * height
    buffer = ctypes.create_string_buffer(size)
    ctypes.windll.gdi32.GetBitmapBits(ctypes.wintypes.HBITMAP(hbmColor), size, buffer)

    # 创建图像
    image = Image.frombytes("RGBA", (width, height), buffer, "raw", "BGRA")

    # 保存为 png 文件
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        image.save(temp_file.name, format="png")
        return Path(temp_file.name)


def merge_elements(first: dict, second: dict):
    if first['windowXPath'] != second['windowXPath'] or first['elementXPath'] == second['elementXPath'] or len(
            first['elementPath']) != len(second['elementPath']):
        return None
    for i in range(len(first['elementPath'])):
        first_node = first['elementPath'][i]
        second_node = second['elementPath'][i]
        if first_node['element'] != second_node['element']:
            return None
        for first_pred in first_node['predicates']:
            second_pred = next((pred for pred in second_node['predicates'] if pred[0] == first_pred[0]), None)
            if second_pred is None:
                first_pred[3] = False
            elif second_pred != first_pred:
                first_pred[3] = False
                second_pred[3] = False
        for second_pred in second_node['predicates']:
            first_pred = next((pred for pred in first_node['predicates'] if pred[0] == second_pred[0]), None)
            if first_pred is None:
                second_pred[3] = False
            elif second_pred != first_pred:
                first_pred[3] = False
                second_pred[3] = False

    merged_element = first

    element_type = first['elementType']
    merged_element['name'] = localized_control_types.get(element_type, element_type) + '_' + first['name'] + '_' + \
                             second['name'] + '_' + gettext('Element List')
    merged_element['elementXPath'] = build_xpath(merged_element["elementPath"])
    return merged_element


class HighlightItem:
    def __init__(self, name: str, rect: QRect, color=Qt.GlobalColor.red, thickness=2):
        self.name = name
        self.rect = rect
        self.color = color
        self.thickness = thickness

    def __eq__(self, other):
        return self.name == other.name and self.rect == other.rect and self.color == other.color and self.thickness == other.thickness

    def __hash__(self):
        return hash((self.name, self.rect, self.color, self.thickness))

    @classmethod
    def from_control(cls, control: BaseWrapper, color=Qt.GlobalColor.red, thickness=2):
        rect = get_control_rect(control)
        control_type = control.element_info.control_type
        name = localized_control_types.get(control_type, control_type)
        return cls(name, rect, color, thickness)


class Highlighter:
    def __init__(self):
        self.highlighted_items = {}

    def highlight(self, items: list[HighlightItem]):
        items_to_delete = [item for item, borders in self.highlighted_items.items() if item not in items]
        for item in items_to_delete:
            for border in self.highlighted_items[item]:
                border.close()
                border.deleteLater()
            del self.highlighted_items[item]
        for item in items:
            if item not in self.highlighted_items:
                self.highlighted_items[item] = draw_outline_rect(item.name, item.rect, item.color, item.thickness)
            else:
                for border in self.highlighted_items[item]:
                    border.raise_()

    def clear(self):
        for item, borders in self.highlighted_items.items():
            for border in borders:
                border.close()
                border.deleteLater()
        self.highlighted_items.clear()


class WindowElementCaptureTool(QDialog):
    def __init__(self, element_info=None, parent=None):
        super().__init__(parent)
        self.element_info = element_info
        self._captured_elements = []
        self.setWindowTitle(gettext("Window Element Capture Tool"))
        main_layout = QVBoxLayout(self)
        help_label = QLabel(gettext(
            'Operation instructions: Ctrl+left-click to get a single element, and Shift+left-click two elements to get multiple similar elements.'))
        if element_info:
            help_label.setVisible(False)
        self._help_label = help_label
        main_layout.addWidget(help_label)
        self._element_editor = WindowElementEditor()
        self._element_editor.setVisible(False)
        self._element_editor.check_element_clicked.connect(self._check_element_info)
        self._element_editor.capture_element_clicked.connect(self._recapture_element)
        main_layout.addWidget(self._element_editor)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText(gettext('Ok'))
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(gettext('Cancel'))
        main_layout.addWidget(button_box)
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
        if element_info:
            self._edit_element_info(element_info)
        else:
            self._start_capture()

    def _start_hooker(self):
        if self.hooker is not None:
            return
        self.hooker = Hooker(self)
        self.hooker.ctrl_left_clicked.connect(self.on_ctrl_left_clicked)
        self.hooker.shift_left_clicked.connect(self.on_shift_left_clicked)
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

    def closeEvent(self, e):
        self._stop_capture()
        self._stop_check_highlighter_timer()
        super().closeEvent(e)

    def done(self, r):
        self._stop_capture()
        self._stop_check_highlighter_timer()
        super().done(r)

    def _start_capture(self):
        self._start_hooker()
        self._start_highlighter()

    def _stop_capture(self):
        self._stop_hooker()
        self._stop_highlighter()

    @Slot(int, int)
    def on_ctrl_left_clicked(self, x, y):
        element_info = self._capture_element_by_position(x, y)
        element_info["name"] = localized_control_types.get(element_info['elementType'],
                                                           element_info['elementType']) + '_' + element_info['name']
        self.element_info = element_info
        self._edit_element_info(element_info)
        self._stop_capture()

    @Slot(int, int)
    def on_shift_left_clicked(self, x, y):
        self._captured_elements.append(self._capture_element_by_position(x, y))
        if len(self._captured_elements) == 2:
            merged_element = merge_elements(*self._captured_elements)
            self._captured_elements.clear()
            if not merged_element:
                QMessageBox.warning(self, gettext("Error"), gettext(
                    "The second element does not match the first element, please select again!"))
            else:
                self.element_info = merged_element
                self._edit_element_info(merged_element)
                self._stop_capture()

    def _capture_element_by_position(self, x, y):
        control = get_control_by_position(x, y)
        control.set_focus()
        element: UIAElementInfo = control.element_info
        pid = element.process_id
        process_name = psutil.Process(pid).name()
        if process_name.lower().endswith(".exe"):
            process_name = process_name[:-4]
        window_path, element_path = get_element_path(element)
        window_handle = window_path[0].pop("handle")
        name = element.name
        if not name:
            name = element.class_name
        if name:
            name = re.sub(r'\s+', '_', name)[:15]
        else:
            name = ""
        element_info = {
            "groupName": process_name,
            "groupIcon": get_window_icon(window_handle),
            "name": name,
            "elementType": element.control_type,
            "windowXPath": build_xpath(window_path),
            "elementXPath": build_xpath(element_path),
            "windowPath": window_path,
            "elementPath": element_path,
            "useCustomWindowXPath": False,
            "customWindowXPath": "",
            "useCustomElementXPath": False,
            "customElementXPath": "",
            "snapshot": self._grab_screenshot(control)
        }
        return element_info

    def _grab_screenshot(self, control: BaseWrapper):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            control.capture_as_image().save(temp_file.name, format="png")
            return temp_file.name

    def _edit_element_info(self, element_info: dict):
        self._help_label.setVisible(False)
        self._element_editor.set_element_info(element_info)
        self._element_editor.setVisible(True)
        self.raise_()
        self.activateWindow()

    @Slot()
    def _check_element_info(self):
        self._stop_check_highlighter_timer()
        controls = find_elements_by_xpath(self.element_info['windowXPath'], self.element_info['elementXPath'])
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
    def _recapture_element(self):
        self._help_label.setVisible(True)
        self._element_editor.setVisible(False)
        self._start_capture()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = WindowElementCaptureTool()
    window.show()
    sys.exit(app.exec())
