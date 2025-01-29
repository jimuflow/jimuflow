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

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class MoveMouseComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        relative_to = flow_node.input('relativeTo')
        if relative_to == 'current_position':
            return gettext(
                'Move the mouse to (##{offsetX}##,##{offsetY}##) position relative to the current position').format(
                offsetX=flow_node.input('offsetX'),
                offsetY=flow_node.input('offsetY'))
        else:
            return gettext(
                'Move the mouse to (##{offsetX}##,##{offsetY}##) position relative to the upper left corner of the screen').format(
                offsetX=flow_node.input('offsetX'),
                offsetY=flow_node.input('offsetY'))

    async def execute(self) -> ControlFlow:
        relative_to = self.read_input("relativeTo")
        offset_x = int(self.read_input("offsetX"))
        offset_y = int(self.read_input("offsetY"))
        move_speed = self.read_input("moveSpeed")
        delay_after_action = float(self.read_input("delayAfterAction"))
        current_position = pyautogui.position()
        if relative_to == 'current_position':
            x = current_position[0] + offset_x
            y = current_position[1] + offset_y
        else:
            x = offset_x
            y = offset_y
        screen_size = pyautogui.size()
        x = max(0, min(x, screen_size[0] - 1))
        y = max(0, min(y, screen_size[1] - 1))
        if move_speed == 'instant':
            duration = 0.0
        else:
            distance = ((x - current_position[0]) ** 2 + (y - current_position[1]) ** 2) ** 0.5
            if move_speed == 'fast':
                speed = screen_size[0] / 1
            elif move_speed == 'medium':
                speed = screen_size[0] / 2
            else:
                speed = screen_size[0] / 3
            duration = distance / speed
        pyautogui.moveTo(x, y, duration)
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
