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

from jimuflow.components.web_automation import ExtractWebPageComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context


@pytest.mark.asyncio
@pytest.mark.parametrize('headless, extractType, expected', [
    (True, 'title', 'Home - jimuflow网页自动化测试'),
    (True, 'url', '/index.html'),
    (True, 'html', '<title>Home - jimuflow网页自动化测试</title>'),
    (True, 'text', 'Home'),
    (False, 'title', 'Home - jimuflow网页自动化测试'),
    (False, 'url', '/index.html'),
    (False, 'html', '<title>Home - jimuflow网页自动化测试</title>'),
    (False, 'text', 'Home')
])
async def test_execute(http_server, headless, extractType, expected):
    async with create_component_context(ExtractWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/index.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "extractType": extractType
        }
        component.node.outputs = {
            "result": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert expected in component.process.get_variable('r')
