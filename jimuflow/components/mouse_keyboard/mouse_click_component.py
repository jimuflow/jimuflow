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

from jimuflow.components.core.os_utils import is_macos
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow

mouse_buttons = {
    "left": "Left button",
    "right": "Right button",
    "middle": "Middle button"
}
click_types = {
    "single_click": "Single click",
    "double_click": "Double click",
    "mouse_down": "Mouse down",
    "mouse_up": "Mouse up"
}
modifier_keys = {
    "none": "None",
    "Alt": "Alt",
    "Control": "Ctrl",
    "ControlOrMeta": "Ctrl or Meta",
    "Meta": "Meta",
    "Shift": "Shift"
}


class MouseClickComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        mouse_button = flow_node.input("mouseButton")
        click_type = flow_node.input("clickType")
        modifier_key = flow_node.input("modifierKey")
        if modifier_key == 'none':
            return gettext('{clickType} {mouseButton}').format(clickType=gettext(click_types[click_type]),
                                                               mouseButton=gettext(mouse_buttons[mouse_button]))
        else:
            return gettext('{modifierKey} + {clickType} {mouseButton}').format(
                clickType=gettext(click_types[click_type]), mouseButton=gettext(mouse_buttons[mouse_button]),
                modifierKey=gettext(modifier_keys[modifier_key]))

    async def execute(self) -> ControlFlow:
        mouse_button = self.read_input("mouseButton")
        click_type = self.read_input("clickType")
        modifier_key = self.read_input("modifierKey")
        delay_after_action = float(self.read_input("delayAfterAction"))
        if modifier_key == 'Alt':
            modifier_key_name = 'alt'
        elif modifier_key == 'Control':
            modifier_key_name = 'ctrl'
        elif modifier_key == 'Shift':
            modifier_key_name = 'shift'
        elif modifier_key == 'Meta':
            modifier_key_name = 'command'
        elif modifier_key == 'ControlOrMeta':
            if is_macos():
                modifier_key_name = 'command'
            else:
                modifier_key_name = 'ctrl'
        else:
            modifier_key_name = ''
        if click_type == 'single_click':
            if modifier_key:
                with pyautogui.hold(modifier_key_name):
                    pyautogui.click(button=mouse_button)
            else:
                pyautogui.click(button=mouse_button)
        elif click_type == 'double_click':
            if modifier_key:
                with pyautogui.hold(modifier_key_name):
                    pyautogui.doubleClick(button=mouse_button)
            else:
                pyautogui.doubleClick(button=mouse_button)
        elif click_type == 'mouse_down':
            if modifier_key:
                with pyautogui.hold(modifier_key_name):
                    pyautogui.mouseDown(button=mouse_button)
            else:
                pyautogui.mouseDown(button=mouse_button)
        elif click_type == 'mouse_up':
            if modifier_key:
                with pyautogui.hold(modifier_key_name):
                    pyautogui.mouseUp(button=mouse_button)
            else:
                pyautogui.mouseUp(button=mouse_button)
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
