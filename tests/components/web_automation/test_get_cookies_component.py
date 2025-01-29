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

from jimuflow.components.web_automation import GetCookiesComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_get_page_cookies(http_server, headless):
    async with create_component_context(GetCookiesComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        cookies = [{'name': 'test_cookie1', 'value': 'test_value1', 'url': f'{http_server}/page4.html'},
                   {'name': 'test_cookie2', 'value': 'test_value2', 'url': f'{http_server}/page4.html'},
                   {'name': 'test_cookie3', 'value': 'test_value3', 'url': f'http://www.baidu.com/index.html'}]
        await browser_context.add_cookies(cookies)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page4.html')
        content = await page.content()
        assert 'test_cookie1=test_value1' in content
        assert 'test_cookie2=test_value2' in content
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "getType": 'page',
            "webPage": 'wp',
        }
        component.node.outputs = {
            'cookies': 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r = component.process.get_variable('r')
        assert len(r) == 2
        assert any(cookie['name'] == 'test_cookie1' and cookie['value'] == 'test_value1' for cookie in r)
        assert any(cookie['name'] == 'test_cookie2' and cookie['value'] == 'test_value2' for cookie in r)


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_get_url_cookies(http_server, headless):
    async with create_component_context(GetCookiesComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        cookies = [{'name': 'test_cookie1', 'value': 'test_value1', 'url': f'{http_server}/page4.html'},
                   {'name': 'test_cookie2', 'value': 'test_value2', 'url': f'{http_server}/page4.html'},
                   {'name': 'test_cookie3', 'value': 'test_value3', 'url': f'http://www.baidu.com/index.html'}]
        await browser_context.add_cookies(cookies)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page4.html')
        content = await page.content()
        assert 'test_cookie1=test_value1' in content
        assert 'test_cookie2=test_value2' in content
        await component.process.update_variable('wb', browser_context)
        component.node.inputs = {
            "getType": 'url',
            "url": escape_string(f'{http_server}/page4.html'),
            "webBrowser": 'wb'
        }
        component.node.outputs = {
            'cookies': 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        r = component.process.get_variable('r')
        assert len(r) == 2
        assert any(cookie['name'] == 'test_cookie1' and cookie['value'] == 'test_value1' for cookie in r)
        assert any(cookie['name'] == 'test_cookie2' and cookie['value'] == 'test_value2' for cookie in r)
