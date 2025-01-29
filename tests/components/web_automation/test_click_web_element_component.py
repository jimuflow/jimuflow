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

from jimuflow.components.core.os_utils import is_macos
from jimuflow.components.web_automation import ClickWebElementComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize("headless, clickType,mouseButton,modifierKey", [
    (True, 'single_click', 'left', 'none'),
    (True, 'single_click', 'left', 'Alt'),
    (True, 'single_click', 'left', 'ControlOrMeta'),
    (True, 'single_click', 'left', 'Shift'),
    (True, 'double_click', 'left', 'none'),
    (True, 'double_click', 'left', 'Alt'),
    (True, 'double_click', 'left', 'ControlOrMeta'),
    (True, 'double_click', 'left', 'Shift'),
    (False, 'single_click', 'left', 'none'),
    (False, 'single_click', 'left', 'Alt'),
    (False, 'single_click', 'left', 'ControlOrMeta'),
    (False, 'single_click', 'left', 'Shift'),
    (False, 'double_click', 'left', 'none'),
    (False, 'double_click', 'left', 'Alt'),
    (False, 'double_click', 'left', 'ControlOrMeta'),
    (False, 'double_click', 'left', 'Shift')
])
async def test_left_click(http_server, headless, clickType, mouseButton, modifierKey):
    async with create_component_context(ClickWebElementComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page5.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "elementUri": add_test_web_element(component, f'//*[@id="{"test1Button" if clickType == "single_click" else "test2Button"}"]'),
            "clickType": clickType,
            "mouseButton": mouseButton,
            "modifierKey": modifierKey
        }
        assert (await component.execute()) == ControlFlow.NEXT
        expected = []
        if modifierKey == 'Control':
            expected.append('ctrl')
        elif modifierKey == 'Meta':
            expected.append('meta')
        elif modifierKey == 'ControlOrMeta':
            if is_macos():
                expected.append('meta')
            else:
                expected.append('ctrl')
        elif modifierKey == 'Shift':
            expected.append('shift')
        elif modifierKey == 'Alt':
            expected.append('alt')
        if mouseButton == 'left':
            expected.append('左键')
        elif mouseButton == 'right':
            expected.append('右键')
        elif mouseButton == 'middle':
            expected.append('中键')
        expected = '+'.join(expected)
        if clickType == 'single_click':
            expected = expected + '单击'
        elif clickType == 'double_click':
            expected = expected + '双击'
        assert (await page.locator('//*[@id="testResult"]').text_content()) == expected
