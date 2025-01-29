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

from jimuflow.components.web_automation import GetRelativeWebElementComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser, get_element_xpath
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize('headless, xpath, locateType, descendantRelativeXpath, childPosition, expected', [
    (True, '//*[@id="test14"]', 'parent', '', '', '/html/body/div[11]/div[1]'),
    (True, '//*[@id="test14"]', 'prev_sibling', '', '', '/html/body/div[11]/div[1]/div[1]'),
    (True, '//*[@id="test14"]', 'next_sibling', '', '', '/html/body/div[11]/div[1]/div[3]'),
    (True, '//*[@id="test12"]', 'first_matched_descendant', 'div[2]', '', '/html/body/div[11]/div[1]/div[2]'),
    (True, '//*[@id="test12"]', 'all_matched_descendants', '//div', '',
     ['/html/body/div[11]/div[1]/div[1]', '/html/body/div[11]/div[1]/div[2]', '/html/body/div[11]/div[1]/div[2]/div[1]',
      '/html/body/div[11]/div[1]/div[3]']),
    (True, '//*[@id="test12"]', 'all_children', '', '',
     ['/html/body/div[11]/div[1]/div[1]', '/html/body/div[11]/div[1]/div[2]', '/html/body/div[11]/div[1]/div[3]']),
    (True, '//*[@id="test12"]', 'specified_child', '', '1', '/html/body/div[11]/div[1]/div[2]'),
    (False, '//*[@id="test14"]', 'parent', '', '', '/html/body/div[11]/div[1]'),
    (False, '//*[@id="test14"]', 'prev_sibling', '', '', '/html/body/div[11]/div[1]/div[1]'),
    (False, '//*[@id="test14"]', 'next_sibling', '', '', '/html/body/div[11]/div[1]/div[3]'),
    (False, '//*[@id="test12"]', 'first_matched_descendant', 'div[2]', '', '/html/body/div[11]/div[1]/div[2]'),
    (False, '//*[@id="test12"]', 'all_matched_descendants', '//div', '',
     ['/html/body/div[11]/div[1]/div[1]', '/html/body/div[11]/div[1]/div[2]', '/html/body/div[11]/div[1]/div[2]/div[1]',
      '/html/body/div[11]/div[1]/div[3]']),
    (False, '//*[@id="test12"]', 'all_children', '', '',
     ['/html/body/div[11]/div[1]/div[1]', '/html/body/div[11]/div[1]/div[2]', '/html/body/div[11]/div[1]/div[3]']),
    (False, '//*[@id="test12"]', 'specified_child', '', '1', '/html/body/div[11]/div[1]/div[2]')
])
async def test_execute(http_server, headless, xpath, locateType, descendantRelativeXpath, childPosition, expected):
    async with create_component_context(GetRelativeWebElementComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "elementUri": add_test_web_element(component, xpath),
            "locateType": locateType,
            "descendantRelativeXpath": escape_string(descendantRelativeXpath),
            "childPosition": escape_string(childPosition)
        }
        component.node.outputs = {
            "result": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        if isinstance(expected, list):
            result_xpath = [await get_element_xpath(item) for item in await component.process.get_variable('r').all()]
        else:
            result_xpath = await get_element_xpath(component.process.get_variable('r'))
        assert result_xpath == expected
