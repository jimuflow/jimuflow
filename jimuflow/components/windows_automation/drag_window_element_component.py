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

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class DragWindowElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        drag_type = flow_node.input('dragType')
        if drag_type == 'to_element':
            return gettext(
                'Drag ##{sourceElement}## to ##{targetElement}##').format(
                sourceElement=describe_element_uri(flow_node.process_def.package, flow_node.input('sourceElementUri')),
                targetElement=describe_element_uri(flow_node.process_def.package, flow_node.input('targetElementUri')))
        else:
            return gettext(
                'Drag ##{sourceElement}## by offset ##{dragOffsetX}## ##{dragOffsetY}##').format(
                sourceElement=describe_element_uri(flow_node.process_def.package, flow_node.input('sourceElementUri')),
                dragOffsetX=flow_node.input('dragOffsetX'),
                dragOffsetY=flow_node.input('dragOffsetY'))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri
        from pywinauto.timings import Timings
        from jimuflow.common.win32_functions import GetSystemMetrics

        source_element_uri = self.read_input("sourceElementUri")
        wait_time = float(self.read_input("waitTime"))
        source_element = get_element_by_uri(self, source_element_uri, wait_time)
        source_element.set_focus()

        source_offset = self.read_input('sourceOffset')
        source_rect = source_element.rectangle()
        if source_offset:
            source_x_offset = int(self.read_input('sourceX'))
            source_y_offset = int(self.read_input('sourceY'))
            if source_x_offset != 0:
                source_x = source_rect.left + source_x_offset
            else:
                source_x = int(source_rect.left + source_rect.width() / 2)
            if source_y_offset != 0:
                source_y = source_rect.top + source_y_offset
            else:
                source_y = int(source_rect.top + source_rect.height() / 2)
        else:
            source_x = int(source_rect.left + source_rect.width() / 2)
            source_y = int(source_rect.top + source_rect.height() / 2)

        drag_type = self.read_input('dragType')
        if drag_type == 'to_element':
            target_element_uri = self.read_input("targetElementUri")
            target_offset = self.read_input('targetOffset')
            target_element = get_element_by_uri(self, target_element_uri, wait_time)
            target_rect = target_element.rectangle()
            if target_offset:
                target_x_offset = int(self.read_input('targetX'))
                target_y_offset = int(self.read_input('targetY'))
                if target_x_offset != 0:
                    target_x = target_rect.left + target_x_offset
                else:
                    target_x = int(target_rect.left + target_rect.width() / 2)
                if target_y_offset != 0:
                    target_y = target_rect.top + target_y_offset
                else:
                    target_y = int(target_rect.top + target_rect.height() / 2)
            else:
                target_x = int(target_rect.left + target_rect.width() / 2)
                target_y = int(target_rect.top + target_rect.height() / 2)
        else:
            drag_offset_x = int(self.read_input('dragOffsetX'))
            drag_offset_y = int(self.read_input('dragOffsetY'))
            target_x = source_x + drag_offset_x
            target_y = source_y + drag_offset_y

        drag_speed = self.read_input('dragSpeed')
        if drag_speed == 'instant':
            duration = 0.0
        else:
            screen_resolution_width = GetSystemMetrics(0)
            distance = ((target_x - source_x) ** 2 + (target_y - source_y) ** 2) ** 0.5
            if drag_speed == 'fast':
                speed = screen_resolution_width / 1
            elif drag_speed == 'medium':
                speed = screen_resolution_width / 2
            else:
                speed = screen_resolution_width / 3
            duration = distance / speed
        pyautogui.mouseDown(source_x, source_y)
        await asyncio.sleep(Timings.before_drag_wait)
        pyautogui.moveTo(target_x, target_y, duration)
        await asyncio.sleep(Timings.before_drop_wait)
        pyautogui.mouseUp()
        await asyncio.sleep(Timings.after_drag_n_drop_wait)
        delay_after_action = float(self.read_input("delayAfterAction"))
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
