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

from jimuflow.components.core.os_utils import sleep_at_least
from jimuflow.components.web_automation import CheckWebContentComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_check_include_element(http_server, headless):
    async with create_component_context(CheckWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "checkType": 'include_element',
            "checkElementUri": add_test_web_element(component, '//*[@id="test2Ele"]'),
        }
        component.node.outputs = {
            "checkResult": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert not component.process.get_variable('r')
        await page.click('//*[@id="test2Button"]')
        await sleep_at_least(1)
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_check_exclude_element(http_server, headless):
    async with create_component_context(CheckWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "checkType": 'exclude_element',
            "checkElementUri": add_test_web_element(component, '//*[@id="test3Ele"]'),
        }
        component.node.outputs = {
            "checkResult": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert not component.process.get_variable('r')
        await page.click('//*[@id="test3Button"]')
        await sleep_at_least(1)
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_check_include_text(http_server, headless):
    async with create_component_context(CheckWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "checkType": 'include_text',
            "checkText": escape_string('yqmz'),
        }
        component.node.outputs = {
            "checkResult": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert not component.process.get_variable('r')
        await page.click('//*[@id="test2Button"]')
        await sleep_at_least(1)
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_check_exclude_text(http_server, headless):
    async with create_component_context(CheckWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "checkType": 'exclude_text',
            "checkText": escape_string('tqhd'),
        }
        component.node.outputs = {
            "checkResult": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert not component.process.get_variable('r')
        await page.click('//*[@id="test3Button"]')
        await sleep_at_least(1)
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_check_element_is_visible(http_server, headless):
    async with create_component_context(CheckWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "checkType": 'element_is_visible',
            "checkElementUri": add_test_web_element(component, '//*[@id="test1Ele"]'),
        }
        component.node.outputs = {
            "checkResult": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert not component.process.get_variable('r')
        await page.click('//*[@id="test1Button"]')
        await sleep_at_least(1)
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_check_element_is_invisible(http_server, headless):
    async with create_component_context(CheckWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "checkType": 'element_is_invisible',
            "checkElementUri": add_test_web_element(component, '//*[@id="test4Ele"]'),
        }
        component.node.outputs = {
            "checkResult": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert not component.process.get_variable('r')
        await page.click('//*[@id="test4Button"]')
        await sleep_at_least(1)
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_check_text_is_visible(http_server, headless):
    async with create_component_context(CheckWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "checkType": 'text_is_visible',
            "checkText": escape_string('jdwk'),
        }
        component.node.outputs = {
            "checkResult": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert not component.process.get_variable('r')
        await page.click('//*[@id="test1Button"]')
        await sleep_at_least(1)
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_check_text_is_invisible(http_server, headless):
    async with create_component_context(CheckWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "checkType": 'text_is_invisible',
            "checkText": escape_string('zfqd'),
        }
        component.node.outputs = {
            "checkResult": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert not component.process.get_variable('r')
        await page.click('//*[@id="test4Button"]')
        await sleep_at_least(1)
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')
