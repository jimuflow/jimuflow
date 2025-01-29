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

from jimuflow.components.web_automation import LoopWebElementsComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser, get_element_xpath
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import add_mock_component, MockComponent, create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize('headless, reversedLoop', [(True, False), (True, True), (False, False), (False, True)])
async def test_execute(http_server, headless, reversedLoop):
    async with create_component_context(LoopWebElementsComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "elementsUri": add_test_web_element(component, '//*[@id="test11"]/div'),
            "reversedLoop": reversedLoop
        }
        component.node.outputs = {
            "currentElement": 'r'
        }
        loop_item_list = []

        async def mock_loop_body(component: MockComponent):
            loop_item_list.append(component.process.get_variable("r"))
            return ControlFlow.NEXT

        add_mock_component(component, mock_loop_body)
        assert (await component.execute()) == ControlFlow.NEXT
        if reversedLoop:
            loop_item_list.reverse()
        loop_item_list = [await get_element_xpath(item) for item in loop_item_list]
        assert loop_item_list == ['/html/body/div[10]/div[1]/div[1]', '/html/body/div[10]/div[1]/div[2]',
                                  '/html/body/div[10]/div[1]/div[3]']


@pytest.mark.asyncio
@pytest.mark.parametrize("headless, controlFlow",
                         [(True, ControlFlow.BREAK), (True, ControlFlow.RETURN), (True, ControlFlow.EXIT),
                          (False, ControlFlow.BREAK), (False, ControlFlow.RETURN), (False, ControlFlow.EXIT)])
async def test_break(http_server, headless, controlFlow):
    async with create_component_context(LoopWebElementsComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "elementsUri": add_test_web_element(component, '//*[@id="test11"]/div'),
        }
        component.node.outputs = {
            "currentElement": 'r'
        }
        loop_item_list = []

        async def mock_loop_body(component: MockComponent):
            loop_item_list.append(component.process.get_variable("r"))
            if len(loop_item_list) >= 2:
                return controlFlow
            return ControlFlow.NEXT

        add_mock_component(component, mock_loop_body)
        assert (await component.execute()) == (ControlFlow.NEXT if controlFlow == ControlFlow.BREAK else controlFlow)
        loop_item_list = [await get_element_xpath(item) for item in loop_item_list]
        assert loop_item_list == ['/html/body/div[10]/div[1]/div[1]', '/html/body/div[10]/div[1]/div[2]']
