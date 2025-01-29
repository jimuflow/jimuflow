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

from jimuflow.components.web_automation import CloseWebPageComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_close_one(http_server, headless):
    async with create_component_context(CloseWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page1 = await browser_context.new_page()
        await page1.goto(f'{http_server}/index.html')
        await component.process.update_variable('wp', page1)
        page2 = await browser_context.new_page()
        await page2.goto(f'{http_server}/page1.html')
        component.node.inputs = {
            "closeType": 'page',
            "webPage": 'wp',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert page1.is_closed()
        assert not page2.is_closed()


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_close_all(http_server, headless):
    async with create_component_context(CloseWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page1 = await browser_context.new_page()
        await page1.goto(f'{http_server}/index.html')
        page2 = await browser_context.new_page()
        await page2.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wb', browser_context)
        component.node.inputs = {
            "closeType": 'browser',
            "webBrowser": 'wb'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert page1.is_closed()
        assert page2.is_closed()
