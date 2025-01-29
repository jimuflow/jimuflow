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

import os.path

import pytest

from jimuflow.components.web_automation import WebUploadComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_execute(http_server, headless):
    async with create_component_context(WebUploadComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html?expected=')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "elementUri": add_test_web_element(component, '//*[@id="test17"]'),
            "filePath": escape_string(os.path.join(os.path.dirname(__file__), 'file.dat'))
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await page.locator('xpath=//*[@id="test18"]').click()
        assert page.url == f'{http_server}/index.html'
