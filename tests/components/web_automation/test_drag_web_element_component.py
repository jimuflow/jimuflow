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

import pytest

from jimuflow.components.web_automation import DragWebElementComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_drag_to_element(http_server, headless):
    async with create_component_context(DragWebElementComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page6.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "sourceElementUri": add_test_web_element(component, '//*[@id="draggable"]'),
            "dragType": 'to_element',
            "targetElementUri": add_test_web_element(component, '//*[@id="dropArea"]'),
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert '拖动我' in (await page.locator('//*[@id="dropArea"]').text_content())
        rect = await page.locator('xpath=//*[@id="draggable"]').bounding_box()
        assert abs(rect['x'] - 469) <= 1
        assert rect['y'] == 122
        assert rect['width'] == 100
        assert rect['height'] == 100


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_drag_to_element_with_offset(http_server, headless):
    async with create_component_context(DragWebElementComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page6.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "sourceElementUri": add_test_web_element(component, '//*[@id="draggable"]'),
            "sourceOffset": True,
            "sourceX": '"10"',
            "sourceY": '"20"',
            "dragType": 'to_element',
            "targetElementUri": add_test_web_element(component, '//*[@id="dropArea"]'),
            "targetOffset": True,
            "targetX": '"30"',
            "targetY": '"40"'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert '拖动我' in (await page.locator('//*[@id="dropArea"]').text_content())
        rect = await page.locator('xpath=//*[@id="draggable"]').bounding_box()
        assert abs(rect['x'] - 388) <= 1
        assert rect['y'] == 41
        assert rect['width'] == 100
        assert rect['height'] == 100


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_drag_by_offset(http_server, headless):
    async with create_component_context(DragWebElementComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page6.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "sourceElementUri": add_test_web_element(component, '//*[@id="draggable"]'),
            "sourceOffset": True,
            "sourceX": '"10"',
            "sourceY": '"20"',
            "dragType": 'by_offset',
            "targetOffset": True,
            "dragOffsetX": '"400"',
            "dragOffsetY": '"100"'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert '拖动我' in (await page.locator('//*[@id="dropArea"]').text_content())
        assert await page.locator('xpath=//*[@id="draggable"]').bounding_box() == {'x': 422, 'y': 122,
                                                                                   'width': 100, 'height': 100}
