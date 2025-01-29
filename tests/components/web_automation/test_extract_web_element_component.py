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

from jimuflow.components.web_automation import ExtractWebElementComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize('headless, xpath, extractType, attributeName, expected', [
    (True, '//*[@id="test1"]', 'text', None, '首页'),
    (True, '//*[@id="test1"]', 'html', None, '<a id="test2" href="./index.html">首页</a>'),
    (True, '//*[@id="test3"]', 'input_value', None, '测试输入li87'),
    (True, '//*[@id="test2"]', 'link_href', None, './index.html'),
    (True, '//*[@id="test3"]', 'attribute_value', 'data-foo', 'brjs91'),
    (True, '//*[@id="test4"]', 'position', None, {'x': 0, 'y': 50}),
    (False, '//*[@id="test1"]', 'text', None, '首页'),
    (False, '//*[@id="test1"]', 'html', None, '<a id="test2" href="./index.html">首页</a>'),
    (False, '//*[@id="test3"]', 'input_value', None, '测试输入li87'),
    (False, '//*[@id="test2"]', 'link_href', None, './index.html'),
    (False, '//*[@id="test3"]', 'attribute_value', 'data-foo', 'brjs91'),
    (False, '//*[@id="test4"]', 'position', None, {'x': 0, 'y': 50}),
])
async def test_execute(http_server, headless, xpath, extractType, attributeName, expected):
    async with create_component_context(ExtractWebElementComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page7.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "elementUri": add_test_web_element(component, xpath),
            "extractType": extractType,
            "attributeName": escape_string(attributeName) if attributeName else None
        }
        component.node.outputs = {
            "result": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == expected
