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

from PySide6.QtCore import Qt, QPoint, QRect, QSize, Slot, QMargins, Signal, QModelIndex, QEvent
from PySide6.QtGui import QStandardItemModel, QStandardItem, QKeySequence
from PySide6.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QStylePainter, QStyle, QSizePolicy, \
    QTextEdit, QCompleter, QPushButton, QHBoxLayout, QStyleOptionFrame, QListView, QMessageBox

from jimuflow.datatypes import builtin_data_type_registry, DataTypeRegistry
from jimuflow.definition import VariableDef
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.expression import expr_parser, ExpressionTokenizer, escape_string, validate_expression, \
    get_property_suggestions


class ExpressionToken:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f'Token("{self.data}")'


class ExpressionEditPopup(QWidget):
    item_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(Qt.WindowType.Popup)
        self._list_view = QListView()
        self._list_view.activated.connect(self.on_item_activated)
        self._list_model = QStandardItemModel()
        self._list_view.setModel(self._list_model)
        self.layout.addWidget(self._list_view)
        self._list_view.installEventFilter(self)

    def set_variables(self, variables: list[VariableDef]):
        self._list_model.clear()
        for var_def in variables:
            item = QStandardItem(f'{var_def.name}\t{gettext("Variable")}')
            item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self._list_model.appendRow(item)

    @Slot(QModelIndex)
    def on_item_activated(self, index: QModelIndex):
        self.hide()
        token = self._list_model.itemFromIndex(index).text()
        tab_idx = token.find('\t')
        if tab_idx > 0:
            token = token[:tab_idx]
        self.item_selected.emit(token)

    def eventFilter(self, watched, event):
        if watched == self._list_view:
            if event.type() == QEvent.Type.KeyPress:
                if ((
                        event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Tab)
                        and self._list_view.currentIndex().isValid()):
                    self.hide()
                    self.item_selected.emit(self._list_model.itemFromIndex(self._list_view.currentIndex()).text())
                    return True
                elif event.key() == Qt.Key.Key_Escape:
                    self.hide()
                    return True
        return False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down:
            # 选择list_view的第一个元素
            self._list_view.setFocus()
            self._list_view.setCurrentIndex(self._list_view.model().index(0, 0))
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.hide()
            event.accept()
        else:
            event.ignore()


class ExpressionEdit(QWidget):
    verticalMargin = 3
    horizontalMargin = 3

    def __init__(self):
        super().__init__()
        self._placeholder_text = ""
        self.frame = True
        self.readOnly = False
        self.textMargins = QMargins(0, 0, 0, 0)
        self.alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        self._content = []
        self._content_rect: list[QRect] = []
        self._scroll_x = 0
        self._cursor_pos = 0
        self._cursor_x = 0
        self._content_spacing = 4
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._cursor_timer = 0
        self._cursor_width = 1
        self._show_cursor = False
        self._select_anchor = -1
        self._select_end = -1
        self._preedit_start = 0
        self._preedit_end = 0
        self._variables: list[VariableDef] = []
        self._type_registry = builtin_data_type_registry
        self._layout_timer = 0
        self._icon_rect = QRect()
        self._icon_spacing = 5
        self._icon_text = '{x}'
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled)
        self._completer_model = self.create_completer_model()
        self.completer = QCompleter(self._completer_model, self)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        self.completer.activated.connect(self.on_completer_activated)
        self.completer.setWidget(self)
        self._variable_popup = ExpressionEditPopup(self)
        self._variable_popup.item_selected.connect(self.on_completer_activated)
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self.setMouseTracking(True)

    def setPlaceholderText(self, text: str):
        self._placeholder_text = text
        self.update()

    def initStyleOption(self, option: QStyleOptionFrame):
        option.initFrom(self)
        option.rect = self.contentsRect()
        option.lineWidth = self.style().pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth, option,
                                                    self) if self.frame else 0
        option.midLineWidth = 0
        option.state |= QStyle.StateFlag.State_Sunken
        if self.readOnly:
            option.state |= QStyle.StateFlag.State_ReadOnly
        option.features = QStyleOptionFrame.FrameFeature.None_

    def setText(self, text: str):
        self.set_expression(text)

    def text(self) -> str:
        return self.get_expression()

    def set_expression(self, expression: str):
        if expression:
            try:
                tree = expr_parser.parse(expression)
                tokens = ExpressionTokenizer().transform(tree)
                if not isinstance(tokens, list):
                    tokens = [tokens]
            except:
                tokens = [expression]
        else:
            tokens = []
        self._content = [token if isinstance(token, str) else ExpressionToken(token.data) for token in tokens]
        self._content_rect: list[QRect] = []
        self._scroll_x = 0
        self._cursor_pos = 0
        self._cursor_x = 0
        self._select_anchor = -1
        self._select_end = -1
        self._preedit_start = -1
        self._preedit_end = -1
        self._do_layout()

    def get_expression(self):
        return " ".join(
            item.data if isinstance(item, ExpressionToken) else escape_string(item) for item in self._content)

    def create_completer_model(self):
        model = QStandardItemModel(0, 2, self)
        model.appendRow([QStandardItem("("), QStandardItem("运算符")])
        model.appendRow([QStandardItem(")"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("+"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("-"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("*"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("/"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("&&"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("||"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("!"), QStandardItem("运算符")])
        model.appendRow([QStandardItem(">"), QStandardItem("运算符")])
        model.appendRow([QStandardItem(">="), QStandardItem("运算符")])
        model.appendRow([QStandardItem("<"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("<="), QStandardItem("运算符")])
        model.appendRow([QStandardItem("=="), QStandardItem("运算符")])
        model.appendRow([QStandardItem("!="), QStandardItem("运算符")])
        model.appendRow([QStandardItem("["), QStandardItem("运算符")])
        model.appendRow([QStandardItem("]"), QStandardItem("运算符")])
        model.appendRow([QStandardItem("."), QStandardItem("运算符")])
        for var_def in self._variables:
            model.appendRow([QStandardItem(var_def.name), QStandardItem("变量")])
        return model

    def _show_property_suggestions(self):
        property_suggestions = get_property_suggestions(self.get_expression(), self._variables, self._type_registry)
        if not property_suggestions:
            return
        model = QStandardItemModel(0, 2, self)
        for prop in property_suggestions:
            model.appendRow([QStandardItem(prop.name), QStandardItem(prop.description)])
        self.completer.setModel(model)
        self.completer.setCompletionPrefix("")
        self.completer.complete()

    def _show_normal_suggestions(self, text):
        self.completer.setModel(self._completer_model)
        self.completer.setCompletionPrefix(text)
        self.completer.complete()

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._variables = variables
        self._type_registry = type_registry
        self._completer_model = self.create_completer_model()
        self.completer.setModel(self._completer_model)
        self._variable_popup.set_variables(variables)

    def on_completer_activated(self, text):
        if self.has_selection():
            self.delete_selection()
        if len(self._content) == 0:
            self._content.append(ExpressionToken(text))
            self._cursor_pos = 1
            if text == '(':
                self._content.append(ExpressionToken(")"))
            elif text == '[':
                self._content.append(ExpressionToken("]"))
            self._do_layout()
            if text == '.':
                self._show_property_suggestions()
            return
        # 找到光标所在元素位置
        item_index, cursor_index_in_item = self._cursor_item_index(self._cursor_pos)
        # 如果光标位于末尾，或者当前元素是个token，则往前查找字符串元素
        if item_index == len(self._content) or isinstance(self._content[item_index], ExpressionToken):
            if item_index > 0:
                prev_item = self._content[item_index - 1]
                if isinstance(prev_item, str):
                    item_index = item_index - 1
                    cursor_index_in_item = len(prev_item)
        # 光标还是位于末尾，直接插入
        if item_index == len(self._content):
            self._content.append(ExpressionToken(text))
            self._cursor_pos += 1
            if text == '(':
                self._content.append(ExpressionToken(")"))
            elif text == '[':
                self._content.append(ExpressionToken("]"))
            self._do_layout()
            if text == '.':
                self._show_property_suggestions()
            return
        item = self._content[item_index]
        # 光标前后都没有字符串，直接插入
        if isinstance(item, ExpressionToken):
            self._content.insert(item_index, ExpressionToken(text))
            self._cursor_pos += 1
            if text == '(':
                self._content.insert(item_index + 1, ExpressionToken(')'))
            elif text == '[':
                self._content.insert(item_index + 1, ExpressionToken(']'))
            self._do_layout()
            if text == '.':
                self._show_property_suggestions()
            return
        # 删除光标前面和text的公共前缀
        for prefix_start in range(0, cursor_index_in_item):
            if item[prefix_start:cursor_index_in_item] == text[0:cursor_index_in_item - prefix_start]:
                self._content[item_index] = item[0:prefix_start]
                left_str = item[0:prefix_start]
                deleted_len = cursor_index_in_item - prefix_start
                right_str = item[cursor_index_in_item:]
                break
        else:
            left_str = item[0:cursor_index_in_item]
            deleted_len = 0
            right_str = item[cursor_index_in_item:]

        if left_str:
            self._content[item_index] = left_str
            item_index += 1
        else:
            self._content.pop(item_index)
        self._content.insert(item_index, ExpressionToken(text))
        item_index += 1
        if text == '(':
            self._content.insert(item_index, ExpressionToken(')'))
            item_index += 1
        elif text == '[':
            self._content.insert(item_index, ExpressionToken(']'))
            item_index += 1
        if right_str:
            self._content.insert(item_index, right_str)
        self._cursor_pos = self._cursor_pos - deleted_len + 1
        self._do_layout()
        if text == '.':
            self._show_property_suggestions()

    def focusInEvent(self, event):
        if self._cursor_timer == 0:
            self._cursor_timer = self.startTimer(500)
        self._show_cursor = True
        self.update()

    def focusOutEvent(self, event):
        if self._cursor_timer != 0:
            self.killTimer(self._cursor_timer)
            self._cursor_timer = 0
        self._show_cursor = False
        self.update()

    def timerEvent(self, event):
        if event.timerId() == self._cursor_timer:
            self._show_cursor = not self._show_cursor
            self.update()
        if event.timerId() == self._layout_timer:
            self._do_layout()
            self.killTimer(self._layout_timer)
            self._layout_timer = 0

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.move_cursor_left(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            event.accept()
        elif event.key() == Qt.Key.Key_Right:
            self.move_cursor_right(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
            event.accept()
        elif event.key() == Qt.Key.Key_Backspace:
            self.delete_left()
            event.accept()
        elif event.key() == Qt.Key.Key_Delete:
            self.delete_right()
            event.accept()
        elif event.matches(QKeySequence.StandardKey.SelectAll):
            self.select_all()
            event.accept()
        elif event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection()
            event.accept()
        elif event.matches(QKeySequence.StandardKey.Cut):
            self.cut_selection()
            event.accept()
        elif event.matches(QKeySequence.StandardKey.Paste):
            self._paste_text()
            event.accept()
        elif event.key() == Qt.Key.Key_Down and not self._variable_popup.isVisible():
            self._show_variable_popup()
            event.accept()
        elif event.text() and event.text().isprintable():
            self.insert_text(event.text())
            self._show_normal_suggestions(event.text())
            event.accept()
        else:
            event.ignore()

    def inputMethodEvent(self, event):
        self.delete_selection()
        if self._preedit_start != -1:
            self._delete_content(self._preedit_start, self._preedit_end)
            # self._cursor_pos = self._preedit_start
            self._preedit_start = -1
            self._preedit_end = -1
            if event.commitString():
                self.insert_text(event.commitString())
                self._show_normal_suggestions(event.commitString())
        if event.preeditString():
            self._preedit_start = self._cursor_pos
            self.insert_text(event.preeditString())
            self._preedit_end = self._cursor_pos

    def select_all(self):
        self._select_anchor = 0
        self._select_end = self._content_length()
        self.update()

    def copy_selection(self):
        if not self.has_selection():
            return
        if self._select_anchor > self._select_end:
            start = self._select_end
            end = self._select_anchor
        else:
            start = self._select_anchor
            end = self._select_end
        selection = []
        pos = 0
        for index, item in enumerate(self._content):
            if isinstance(item, ExpressionToken):
                if start <= pos < end:
                    selection.append(item.data)
                pos += 1
            else:
                item_len = len(item)
                item_start = max(start - pos, 0)
                item_end = min(end - pos, item_len)
                if item_start < item_end:
                    selection.append(escape_string(item[item_start:item_end]))
                pos += item_len
            if pos >= end:
                break
        clipboard = QApplication.clipboard()
        clipboard.setText(" ".join(selection))

    def cut_selection(self):
        if not self.has_selection():
            return
        self.copy_selection()
        self.delete_selection()

    def _paste_text(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text:
            return
        self.delete_selection()
        self.insert_text(text)

    def move_cursor_left(self, select=False):
        if self._cursor_pos > 0:
            self._move_cursor_to(self._cursor_pos - 1, select)

    def move_cursor_right(self, select=False):
        if self._cursor_pos < self._content_length():
            self._move_cursor_to(self._cursor_pos + 1, select)

    def _move_cursor_to(self, pos, select=False):
        if select:
            if self._select_anchor == -1:
                self._select_anchor = self._cursor_pos
            self._select_end = pos
        else:
            self._select_anchor = -1
            self._select_end = -1
        self._cursor_pos = pos
        self._scroll_content()

    def delete_left(self):
        if self.has_selection():
            return self.delete_selection()
        if self._cursor_pos == 0:
            return False
        return self._delete_content(self._cursor_pos - 1, self._cursor_pos)

    def delete_right(self):
        if self.has_selection():
            return self.delete_selection()
        if self._cursor_pos == self._content_length():
            return False
        return self._delete_content(self._cursor_pos, self._cursor_pos + 1)

    def has_selection(self):
        return self._select_anchor != -1 and self._select_anchor != self._select_end

    def delete_selection(self):
        if not self.has_selection():
            return False
        if self._select_anchor > self._select_end:
            start = self._select_end
            end = self._select_anchor
        else:
            start = self._select_anchor
            end = self._select_end
            # self._cursor_pos = self._select_anchor
        return self._delete_content(start, end)

    def _delete_content(self, start, end):
        """
        删除start和end之前的内容
        """
        if start == end:
            return False
        index = 0
        pos = 0
        item_index_before_start = -1
        while index < len(self._content):
            item = self._content[index]
            if isinstance(item, str):
                item_len = len(item)
                delete_start = start - pos
                delete_end = end - pos
                if start >= pos and start < pos + item_len:
                    item_index_before_start = index - 1
                if delete_start >= item_len:
                    index += 1
                elif delete_start <= 0:
                    if delete_end >= item_len:
                        self._content.pop(index)
                    else:
                        self._content[index] = item[delete_end:]
                        index += 1
                else:
                    if delete_end >= item_len:
                        self._content[index] = item[0:delete_start]
                    else:
                        self._content[index] = item[0:delete_start] + item[delete_end:]
                    index += 1
                pos += item_len
            else:
                if start == pos:
                    item_index_before_start = index - 1
                if start <= pos < end:
                    self._content.pop(index)
                else:
                    index += 1
                pos += 1
            if pos >= end:
                break
        # 合并相邻的两个字符串
        if 0 <= item_index_before_start < len(self._content) - 1:
            item = self._content[item_index_before_start]
            next_item = self._content[item_index_before_start + 1]
            if isinstance(item, str) and isinstance(next_item, str):
                self._content[item_index_before_start] = item + next_item
                self._content.pop(item_index_before_start + 1)
        # 移动光标
        if self._cursor_pos > end:
            self._cursor_pos = self._cursor_pos - (end - start)
        elif self._cursor_pos > start:
            self._cursor_pos = start
        self._select_anchor = -1
        self._select_end = -1
        self._do_layout()
        return True

    def insert_text(self, text):
        """在光标位置插入文本，插入后光标移动到插入文本后面"""
        self.delete_selection()
        item_index, cursor_index_in_item = self._cursor_item_index(self._cursor_pos)
        if item_index >= len(self._content):
            left_item = self._content[item_index - 1] if item_index > 0 else None
            if left_item and isinstance(left_item, str):
                left_item = left_item + text
                self._content[item_index - 1] = left_item
            else:
                self._content.insert(item_index, text)
        else:
            item = self._content[item_index]
            if isinstance(item, str):
                item = item[0:cursor_index_in_item] + text + item[cursor_index_in_item:]
                self._content[item_index] = item
            elif isinstance(item, ExpressionToken):
                left_item = self._content[item_index - 1] if item_index > 0 else None
                if left_item and isinstance(left_item, str):
                    left_item = left_item + text
                    self._content[item_index - 1] = left_item
                else:
                    self._content.insert(item_index, text)
        self._cursor_pos += len(text)
        self._do_layout()
        return True

    def _cursor_item_index(self, cursor_index):
        """
        返回光标所在的元素索引及在元素中的偏移量
        """
        pos = 0
        for index, item in enumerate(self._content):
            if isinstance(item, str):
                if cursor_index >= pos and cursor_index < pos + len(item):
                    cursor_index_in_item = cursor_index - pos
                    return index, cursor_index_in_item
                pos += len(item)
            elif isinstance(item, ExpressionToken):
                if cursor_index == pos:
                    return index, 0
                pos += 1
        return len(self._content), 0

    def _content_length(self):
        return sum(len(item) if isinstance(item, str) else 1 for item in self._content)

    def sizeHint(self):
        self.ensurePolished()
        font_metrics = self.fontMetrics()
        h = (font_metrics.height() + max(2 * self.verticalMargin, font_metrics.leading())
             + self.textMargins.top() + self.textMargins.bottom()
             + self.contentsMargins().top() + self.contentsMargins().bottom())
        w = (font_metrics.horizontalAdvance('x') * 17 + font_metrics.horizontalAdvance(self._icon_text)
             + self._icon_spacing + 2 * self.horizontalMargin
             + self.textMargins.left() + self.textMargins.right()
             + self.contentsMargins().left() + self.contentsMargins().right())

        opt = QStyleOptionFrame()
        self.initStyleOption(opt)
        size = self.style().sizeFromContents(QStyle.ContentsType.CT_LineEdit, opt, QSize(w, h), self)
        return QSize(size.width(), max(size.height(), h))

    def minimumSizeHint(self):
        self.ensurePolished()
        font_metrics = self.fontMetrics()
        h = (font_metrics.height() + max(2 * self.verticalMargin, font_metrics.leading())
             + self.textMargins.top() + self.textMargins.bottom()
             + self.contentsMargins().top() + self.contentsMargins().bottom())
        w = (font_metrics.maxWidth() * 3 + font_metrics.horizontalAdvance(self._icon_text) + self._icon_spacing
             + 2 * self.horizontalMargin
             + self.textMargins.left() + self.textMargins.right()
             + self.contentsMargins().left() + self.contentsMargins().right())
        opt = QStyleOptionFrame()
        self.initStyleOption(opt)
        return self.style().sizeFromContents(QStyle.ContentsType.CT_LineEdit, opt, QSize(w, h), self)

    def resizeEvent(self, event):
        self._update_layout()

    def _update_layout(self):
        if self._layout_timer != 0:
            return
        self._layout_timer = self.startTimer(0)

    def _do_layout(self):
        self._do_layout_content()
        self._scroll_content()

    def _do_layout_content(self):
        """
        重新计算内容布局
        """
        font_metrics = self.fontMetrics()
        self._content_rect.clear()
        x = 0
        height = font_metrics.height()
        prev_item = None
        for index, item in enumerate(self._content):
            if isinstance(item, str):
                if prev_item:
                    x += self._content_spacing
                rect = QRect(x, 0, font_metrics.horizontalAdvance(item), height)
                self._content_rect.append(rect)
                x += rect.width()
            elif isinstance(item, ExpressionToken):
                if isinstance(prev_item, str):
                    x += self._content_spacing
                elif isinstance(prev_item, ExpressionToken):
                    x += self._content_spacing * 2
                rect = QRect(x, 0, font_metrics.horizontalAdvance(item.data), height)
                self._content_rect.append(rect)
                x += rect.width()
            prev_item = item
        self.update()

    def _scroll_content(self):
        """滚动内容区保证光标在可视区域"""
        self._cursor_x = self._calculate_cursor_x(self._cursor_pos)
        line_width = (self.contentsRect().width() - self.textMargins.left() - self.textMargins.right()
                      - 2 * self.horizontalMargin - self.fontMetrics().horizontalAdvance(self._icon_text)
                      - self._icon_spacing)
        if self._cursor_x < self._scroll_x:
            self._scroll_x = self._cursor_x
        elif self._cursor_x > self._scroll_x + line_width:
            self._scroll_x = self._cursor_x - line_width + self._cursor_width
        self.update()

    def _calculate_cursor_x(self, cursor_pos):
        """计算指定光标位置的x偏移量"""
        x = 0
        pos = 0
        prev_item = None
        font_metrics = self.fontMetrics()
        for index, item in enumerate(self._content):
            if isinstance(item, str):
                if prev_item:
                    x += self._content_spacing
                rect = self._content_rect[index]
                if pos <= cursor_pos < pos + len(item):
                    return x + font_metrics.horizontalAdvance(item[0:cursor_pos - pos])
                x += rect.width()
                pos += len(item)
            elif isinstance(item, ExpressionToken):
                if isinstance(prev_item, str):
                    if cursor_pos == pos:
                        return x
                    x += self._content_spacing
                elif isinstance(prev_item, ExpressionToken):
                    if cursor_pos == pos:
                        return x + self._content_spacing - int(self._cursor_width / 2)
                    x += self._content_spacing * 2
                elif cursor_pos == pos:
                    return x
                rect = self._content_rect[index]
                x += rect.width()
                pos += 1
            prev_item = item
        if isinstance(prev_item, ExpressionToken):
            return x + self._content_spacing
        else:
            return x

    def paintEvent(self, event):
        painter = QStylePainter(self)
        painter.save()
        fm = self.fontMetrics()
        fm_height = fm.height()
        pal = self.palette()
        panel = QStyleOptionFrame()
        self.initStyleOption(panel)
        painter.drawPrimitive(QStyle.PrimitiveElement.PE_PanelLineEdit, panel)
        r = self.style().subElementRect(QStyle.SubElement.SE_LineEditContents, panel, self)
        r = r.marginsRemoved(self.textMargins)
        painter.setClipRect(QRect(r.left(), r.top(), r.width() - fm.horizontalAdvance('X') * 2, r.height()))

        va = QStyle.visualAlignment(self.layoutDirection(), self.alignment) & Qt.AlignmentFlag.AlignVertical_Mask

        if va == Qt.AlignmentFlag.AlignBottom:
            vscroll = r.y() + r.height() - fm_height - self.verticalMargin
        elif va == Qt.AlignmentFlag.AlignTop:
            vscroll = r.y() + self.verticalMargin
        else:
            vscroll = r.y() + (r.height() - fm_height + 1) / 2

        line_rect = QRect(r.x() + self.horizontalMargin, vscroll, r.width() - self.horizontalMargin * 2, fm_height)
        painter.translate(-self._scroll_x + line_rect.x(), line_rect.y())
        # 绘制选中背景
        if self.has_selection():
            if self._select_anchor < self._select_end:
                selection_start_x = self._calculate_cursor_x(self._select_anchor)
                selection_end_x = self._calculate_cursor_x(self._select_end)
            else:
                selection_start_x = self._calculate_cursor_x(self._select_end)
                selection_end_x = self._calculate_cursor_x(self._select_anchor)
            painter.fillRect(QRect(selection_start_x, 0, selection_end_x - selection_start_x, fm_height),
                             pal.highlight())
        if not self._content and self._placeholder_text:
            painter.setPen(pal.placeholderText().color())
            painter.drawText(QRect(0, 0, line_rect.width(), line_rect.height()), Qt.TextFlag.TextSingleLine,
                             self._placeholder_text)
        pos = 0
        for index, item in enumerate(self._content):
            if isinstance(item, str):
                painter.setPen(pal.text().color())
                painter.drawText(self._content_rect[index], Qt.TextFlag.TextSingleLine, item)
                if self._preedit_start != -1 and self._preedit_end > self._preedit_start >= pos and pos + len(
                        item) >= self._preedit_end:
                    underline_start_x = self._content_rect[index].x() + fm.horizontalAdvance(
                        item[0:self._preedit_start - pos])
                    underline_end_x = underline_start_x + fm.horizontalAdvance(
                        item[self._preedit_start - pos:self._preedit_end - pos])
                    painter.drawLine(underline_start_x, fm_height, underline_end_x, fm_height)
                pos += len(item)
            elif isinstance(item, ExpressionToken):
                painter.fillRect(self._content_rect[index], Qt.GlobalColor.gray)
                painter.setPen(Qt.GlobalColor.blue)
                painter.drawText(self._content_rect[index], Qt.TextFlag.TextSingleLine, item.data)
                pos += 1
        self.draw_cursor(painter, QPoint(self._cursor_x, 0))
        painter.setClipRect(QRect(), Qt.ClipOperation.NoClip)
        painter.translate(self._scroll_x - line_rect.x(), -line_rect.y())
        painter.setPen(pal.accent().color())
        icon_width = fm.horizontalAdvance(self._icon_text)
        self._icon_rect = QRect(line_rect.x() + line_rect.width() - icon_width, line_rect.y(), icon_width,
                                line_rect.height())
        painter.drawText(self._icon_rect, Qt.TextFlag.TextSingleLine, self._icon_text)
        painter.restore()

    def draw_cursor(self, painter: QStylePainter, pos: QPoint):
        if not self._show_cursor:
            return
        cursor_height = self.fontMetrics().height()
        painter.setPen(self.palette().text().color())
        painter.drawLine(pos, QPoint(pos.x(), pos.y() + cursor_height - 1))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._icon_rect.contains(event.position().toPoint()):
                self._show_variable_popup()
            else:
                self._move_cursor_to(self._cursor_pos_at_point(event.position().toPoint()), False)

    def mouseMoveEvent(self, event):
        if self._icon_rect.contains(event.position().toPoint()):
            self.setCursor(Qt.CursorShape.ArrowCursor)
        else:
            self.setCursor(Qt.CursorShape.IBeamCursor)
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._move_cursor_to(self._cursor_pos_at_point(event.position().toPoint()), True)

    def _cursor_pos_at_point(self, point: QPoint):
        """获取指定坐标位置的光标位置，需要考虑滚动"""
        point_x = point.x() + self._scroll_x
        font_metrics = self.fontMetrics()
        pos = 0
        for index, item in enumerate(self._content):
            rect = self._content_rect[index]
            if rect.x() <= point_x <= rect.x() + rect.width():
                if isinstance(item, str):
                    index_in_item = min(int((point_x - rect.x()) / font_metrics.averageCharWidth()), len(item) - 1)
                    x = rect.x() + font_metrics.horizontalAdvance(item[:index_in_item])
                    min_distance = abs(x - point_x)
                    find_direction = 1 if point_x > x else -1
                    while True:
                        index_in_item += find_direction
                        if index_in_item < 0 or index_in_item >= len(item):
                            return pos + index_in_item - find_direction
                        x = rect.x() + font_metrics.horizontalAdvance(item[:index_in_item])
                        new_distance = abs(x - point_x)
                        if new_distance >= min_distance:
                            return pos + index_in_item - find_direction
                        else:
                            min_distance = new_distance
                else:
                    return pos if point_x - rect.x() < rect.width() / 2 else pos + 1
            elif rect.x() >= point_x:
                return pos
            if isinstance(item, str):
                pos += len(item)
            else:
                pos += 1
        return pos

    def _show_variable_popup(self):
        pos = self.mapToGlobal(QPoint(0, self.height() - 2))
        self._variable_popup.move(pos)
        self._variable_popup.setFixedWidth(self.width())
        self._variable_popup.show()

    def validate_expression(self):
        return validate_expression(self.get_expression())


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self._expression_edit = ExpressionEdit()
        self._expression_edit.setPlaceholderText("请输入表达式")
        self._expression_edit.set_variables([VariableDef("var_str", "text"),
                                             VariableDef("var_int", "number"),
                                             VariableDef("变量1", "text"),
                                             VariableDef("变量2", "number")], builtin_data_type_registry)
        self.layout.addWidget(self._expression_edit)
        self._line_edit = QLineEdit('a+b+1+"hello"')
        self.layout.addWidget(self._line_edit)
        self._text_edit = QTextEdit()
        self.layout.addWidget(self._text_edit)
        buttons = QHBoxLayout()
        button = QPushButton("设置表达式")
        button.clicked.connect(self._set_expression)
        buttons.addWidget(button)
        button = QPushButton("读取表达式")
        button.clicked.connect(self._get_expression)
        buttons.addWidget(button)
        button = QPushButton("验证表达式")
        button.clicked.connect(self._validate_expression)
        buttons.addWidget(button)
        self.layout.addLayout(buttons)

    @Slot()
    def _set_expression(self):
        self._expression_edit.set_expression(self._line_edit.text())

    @Slot()
    def _get_expression(self):
        self._text_edit.setText(self._expression_edit.get_expression())

    @Slot()
    def _validate_expression(self):
        if self._expression_edit.validate_expression():
            QMessageBox.information(self, "提示", "验证成功")
        else:
            QMessageBox.warning(self, "提示", "验证失败")


if __name__ == "__main__":
    app = QApplication()
    w = MyWidget()
    w.show()
    app.exec()
