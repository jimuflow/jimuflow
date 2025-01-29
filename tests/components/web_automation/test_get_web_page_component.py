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

from jimuflow.components.web_automation import GetWebPageComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_get_by_title(http_server, headless):
    async with create_component_context(GetWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page1 = await browser_context.new_page()
        await page1.goto(f'{http_server}/index.html')
        page2 = await browser_context.new_page()
        await page2.goto(f'{http_server}/page1.html')
        page3 = await browser_context.new_page()
        await page3.goto(f'{http_server}/page2.html')
        await component.process.update_variable('wb', browser_context)
        component.node.inputs = {
            "webBrowser": 'wb',
            "matchType": 'by_title',
            "matchText": '"Page 1"',
            "useRegexMatch": False
        }
        component.node.outputs = {
            "webPage": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        page = component.process.get_variable('r')
        assert page is page2


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_open_new_page_when_match_failed(http_server, headless):
    async with create_component_context(GetWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page1 = await browser_context.new_page()
        await page1.goto(f'{http_server}/index.html')
        page2 = await browser_context.new_page()
        await page2.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wb', browser_context)
        component.node.inputs = {
            "webBrowser": 'wb',
            "matchType": 'by_title',
            "matchText": '"Page 2"',
            "useRegexMatch": False,
            "openNewPageWhenMatchFailed": True,
            "url": escape_string(f'{http_server}/page2.html')
        }
        component.node.outputs = {
            "webPage": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        page = component.process.get_variable('r')
        assert page is not page1
        assert page is not page2
        assert page.url == f'{http_server}/page2.html'


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_get_by_url(http_server, headless):
    async with create_component_context(GetWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page1 = await browser_context.new_page()
        await page1.goto(f'{http_server}/index.html')
        page2 = await browser_context.new_page()
        await page2.goto(f'{http_server}/page1.html')
        page3 = await browser_context.new_page()
        await page3.goto(f'{http_server}/page2.html')
        await component.process.update_variable('wb', browser_context)
        component.node.inputs = {
            "webBrowser": 'wb',
            "matchType": 'by_url',
            "matchText": escape_string('[a-z]+1'),
            "useRegexMatch": True,
        }
        component.node.outputs = {
            "webPage": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        page = component.process.get_variable('r')
        assert page is page2


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_get_active(http_server, headless):
    async with create_component_context(GetWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page1 = await browser_context.new_page()
        await page1.goto(f'{http_server}/index.html')
        page2 = await browser_context.new_page()
        await page2.goto(f'{http_server}/page1.html')
        page3 = await browser_context.new_page()
        await page3.goto(f'{http_server}/page2.html')
        await component.process.update_variable('wb', browser_context)
        component.node.inputs = {
            "webBrowser": 'wb',
            "matchType": 'active',
        }
        component.node.outputs = {
            "webPage": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        page = component.process.get_variable('r')
        assert page is page3
