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


class HoverImageComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Find the image ##{image}## on the screen and move the mouse to the image').format(
            image=flow_node.input('image'))

    async def execute(self) -> ControlFlow:
        image = self.read_input("image")
        similarity = float(self.read_input('similarity'))
        match_mode = self.read_input('matchMode')
        image_path = self.get_resource_path(image)
        screen_size = pyautogui.size()
        screen_image = pyautogui.screenshot()
        try:
            scale = screen_size[0] / screen_image.width
            location = pyautogui.locate(str(image_path), screen_image, grayscale=match_mode == 'grayscale',
                                        confidence=similarity / 100)
        finally:
            screen_image.close()
        self.log_debug(gettext("Found image at {location}"),
                       location={'x': int(location.left), 'y': int(location.top), 'width': location.width,
                                 'height': location.height})
        cursor_position = self.read_input('cursorPosition')
        if cursor_position == 'center':
            origin_x, origin_y = pyautogui.center(location)
        else:
            origin_x, origin_y, _, _ = location
        offset_x = int(self.read_input("offsetX"))
        offset_y = int(self.read_input("offsetY"))
        x = origin_x * scale + offset_x
        y = origin_y * scale + offset_y
        move_speed = self.read_input("moveSpeed")
        current_position = pyautogui.position()
        x = max(0, min(x, screen_size[0] - 1))
        y = max(0, min(y, screen_size[1] - 1))
        if move_speed == 'fast':
            duration = ((x - current_position[0]) ** 2 + (y - current_position[1]) ** 2) ** 0.5 / 1500
        elif move_speed == 'medium':
            duration = ((x - current_position[0]) ** 2 + (y - current_position[1]) ** 2) ** 0.5 / 1000
        elif move_speed == 'slow':
            duration = ((x - current_position[0]) ** 2 + (y - current_position[1]) ** 2) ** 0.5 / 500
        else:
            duration = 0.0
        pyautogui.moveTo(x, y, duration)
        delay_after_action = float(self.read_input("delayAfterAction"))
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
