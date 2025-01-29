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

import asyncio

import pyautogui

from jimuflow.common.keyboard import common_hotkeys, desc_hotkey, transform_key
from jimuflow.components.core.os_utils import is_macos, is_windows
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class KeyboardInputComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        input_type = flow_node.input('inputType')
        if input_type == 'text':
            return gettext(
                'Type text ##{textContent}## in the current window').format(
                textContent=flow_node.input('textContent'))
        else:
            hotkey_type = flow_node.input('hotkeyType')
            if hotkey_type == 'common':
                common_hotkey = flow_node.input('commonHotkey')
                hotkey = common_hotkeys.get(common_hotkey, common_hotkey)
            else:
                hotkey = desc_hotkey(flow_node.input('customHotkey'))
            return gettext('Press the hotkey ##{hotkey}##').format(
                hotkey=hotkey)

    async def execute(self) -> ControlFlow:
        input_type = self.read_input("inputType")
        if input_type == 'text':
            text_content = self.read_input("textContent")
            input_interval = float(self.read_input("inputInterval")) / 1000
            if is_windows():
                from jimuflow.components.windows_automation.pywinauto_utill import send_text
                send_text(text_content, input_interval)
            else:
                pyautogui.write(text_content, interval=input_interval)
        else:
            hotkey_type = self.read_input('hotkeyType')
            if hotkey_type == 'common':
                common_hotkey = self.read_input('commonHotkey')
                if common_hotkey == 'ctrlcmd_c':
                    pyautogui.hotkey('command' if is_macos() else 'ctrl', 'c')
                elif common_hotkey == 'ctrlcmd_v':
                    pyautogui.hotkey('command' if is_macos() else 'ctrl', 'v')
                elif common_hotkey == 'ctrlcmd_x':
                    pyautogui.hotkey('command' if is_macos() else 'ctrl', 'x')
                elif common_hotkey == 'ctrlcmd_z':
                    pyautogui.hotkey('command' if is_macos() else 'ctrl', 'z')
                elif common_hotkey == 'ctrlcmd_s':
                    pyautogui.hotkey('command' if is_macos() else 'ctrl', 's')
                elif common_hotkey == 'ctrlcmd_a':
                    pyautogui.hotkey('command' if is_macos() else 'ctrl', 'a')
                elif common_hotkey == 'enter':
                    pyautogui.press('enter')
            else:
                custom_hotkey = self.read_input('customHotkey')
                custom_hotkey = [transform_key(k) for k in custom_hotkey]
                if len(custom_hotkey) > 1:
                    pyautogui.hotkey(*custom_hotkey)
                else:
                    pyautogui.press(custom_hotkey[0])
        delay_after_action = float(self.read_input("delayAfterAction"))
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
