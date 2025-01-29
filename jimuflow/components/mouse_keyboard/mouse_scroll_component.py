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

modifier_keys = {
    "none": "None",
    "Alt": "Alt",
    "Control": "Ctrl",
    "ControlOrMeta": "Ctrl or Meta",
    "Meta": "Meta",
    "Shift": "Shift"
}

class MouseScrollComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        scroll_direction = flow_node.input("scrollDirection")
        number_of_scrolls = flow_node.input("numberOfScrolls")
        modifier_key = flow_node.input("modifierKey")
        if modifier_key == 'none':
            if scroll_direction == 'up':
                return gettext('Scroll up ##{number_of_scrolls}## times').format(number_of_scrolls=number_of_scrolls)
            else:
                return gettext('Scroll down ##{number_of_scrolls}## times').format(number_of_scrolls=number_of_scrolls)
        else:
            if scroll_direction == 'up':
                return gettext('{modifierKey} + Scroll up ##{number_of_scrolls}## times').format(
                    number_of_scrolls=number_of_scrolls,
                    modifierKey=gettext(modifier_keys[modifier_key]))
            else:
                return gettext('{modifierKey} + Scroll down ##{number_of_scrolls}## times').format(
                    number_of_scrolls=number_of_scrolls,
                    modifierKey=gettext(modifier_keys[modifier_key]))

    async def execute(self) -> ControlFlow:
        scroll_direction = self.read_input("scrollDirection")
        number_of_scrolls = int(self.read_input("numberOfScrolls"))
        if scroll_direction == 'down':
            number_of_scrolls = -number_of_scrolls
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
        if modifier_key:
            with pyautogui.hold(modifier_key_name):
                pyautogui.scroll(number_of_scrolls)
        else:
            pyautogui.scroll(number_of_scrolls)
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
