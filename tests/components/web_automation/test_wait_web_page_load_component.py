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

from jimuflow.components.web_automation import WaitWebPageLoadComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_execute(http_server, headless):
    async with create_component_context(WaitWebPageLoadComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/index.html?delay=0.3', wait_until='commit')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "loadTimeout": '0.5',
            "loadTimeoutAction": 'stop_loading'
        }
        assert (await component.execute()) == ControlFlow.NEXT


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_stop_loading_when_timeout(http_server, headless):
    async with create_component_context(WaitWebPageLoadComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/index.html?delay=1', wait_until='commit')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "loadTimeout": '0.5',
            "loadTimeoutAction": 'stop_loading'
        }
        assert (await component.execute()) == ControlFlow.NEXT


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_throw_error_when_timeout(http_server, headless):
    async with create_component_context(WaitWebPageLoadComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/index.html?delay=1', wait_until='commit')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "loadTimeout": '0.5',
            "loadTimeoutAction": 'throw_error'
        }
        with pytest.raises(Exception):
            await component.execute()
