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

from PySide6.QtCore import QObject, Signal


class Action:
    def __init__(self, description):
        self.description = description

    def execute(self):
        """
        执行操作
        """
        pass

    def undo(self):
        """
        撤销操作
        """
        pass


class UndoRedoManager(QObject):
    stack_updated = Signal(str, str)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._undo_stack: list[Action] = []  # 存储可撤销的操作
        self._redo_stack: list[Action] = []  # 存储可重做的操作

    def perform_action(self, action: Action):
        """
        执行一个新操作，并记录用于撤销的逆操作。
        """
        self._undo_stack.append(action)
        self._redo_stack.clear()  # 执行新操作时清空重做栈
        action.execute()  # 执行操作
        self.notify_stack_updated()

    def notify_stack_updated(self):
        current_undo_description = self._undo_stack[-1].description if self._undo_stack else ""
        current_redo_description = self._redo_stack[-1].description if self._redo_stack else ""
        self.stack_updated.emit(current_undo_description, current_redo_description)

    def undo(self):
        """
        撤销最近的操作。
        """
        if self._undo_stack:
            action = self._undo_stack.pop()
            action.undo()  # 执行逆操作
            self._redo_stack.append(action)
            self.notify_stack_updated()

    def redo(self):
        """
        重做最近撤销的操作。
        """
        if self._redo_stack:
            action = self._redo_stack.pop()
            action.execute()  # 再次执行操作
            self._undo_stack.append(action)
            self.notify_stack_updated()
