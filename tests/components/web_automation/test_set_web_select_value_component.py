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

from jimuflow.components.web_automation import SetWebSelectValueComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize("headless, optionContent,matchType", [
    (True, '项2', 'contains'),
    (True, '选项2', 'equals'),
    (True, '.{2}2', 'regex'),
    (False, '项2', 'contains'),
    (False, '选项2', 'equals'),
    (False, '.{2}2', 'regex'),
])
async def test_select_by_label(http_server, headless, optionContent, matchType):
    async with create_component_context(SetWebSelectValueComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "elementUri": add_test_web_element(component, '//*[@id="test8"]'),
            "selectType": 'by_content',
            "optionContent": escape_string(optionContent),
            "matchType": matchType
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert (await page.locator('//*[@id="test8"]').input_value()) == '2'


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_select_by_index(http_server, headless):
    async with create_component_context(SetWebSelectValueComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "elementUri": add_test_web_element(component, '//*[@id="test8"]'),
            "selectType": 'by_index',
            "optionIndex": '"2"',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert (await page.locator('//*[@id="test8"]').input_value()) == '2'
