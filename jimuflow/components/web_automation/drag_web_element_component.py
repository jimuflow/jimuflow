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

import time

from playwright.async_api import Page

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.components.web_automation.playwright_utils import get_element_by_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class DragWebElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        drag_type = flow_node.input('dragType')
        if drag_type == 'to_element':
            return gettext(
                'Drag ##{sourceElement}## to ##{targetElement}## on web page ##{webPage}##').format(
                sourceElement=describe_element_uri(flow_node.process_def.package, flow_node.input('sourceElementUri')),
                targetElement=describe_element_uri(flow_node.process_def.package, flow_node.input('targetElementUri')),
                webPage=flow_node.input('webPage'))
        else:
            return gettext(
                'Drag ##{sourceElement}## by offset ##{dragOffsetX}## ##{dragOffsetY}## on web page ##{webPage}##').format(
                sourceElement=describe_element_uri(flow_node.process_def.package, flow_node.input('sourceElementUri')),
                dragOffsetX=flow_node.input('dragOffsetX'),
                dragOffsetY=flow_node.input('dragOffsetY'),
                webPage=flow_node.input('webPage'))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input("webPage")
        source_element_uri = self.read_input("sourceElementUri")
        source_offset = self.read_input('sourceOffset')
        wait_time = float(self.read_input("waitTime"))
        source_element = await get_element_by_uri(self, page, source_element_uri, wait_time)
        await source_element.scroll_into_view_if_needed(timeout=wait_time * 1000)
        source_bounding_box = await source_element.bounding_box(timeout=wait_time * 1000)
        if source_offset:
            source_x_offset = int(self.read_input('sourceX'))
            source_y_offset = int(self.read_input('sourceY'))
            source_x = source_bounding_box['x'] + source_x_offset
            source_y = source_bounding_box['y'] + source_y_offset
        else:
            source_x = source_bounding_box['x'] + source_bounding_box['width'] / 2
            source_y = source_bounding_box['y'] + source_bounding_box['height'] / 2

        drag_type = self.read_input('dragType')
        if drag_type == 'to_element':
            target_element_uri = self.read_input("targetElementUri")
            target_offset = self.read_input('targetOffset')
            target_element = await get_element_by_uri(self, page, target_element_uri, wait_time)
            target_bounding_box = await target_element.bounding_box(timeout=wait_time * 1000)
            if target_offset:
                target_x_offset = int(self.read_input('targetX'))
                target_y_offset = int(self.read_input('targetY'))
                target_x = target_bounding_box['x'] + target_x_offset
                target_y = target_bounding_box['y'] + target_y_offset
            else:
                target_x = target_bounding_box['x'] + target_bounding_box['width'] / 2
                target_y = target_bounding_box['y'] + target_bounding_box['height'] / 2
        else:
            drag_offset_x = int(self.read_input('dragOffsetX'))
            drag_offset_y = int(self.read_input('dragOffsetY'))
            target_x = source_x + drag_offset_x
            target_y = source_y + drag_offset_y

        # 计算source坐标和target坐标之间的距离
        distance = ((target_x - source_x) ** 2 + (target_y - source_y) ** 2) ** 0.5

        drag_speed = self.read_input('dragSpeed')
        if drag_speed == 'instant':
            steps = 1
        else:
            step_interval = 17
            steps_per_second = 1000 / step_interval
            if drag_speed == 'fast':
                distance_per_second = 500
            elif drag_speed == 'medium':
                distance_per_second = 300
            else:
                distance_per_second = 100
            steps = int(distance / distance_per_second * steps_per_second)
        print(
            f'source_x={source_x}, source_y={source_y}, target_x={target_x}, target_y={target_y}, distance={distance}, steps={steps}')
        await page.mouse.move(source_x, source_y)
        await page.mouse.down(button='left')
        start = time.time()
        await page.mouse.move(target_x, target_y, steps=steps)
        print(f"step_interval={(time.time() - start) / steps}, steps={steps}")
        await page.mouse.up(button='left')

        return ControlFlow.NEXT
