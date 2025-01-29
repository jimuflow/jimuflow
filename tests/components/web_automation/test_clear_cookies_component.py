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

from jimuflow.components.web_automation import ClearCookiesComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_clear_specified_cookie(http_server, headless):
    async with create_component_context(ClearCookiesComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        cookies = [{'name': 'test_cookie1', 'value': 'test_value1', 'url': f'{http_server}/page4.html'},
                   {'name': 'test_cookie2', 'value': 'test_value2', 'url': f'{http_server}/page4.html'}]
        await browser_context.add_cookies(cookies)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page4.html')
        content = await page.content()
        assert 'test_cookie1=test_value1' in content
        assert 'test_cookie2=test_value2' in content
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "clearType": 'specified',
            "cookieName": '"test_cookie1"'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await page.reload()
        content = await page.content()
        assert 'test_cookie1=test_value1' not in content
        assert 'test_cookie2=test_value2' in content


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_clear_all_cookies(http_server, headless):
    async with create_component_context(ClearCookiesComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        cookies = [{'name': 'test_cookie1', 'value': 'test_value1', 'url': f'{http_server}/page4.html'},
                   {'name': 'test_cookie2', 'value': 'test_value2', 'url': f'{http_server}/page4.html'}]
        await browser_context.add_cookies(cookies)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page4.html')
        content = await page.content()
        assert 'test_cookie1=test_value1' in content
        assert 'test_cookie2=test_value2' in content
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "clearType": 'all',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await page.reload()
        content = await page.content()
        assert 'test_cookie1=test_value1' not in content
        assert 'test_cookie2=test_value2' not in content
