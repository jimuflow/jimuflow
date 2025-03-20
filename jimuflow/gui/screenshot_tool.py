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

import sys

from PySide6.QtCore import Qt, QRectF, QPointF, QSizeF, QMarginsF
from PySide6.QtGui import QPainter, QPen, QColor, QTextOption, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QDialog

from jimuflow.locales.i18n import gettext


class ScreenshotWidget(QDialog):
    def __init__(self):
        super().__init__()
        self.accepted_value = QPixmap()
        # 设置窗口属性，使其显示在所有窗口之上
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setGeometry(QApplication.primaryScreen().geometry())
        self.setMouseTracking(True)
        self.begin: QPointF | None = None
        self.end: QPointF | None = None
        self.is_drawing = False
        self.mouse_pos: QPointF | None = None
        self.mouse_color: QColor | None = None
        self.dragging = False
        self.drag_offset: QPointF | None = None
        self.control_point_size = 10
        self.control_points = []
        self.selection_rect: QRectF | None = None
        self.dragging_point_index = -1

        self.toolbar = QWidget(self)
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar_layout = QVBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(5)
        confirm_button = QPushButton(gettext('Save'))
        confirm_button.clicked.connect(self.confirm_screenshot)
        confirm_button.setDefault(True)
        toolbar_layout.addWidget(confirm_button)
        cancel_button = QPushButton(gettext('Cancel'))
        cancel_button.clicked.connect(self.reject)
        toolbar_layout.addWidget(cancel_button)
        self.toolbar.hide()

        # 工具启动时进行全屏截图
        self.screenshot = QApplication.primaryScreen().grabWindow(0)
        self.screenshot_image = self.screenshot.toImage()

        # 设置 macOS 窗口层级
        if sys.platform == 'darwin':
            import objc
            from AppKit import NSApp
            window = objc.objc_object(c_void_p=self.winId().__int__())
            # 通过 NSApp 找到对应的 NSWindow
            windows = NSApp.windows()
            for ns_window in windows:
                if ns_window.contentView() == window:
                    # 使用 kCGWindowLevelModalPanel 对应的层级值
                    window_level = 1000
                    ns_window.setLevel_(window_level)
                    break

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.selection_rect:
                for i, point in enumerate(self.control_points):
                    if point.contains(event.position()):
                        self.dragging = True
                        self.drag_offset = event.position() - point.topLeft()
                        self.dragging_point_index = i
                        return
                if self.selection_rect.contains(event.position()):
                    self.dragging = True
                    self.drag_offset = event.position() - self.selection_rect.topLeft()
                    self.dragging_point_index = -1
                    return
            self.begin = event.position()
            self.end = None
            self.is_drawing = True
            self.selection_rect = None
            self.toolbar.hide()

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end = event.position()
            self.update()
        elif self.dragging:
            if self.selection_rect:
                if self.dragging_point_index == 0:
                    # 左上角控制点
                    new_top_left = event.position() - self.drag_offset + QPointF(self.control_point_size // 2,
                                                                                 self.control_point_size // 2)
                    new_top_left = self.clamp_point(self.rect().toRectF(), new_top_left)
                    self.selection_rect.setTopLeft(new_top_left)
                elif self.dragging_point_index == 1:
                    # 右上角控制点
                    new_top_right = event.position() - self.drag_offset + QPointF(self.control_point_size // 2,
                                                                                  self.control_point_size // 2)
                    new_top_right = self.clamp_point(self.rect().toRectF(), new_top_right)
                    self.selection_rect.setTopRight(new_top_right)
                elif self.dragging_point_index == 2:
                    # 右下角控制点
                    new_bottom_right = event.position() - self.drag_offset + QPointF(self.control_point_size // 2,
                                                                                     self.control_point_size // 2)
                    new_bottom_right = self.clamp_point(self.rect().toRectF(), new_bottom_right)
                    self.selection_rect.setBottomRight(new_bottom_right)
                elif self.dragging_point_index == 3:
                    # 左下角控制点
                    new_bottom_left = event.position() - self.drag_offset + QPointF(self.control_point_size // 2,
                                                                                    self.control_point_size // 2)
                    new_bottom_left = self.clamp_point(self.rect().toRectF(), new_bottom_left)
                    self.selection_rect.setBottomLeft(new_bottom_left)
                elif self.dragging_point_index == -1:
                    # 拖动整个矩形
                    new_top_left = event.position() - self.drag_offset
                    selection_rect_size: QSizeF = self.selection_rect.size()
                    bounding_rect = self.rect().toRectF().marginsRemoved(
                        QMarginsF(-selection_rect_size.width() if selection_rect_size.width() < 0 else 0,
                                  -selection_rect_size.height() if selection_rect_size.height() < 0 else 0,
                                  selection_rect_size.width() if selection_rect_size.width() > 0 else 0,
                                  selection_rect_size.height() if selection_rect_size.height() > 0 else 0))
                    new_top_left = self.clamp_point(bounding_rect, new_top_left)
                    self.selection_rect.moveTo(new_top_left)
                self.update_control_points()
                self.update_toolbar_position()
                self.update()
        if not self.selection_rect:
            self.mouse_pos = event.position()
            device_pixel_ratio = self.screenshot.devicePixelRatio()
            self.mouse_color = self.screenshot_image.pixelColor(int(self.mouse_pos.x() * device_pixel_ratio),
                                                                int(self.mouse_pos.y() * device_pixel_ratio))
            self.update()

    def clamp_point(self, rect: QRectF, point: QPointF):
        x = point.x()
        y = point.y()
        if x < rect.left():
            x = rect.left()
        if x > rect.right():
            x = rect.right()
        if y < rect.top():
            y = rect.top()
        if y > rect.bottom():
            y = rect.bottom()
        return QPointF(x, y)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_drawing:
                self.is_drawing = False
                selection_rect = QRectF(self.begin, event.position()).normalized()
                if self.is_empty_rect(selection_rect):
                    self.begin = None
                else:
                    self.end = event.position()
                    self.selection_rect = selection_rect
                    self.update_control_points()
                    self.toolbar.show()
                    self.update_toolbar_position()
                self.update()
            self.dragging = False

    def update_toolbar_position(self):
        toolbar_rect = self.toolbar.rect()
        top_left = self.selection_rect.normalized().bottomRight() + QPointF(4, -toolbar_rect.height())
        x = top_left.x()
        y = top_left.y()
        if x + toolbar_rect.width() > self.rect().width():
            x = self.rect().width() - toolbar_rect.width()
        if y + toolbar_rect.height() > self.rect().height():
            y = self.rect().height() - toolbar_rect.height()
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        self.toolbar.move(QPointF(x, y).toPoint())

    def update_control_points(self):
        if self.selection_rect:
            top_left = self.selection_rect.topLeft()
            top_right = self.selection_rect.topRight()
            bottom_right = self.selection_rect.bottomRight()
            bottom_left = self.selection_rect.bottomLeft()
            self.control_points = [
                QRectF(top_left.x() - self.control_point_size // 2, top_left.y() - self.control_point_size // 2,
                       self.control_point_size, self.control_point_size),
                QRectF(top_right.x() - self.control_point_size // 2, top_right.y() - self.control_point_size // 2,
                       self.control_point_size, self.control_point_size),
                QRectF(bottom_right.x() - self.control_point_size // 2, bottom_right.y() - self.control_point_size // 2,
                       self.control_point_size, self.control_point_size),
                QRectF(bottom_left.x() - self.control_point_size // 2, bottom_left.y() - self.control_point_size // 2,
                       self.control_point_size, self.control_point_size)
            ]

    def paintEvent(self, event):
        painter = QPainter(self)
        # 绘制全屏截图
        painter.drawPixmap(0, 0, self.screenshot)

        if self.is_drawing and self.end:
            # 绘制半透明背景
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

            # 绘制框选区域的透明矩形
            rect = QRectF(self.begin, self.end).normalized()
            self.draw_rect_content(painter, rect)

            # 绘制正在框选的矩形框
            pen = QPen(Qt.GlobalColor.red, 2)
            painter.setPen(pen)
            painter.drawRect(rect)

            # 显示矩形框的长宽
            self.draw_rect_size_info(painter, rect)

        if self.selection_rect:
            # 绘制半透明背景
            painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

            # 绘制框选区域的透明矩形
            rect = self.selection_rect
            self.draw_rect_content(painter, rect)

            # 绘制框选区域的红色边框
            pen = QPen(Qt.GlobalColor.red, 2)
            painter.setPen(pen)
            painter.drawRect(rect)

            # 显示矩形框的长宽
            self.draw_rect_size_info(painter, rect)

            # 绘制控制点
            for point in self.control_points:
                painter.fillRect(point, Qt.GlobalColor.white)
        else:
            # 显示鼠标位置和颜色
            if self.mouse_pos:
                self.draw_mouse_info(painter)

    def draw_mouse_info(self, painter):
        # 显示鼠标位置和颜色
        if self.selection_rect or not self.mouse_pos:
            return
        text = gettext('Coordinate: ({x},{y}) Color value: {color}').format(x=int(self.mouse_pos.x()),
                                                                            y=int(self.mouse_pos.y()),
                                                                            color=self.mouse_color.name())
        text_width = painter.fontMetrics().horizontalAdvance(text)
        text_height = painter.fontMetrics().height()
        text_rect_height = text_height * 1.3
        text_rect_width = text_width + text_height
        text_rect_left_top = self.mouse_pos + QPointF(0, 4)
        text_rect_x = text_rect_left_top.x()
        text_rect_y = text_rect_left_top.y()
        if text_rect_x + text_rect_width > self.rect().width():
            text_rect_x = self.rect().width() - text_rect_width
        if text_rect_y + text_rect_height > self.rect().height():
            text_rect_y = self.mouse_pos.y() - text_rect_height - 4
        if text_rect_x < 0:
            text_rect_x = 0
        if text_rect_y < 0:
            text_rect_y = 0
        text_rect = QRectF(text_rect_x, text_rect_y, text_rect_width, text_rect_height)
        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(text_rect, text_rect_height / 5, text_rect_height / 5)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        text_option = QTextOption()
        text_option.setWrapMode(QTextOption.WrapMode.NoWrap)
        text_option.setAlignment(Qt.AlignmentFlag.AlignCenter)
        painter.drawText(text_rect, text, text_option)

    def draw_rect_content(self, painter, rect):
        # 绘制框选区域的透明矩形
        rect = rect.normalized()
        painter.drawPixmap(rect.topLeft(), self.crop_screenshot(rect))

    def crop_screenshot(self, rect):
        rect = rect.normalized()
        device_pixel_ratio = self.screenshot.devicePixelRatio()
        scaled_rect = QRectF(
            rect.x() * device_pixel_ratio,
            rect.y() * device_pixel_ratio,
            rect.width() * device_pixel_ratio,
            rect.height() * device_pixel_ratio
        )
        scaled_rect = scaled_rect.toRect()
        if scaled_rect.width() <= 0 or scaled_rect.height() <= 0:
            return QPixmap()
        sub_screenshot = self.screenshot.copy(scaled_rect)
        sub_screenshot.setDevicePixelRatio(device_pixel_ratio)
        return sub_screenshot

    def is_empty_rect(self, rect: QRectF):
        rect = rect.normalized()
        device_pixel_ratio = self.screenshot.devicePixelRatio()
        scaled_rect = QRectF(
            rect.x() * device_pixel_ratio,
            rect.y() * device_pixel_ratio,
            rect.width() * device_pixel_ratio,
            rect.height() * device_pixel_ratio
        )
        scaled_rect = scaled_rect.toRect()
        return scaled_rect.width() <= 0 or scaled_rect.height() <= 0

    def draw_rect_size_info(self, painter, rect):
        # 显示矩形框的长宽
        rect = rect.normalized()
        width = rect.width()
        height = rect.height()
        text = f"{int(width)} * {int(height)}"
        text_width = painter.fontMetrics().horizontalAdvance(text)
        text_height = painter.fontMetrics().height()
        text_rect_height = text_height * 1.3
        text_rect_width = text_width + text_height
        text_rect = QRectF(rect.topLeft() - QPointF(0, text_rect_height + 4),
                           QSizeF(text_rect_width, text_rect_height))
        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(text_rect, text_rect_height / 5, text_rect_height / 5)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        text_option = QTextOption()
        text_option.setWrapMode(QTextOption.WrapMode.NoWrap)
        text_option.setAlignment(Qt.AlignmentFlag.AlignCenter)
        painter.drawText(text_rect, text, text_option)

    def confirm_screenshot(self):
        if self.selection_rect:
            # 从全屏截图中截取选中区域
            screenshot = self.crop_screenshot(self.selection_rect)
            if screenshot.isNull():
                return
            self.accepted_value = screenshot
            self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
            event.accept()
        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            if self.selection_rect:
                self.confirm_screenshot()
                event.accept()
        elif event.key() == Qt.Key.Key_Backspace or event.key() == Qt.Key.Key_Delete:
            if self.selection_rect:
                self.selection_rect = None
                self.toolbar.hide()
                self.dragging = False
                self.is_drawing = False
                self.update()
                event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = ScreenshotWidget()
    widget.show()
    sys.exit(app.exec())
