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

from jimuflow.components.web_automation import SetWebCheckboxValueComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize("headless, checkboxId,checkType,expected", [
    (True, 'test9', "check", True),
    (True, 'test9', "uncheck", False),
    (True, 'test9', "toggle", True),
    (True, 'test10', "check", True),
    (True, 'test10', "uncheck", False),
    (True, 'test10', "toggle", False),
    (False, 'test9', "check", True),
    (False, 'test9', "uncheck", False),
    (False, 'test9', "toggle", True),
    (False, 'test10', "check", True),
    (False, 'test10', "uncheck", False),
    (False, 'test10', "toggle", False)
])
async def test_check(http_server, headless, checkboxId, checkType, expected):
    async with create_component_context(SetWebCheckboxValueComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "elementUri": add_test_web_element(component, f'//*[@id="{checkboxId}"]'),
            "checkType": checkType
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert (await page.locator(f'//*[@id="{checkboxId}"]').is_checked()) == expected
