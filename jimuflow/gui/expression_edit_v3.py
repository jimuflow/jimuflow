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
from enum import Enum

from PySide6.QtCore import Slot, QEvent, QPoint, QTimer, QMimeData
from PySide6.QtGui import QTextCharFormat, Qt, QTextFormat, QTextCursor, QStandardItemModel, QStandardItem, QKeySequence
from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QPushButton, QCompleter, QMessageBox, QHBoxLayout, \
    QLabel, QApplication, QTreeView

from jimuflow.common.mimetypes import mimetype_expression
from jimuflow.datatypes import builtin_data_type_registry, DataTypeRegistry
from jimuflow.definition import VariableDef
from jimuflow.gui.expression_edit_popup import ExpressionEditPopup
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.expression import escape_string, get_property_suggestions, \
    validate_expression, tokenize_expression


class AdjustPositionStrategy(Enum):
    prefer_next_position = 0
    prefer_previous_position = 1
    force_previous_position = 2
    force_next_position = 3


operators = [
    ('(', gettext('Bracket operator')),
    (')', gettext('Bracket operator')),
    ('+', gettext('Addition operator')),
    ('-', gettext('Subtraction or negative operator')),
    ('*', gettext('Multiplication operator')),
    ('/', gettext('Division operator')),
    ('%', gettext('Remainder operator')),
    ('**', gettext('Power operator')),
    ('//', gettext('Floor division operator')),
    ('&&', gettext('Logical and operator')),
    ('||', gettext('Logical or operator')),
    ('!', gettext('Logical non operator')),
    ('>', gettext('Greater than operator')),
    ('>=', gettext('Greater than or equal to operator')),
    ('<', gettext('Less than operator')),
    ('<=', gettext('Less than or equal to operator')),
    ('==', gettext('Equal operator')),
    ('!=', gettext('Not equal to operator')),
    ('[', gettext('Index access operator')),
    (']', gettext('Index access operator')),
    ('.', gettext('Attribute access operator')),
]


def create_completion_model_row(token, description):
    name_item = QStandardItem(token)
    desc_item = QStandardItem(description)
    desc_item.setData(Qt.AlignmentFlag.AlignRight, Qt.ItemDataRole.TextAlignmentRole)
    return [name_item, desc_item]


class ExpressionEditV3(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._button = QLabel("{x}", self)
        self._button.setStyleSheet("color:blue;")
        self._button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._button.installEventFilter(self)
        self._button_top_margin = 4
        self._button_size = self._button.sizeHint()
        self._right_margin = self._button_size.width()
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        self._next_token_id = 1
        self._text_fmt = self.currentCharFormat()
        self._variables: list[VariableDef] = []
        self._type_registry = builtin_data_type_registry
        self._completer_model = self._create_completer_model()
        self._completer_popup = QTreeView()
        self.completer = QCompleter(self._completer_model, self)
        self.completer.setPopup(self._completer_popup)
        self._completer_popup.setHeaderHidden(True)
        self._completer_popup.setRootIsDecorated(False)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        self.completer.activated.connect(self._on_completer_activated)
        self.completer.setWidget(self)
        self._variable_popup = ExpressionEditPopup(self)
        self._variable_popup.item_selected.connect(self._on_tokens_activated)
        self._line_height = self.fontMetrics().height()
        self._top_margin = 5
        self._button_margin = 5
        self._max_rows = 5
        self._min_height = self._line_height + self._top_margin + self._button_margin + 1
        self._max_height = (self._line_height+1) * self._max_rows + self._top_margin + self._button_margin
        self.setFixedHeight(self._min_height)
        self.textChanged.connect(self.adjust_height)

    def adjust_height(self):
        ideal_height = int(self.document().size().height()) + 2
        if self.height() < ideal_height:
            height = min(self._max_height, ideal_height)
        else:
            height = max(self._min_height, ideal_height)
        if height != self.height():
            self.setFixedHeight(height)

    def createMimeDataFromSelection(self):
        data = super().createMimeDataFromSelection()
        data.setText(self.selected_expression())
        return data

    def canInsertFromMimeData(self, source):
        return source.hasFormat("text/plain")

    def insertFromMimeData(self, source):
        if source.hasFormat("text/plain"):
            self.insert_expression(source.text())
            return True
        return False

    def eventFilter(self, watched, event):
        if watched is self._button:
            if event.type() == QEvent.Type.MouseButtonPress:
                self._show_variable_popup()
                return True
        return super().eventFilter(watched, event)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        x = self.rect().right() - self._button_size.width()
        if self.verticalScrollBar().isVisible():
            x -= self.verticalScrollBar().width()
        self._button.setGeometry(x, self.rect().top() + self._button_top_margin,
                                 self._button_size.width(), self._button_size.height())
        self._resize_completer_popup()

    def _resize_completer_popup(self):
        width = self.rect().width() - 20
        if width > 0:
            self._completer_popup.setColumnWidth(0, width * 0.7)
            self._completer_popup.setColumnWidth(1, width * 0.3)
        else:
            self._completer_popup.setColumnWidth(0, 70)
            self._completer_popup.setColumnWidth(1, 30)

    def copy_selection(self):
        selected_expression = self.selected_expression()
        if selected_expression:
            clipboard = QApplication.clipboard()
            mime_data = QMimeData()
            mime_data.setData(mimetype_expression, selected_expression.encode("utf-8"))
            mime_data.setText(selected_expression)
            clipboard.setMimeData(mime_data)

    def selected_expression(self):
        if self.textCursor().hasSelection():
            return self._get_expression(self.textCursor().selectionStart(), self.textCursor().selectionEnd())

    def cut_selection(self):
        if not self.textCursor().hasSelection():
            return
        self.copy_selection()
        self.textCursor().removeSelectedText()

    def paste(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasFormat(mimetype_expression):
            self.textCursor().removeSelectedText()
            self.insert_expression(mime_data.data(mimetype_expression).data().decode('utf-8'))
        elif mime_data.hasText():
            self.textCursor().removeSelectedText()
            self.insert_text(mime_data.text())

    def get_expression(self):
        return self._get_expression(0, sys.maxsize)

    def _get_previous_char_token_id(self, cursor: QTextCursor):
        if not cursor.atBlockStart():
            return cursor.charFormat().property(QTextFormat.Property.UserProperty)

    def _get_expression(self, start, end):
        expression = []
        cursor = QTextCursor(self.document())
        cursor.setPosition(start)
        prev_token_id = None
        while cursor.movePosition(QTextCursor.MoveOperation.NextCharacter,
                                  QTextCursor.MoveMode.KeepAnchor) and cursor.position() <= end:
            if self._get_previous_char_token_id(cursor) != prev_token_id:
                cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter, QTextCursor.MoveMode.KeepAnchor)
                selected_text = cursor.selectedText()
                if selected_text:
                    if prev_token_id is None:
                        expression.append(escape_string(selected_text.replace('\u2029', '\n')))
                    else:
                        expression.append(selected_text.strip())
                cursor.clearSelection()
                cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, QTextCursor.MoveMode.KeepAnchor)
                prev_token_id = self._get_previous_char_token_id(cursor)
        selected_text = cursor.selectedText()
        if selected_text:
            if prev_token_id is None:
                expression.append(escape_string(selected_text.replace('\u2029', '\n')))
            else:
                expression.append(selected_text.strip())
        return " ".join(expression)

    def set_expression(self, expression: str):
        self.clear()
        self.insert_expression(expression)

        def adjust_height_and_scroll_top():
            self.adjust_height()
            self.verticalScrollBar().setValue(0)

        QTimer.singleShot(0, adjust_height_and_scroll_top)

    def insert_expression(self, expression):
        if expression:
            try:
                tokens = tokenize_expression(expression)
            except:
                tokens = [expression]
        else:
            tokens = []
        for token in tokens:
            if isinstance(token, str):
                self.insert_text(token)
            else:
                self.insert_token(token.data)

    def setText(self, text: str):
        self.set_expression(text)

    def text(self) -> str:
        return self.get_expression()

    def _create_completer_model(self):
        model = QStandardItemModel(0, 2, self)
        for token, description in operators:
            model.appendRow(create_completion_model_row(token, description))
        for var_def in self._variables:
            var_type_def = self._type_registry.get_data_type(var_def.type)
            model.appendRow(create_completion_model_row(var_def.name, gettext('{type} Variable').format(
                type=var_type_def.display_name)))
        return model

    def _on_completer_activated(self, token: str):
        w = max(self.rect().width() - 70, self.rect().width() * 0.7)
        tab_idx = token.find('\t')
        if tab_idx > 0:
            token = token[:tab_idx]
        # 删除当前选中的文本
        self.textCursor().removeSelectedText()
        if self._get_previous_char_token_id(self.textCursor()) is None:
            # 光标位于字符串中，删除光标前面的字符串和token的公共前缀
            cursor = QTextCursor(self.textCursor())
            prefix_matched = False
            while cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter, QTextCursor.MoveMode.KeepAnchor):
                prefix = cursor.selectedText()
                prefix_matched = token.lower().startswith(prefix.lower())
                if self._get_previous_char_token_id(cursor) is not None or prefix_matched:
                    break
            if prefix_matched:
                cursor.removeSelectedText()
        # 插入token
        self.insert_token(token)
        if token == '(':
            self.insert_token(')')
            self.move_cursor_left()
        elif token == '[':
            self.insert_token(']')
            self.move_cursor_left()
        if token == '.':
            self._show_property_suggestions()

    def _on_tokens_activated(self, tokens: list[str]):
        # 删除当前选中的文本
        self.textCursor().removeSelectedText()
        # 插入token
        for token in tokens:
            self.insert_token(token)

    def _show_normal_suggestions(self, text):
        self.completer.setModel(self._completer_model)
        self.completer.setCompletionPrefix(text)
        self.completer.complete()

    def _show_property_suggestions(self):
        property_suggestions = get_property_suggestions(self._get_expression(0, self.textCursor().position()),
                                                        self._variables, self._type_registry)
        if not property_suggestions:
            return
        model = QStandardItemModel(0, 2, self)
        for prop in property_suggestions:
            model.appendRow(create_completion_model_row(prop.name, prop.description))
        self.completer.setModel(model)
        self.completer.setCompletionPrefix("")
        self.completer.complete()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.move_cursor_left(
                QTextCursor.MoveMode.KeepAnchor if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else QTextCursor.MoveMode.MoveAnchor)
            event.accept()
        elif event.key() == Qt.Key.Key_Right:
            self.move_cursor_right(
                QTextCursor.MoveMode.KeepAnchor if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else QTextCursor.MoveMode.MoveAnchor)
            event.accept()
        elif event.key() == Qt.Key.Key_Return:
            if self.completer.popup().isVisible():
                event.ignore()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key.Key_Backspace:
            self._delete_left()
            event.accept()
        elif event.key() == Qt.Key.Key_Delete:
            self._delete_right()
            event.accept()
        elif event.key() == Qt.Key.Key_Tab:
            event.ignore()
        elif event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection()
            event.accept()
        elif event.matches(QKeySequence.StandardKey.Cut):
            self.cut_selection()
            event.accept()
        elif event.matches(QKeySequence.StandardKey.Paste):
            self.paste()
            event.accept()
        elif event.text() and event.text().isprintable():
            super().keyPressEvent(event)
            self._show_normal_suggestions(event.text())
        else:
            super().keyPressEvent(event)

    def inputMethodEvent(self, event):
        super().inputMethodEvent(event)
        if event.commitString():
            self._show_normal_suggestions(event.commitString())

    def _delete_left(self):
        if self.textCursor().hasSelection():
            self.textCursor().removeSelectedText()
        else:
            self.move_cursor_left(QTextCursor.MoveMode.KeepAnchor)
            self.textCursor().removeSelectedText()
        if self.textCursor().charFormat() != self._text_fmt:
            self.setCurrentCharFormat(self._text_fmt)

    def _delete_right(self):
        if self.textCursor().hasSelection():
            self.textCursor().removeSelectedText()
        else:
            self.move_cursor_right(QTextCursor.MoveMode.KeepAnchor)
            self.textCursor().removeSelectedText()
        if self.textCursor().charFormat() != self._text_fmt:
            self.setCurrentCharFormat(self._text_fmt)

    def insert_text(self, text):
        self.textCursor().insertText(text, self._text_fmt)

    def insert_token(self, token):
        fmt = QTextCharFormat(self._text_fmt)
        fmt.setBackground(Qt.GlobalColor.gray)
        fmt.setForeground(Qt.GlobalColor.blue)
        token_id = f"token_{self._next_token_id}"
        fmt.setProperty(QTextFormat.Property.UserProperty, token_id)
        space_fmt = QTextCharFormat(self._text_fmt)
        space_fmt.setProperty(QTextFormat.Property.UserProperty, token_id)
        self._next_token_id += 1
        self.textCursor().insertText(' ', space_fmt)
        self.textCursor().insertText(token, fmt)
        self.textCursor().insertText(' ', space_fmt)
        self.setCurrentCharFormat(self._text_fmt)

    def _on_cursor_position_changed(self):
        cursor = QTextCursor(self.textCursor())
        cursor_updated = False
        if cursor.hasSelection():
            adjusted_anchor = self._adjust_cursor_position(cursor.anchor(),
                                                           AdjustPositionStrategy.prefer_previous_position if cursor.position() > cursor.anchor() else AdjustPositionStrategy.prefer_next_position)
            adjusted_position = self._adjust_cursor_position(cursor.position(),
                                                             AdjustPositionStrategy.prefer_previous_position if cursor.position() < cursor.anchor() else AdjustPositionStrategy.prefer_next_position)
            if adjusted_anchor != cursor.anchor() or adjusted_position != cursor.position():
                cursor.setPosition(adjusted_anchor)
                cursor.setPosition(adjusted_position, QTextCursor.MoveMode.KeepAnchor)
                cursor_updated = True
                self.setTextCursor(cursor)
        else:
            adjusted_position = self._adjust_cursor_position(cursor.position())
            if cursor.position() != adjusted_position:
                cursor.setPosition(adjusted_position)
                cursor_updated = True
            if cursor.charFormat() != self._text_fmt:
                cursor.setCharFormat(self._text_fmt)
                cursor_updated = True
            block_fmt = cursor.blockFormat()
            if block_fmt.rightMargin() != self._right_margin:
                block_fmt.setRightMargin(self._right_margin)
                cursor.setBlockFormat(block_fmt)
                cursor_updated = True
        if cursor_updated:
            self.setTextCursor(cursor)

    def move_cursor_left(self, mode=QTextCursor.MoveMode.MoveAnchor):
        cursor = QTextCursor(self.textCursor())
        if cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter, mode):
            adjusted_position = self._adjust_cursor_position(cursor.position(),
                                                             AdjustPositionStrategy.force_previous_position)
            if adjusted_position != cursor.position():
                cursor.setPosition(adjusted_position, mode)
            self.setTextCursor(cursor)

    def move_cursor_right(self, mode=QTextCursor.MoveMode.MoveAnchor):
        cursor = QTextCursor(self.textCursor())
        if cursor.movePosition(QTextCursor.MoveOperation.NextCharacter, mode):
            adjusted_position = self._adjust_cursor_position(cursor.position(),
                                                             AdjustPositionStrategy.force_next_position)
            if adjusted_position != cursor.position():
                cursor.setPosition(adjusted_position, mode)
            self.setTextCursor(cursor)

    def _adjust_cursor_position(self, position, adjust_strategy=AdjustPositionStrategy.prefer_next_position):
        """
        获取离position最近的合法位置：token前、token后、字符串中
        """
        cursor = QTextCursor(self.textCursor())
        cursor.setPosition(position)
        token_id = self._get_previous_char_token_id(cursor)
        if token_id is None:
            # 不在token中
            return position
        # 向前查找相同格式的字符
        start_pos = position
        while cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter):
            start_pos = cursor.position()
            if self._get_previous_char_token_id(cursor) != token_id:
                break
        if start_pos == position:
            # 在token前
            return position
        # 向后查找相同格式的字符
        cursor.setPosition(position)
        end_pos = position
        while cursor.movePosition(QTextCursor.MoveOperation.NextCharacter):
            if self._get_previous_char_token_id(cursor) != token_id:
                break
            else:
                end_pos = cursor.position()
        if end_pos == position:
            # 在token后
            return position
        if adjust_strategy == AdjustPositionStrategy.force_previous_position:
            return start_pos
        elif adjust_strategy == AdjustPositionStrategy.force_next_position:
            return end_pos
        elif end_pos - position < position - start_pos:
            return end_pos
        elif end_pos - position > position - start_pos:
            return start_pos
        elif adjust_strategy == AdjustPositionStrategy.prefer_previous_position:
            return start_pos
        else:
            return end_pos

    def validate_expression(self):
        return validate_expression(self.get_expression())

    def set_variables(self, variables: list[VariableDef], type_registry: DataTypeRegistry):
        self._variables = variables
        self._type_registry = type_registry
        self._completer_model = self._create_completer_model()
        self.completer.setModel(self._completer_model)
        self._variable_popup.set_variables(variables, type_registry)
        self._resize_completer_popup()

    def _show_variable_popup(self):
        pos = self.mapToGlobal(QPoint(0, self.height() - 2))
        self._variable_popup.move(pos)
        self._variable_popup.setFixedWidth(self.width())
        self._variable_popup.show()


class ExpressionEditTestPopup(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self._expression_edit = ExpressionEditV3()
        self._expression_edit.setPlaceholderText("请输入表达式")
        self._expression_edit.set_variables([VariableDef("var_str", "text"),
                                             VariableDef("var_int", "number"),
                                             VariableDef("变量1", "text"),
                                             VariableDef("变量2", "number")], builtin_data_type_registry)
        self.layout.addWidget(self._expression_edit)
        self._line_edit = QTextEdit('a+b+1+"h\\ne\\n\\nl\\n\\nl\\n\\no"')
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
        self._expression_edit.set_expression(self._line_edit.toPlainText())

    @Slot()
    def _get_expression(self):
        self._text_edit.setText(self._expression_edit.get_expression())

    @Slot()
    def _validate_expression(self):
        if self._expression_edit.validate_expression():
            QMessageBox.information(self, "提示", "验证成功")
        else:
            QMessageBox.warning(self, "提示", "验证失败")


if __name__ == '__main__':
    app = QApplication()
    window = ExpressionEditTestPopup()
    window.show()
    app.exec()
