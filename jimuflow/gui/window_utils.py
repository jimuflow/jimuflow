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

from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter, Qt, QPalette
from PySide6.QtWidgets import QWidget, QApplication, QLabel
from pywinauto.base_wrapper import BaseWrapper
from pywinauto.win32defines import LOGPIXELSX
from pywinauto.win32functions import GetDC
from pywinauto.win32structures import RECT

from jimuflow.common.win32_functions import GetSystemMetrics, GetDeviceCaps, ReleaseDC


class OutlineNameWindow(QLabel):
    def __init__(self, name: str):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowTransparentForInput | Qt.WindowType.WindowDoesNotAcceptFocus)
        self.setText(name)
        self.setContentsMargins(5, 2, 5, 2)
        self.setBackgroundRole(QPalette.ColorRole.Highlight)
        self.setForegroundRole(QPalette.ColorRole.HighlightedText)
        self.setAutoFillBackground(True)


class OutlineBorderWindow(QWidget):
    def __init__(self, background_color=Qt.GlobalColor.red):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowTransparentForInput | Qt.WindowType.WindowDoesNotAcceptFocus)
        self._background_color = background_color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._background_color)


def draw_outline_rect(name: str, rect: QRect, color=Qt.GlobalColor.red, thickness=2):
    name_window = OutlineNameWindow(name)
    name_window_size = name_window.sizeHint()
    name_window.setGeometry(
        QRect(rect.left() - thickness, rect.top() - thickness - name_window_size.height(), name_window_size.width(),
              name_window_size.height()))
    top_border = OutlineBorderWindow(color)
    top_border.setGeometry(
        QRect(rect.left() - thickness, rect.top() - thickness, rect.width() + thickness, thickness))
    right_border = OutlineBorderWindow(color)
    right_border.setGeometry(QRect(rect.right(), rect.top() - thickness, thickness, rect.height() + thickness))
    bottom_border = OutlineBorderWindow(color)
    bottom_border.setGeometry(QRect(rect.left(), rect.bottom(), rect.width() + thickness - 1, thickness))
    left_border = OutlineBorderWindow(color)
    left_border.setGeometry(QRect(rect.left() - thickness, rect.top(), thickness, rect.height() + thickness - 1))
    name_window.show()
    top_border.show()
    right_border.show()
    bottom_border.show()
    left_border.show()
    return name_window, top_border, right_border, bottom_border, left_border


def close_outline_rect(rect):
    for border in rect:
        border.close()
        border.deleteLater()


def get_control_rect(control: BaseWrapper):
    screen_resolution_width = GetSystemMetrics(0)
    screen_scale = QApplication.primaryScreen().size().width() / screen_resolution_width
    rect: RECT = control.rectangle()
    return QRect(round(rect.left * screen_scale),
                 round(rect.top * screen_scale),
                 round(rect.width() * screen_scale),
                 round(rect.height() * screen_scale))


def get_physical_pixel_ratio():
    hdc = GetDC(None)
    logical_dpi = GetDeviceCaps(hdc, LOGPIXELSX)
    ReleaseDC(None, hdc)
    return logical_dpi / 96


def get_logical_pixel_ratio():
    hdc = GetDC(None)
    logical_dpi = GetDeviceCaps(hdc, LOGPIXELSX)
    ReleaseDC(None, hdc)
    return 96 / logical_dpi


def physical_pixels_to_logical_pixels(physical_width):
    return round(physical_width * get_logical_pixel_ratio())


def logical_pixels_to_physical_pixels(logical_width):
    return round(logical_width * get_physical_pixel_ratio())
