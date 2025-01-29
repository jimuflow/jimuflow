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

from jimuflow.components.web_automation import WaitWebContentComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from jimuflow.runtime.expression import escape_string
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_wait_include_element(http_server, headless):
    async with create_component_context(WaitWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "waitType": 'include_element',
            "waitElementUri": add_test_web_element(component, '//*[@id="test2Ele"]'),
            "waitTime": '2',
        }
        component.node.outputs = {
            "waitResult": 'r'
        }
        await page.click('//*[@id="test2Button"]')
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_wait_include_element_timeout(http_server, headless):
    async with create_component_context(WaitWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "waitType": 'include_element',
            "waitElementUri": add_test_web_element(component, '//*[@id="test2Ele"]'),
            "waitTime": '0.5',
        }
        component.node.outputs = {
            "waitResult": 'r'
        }
        with pytest.raises(Exception):
            await component.execute()


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_wait_exclude_element(http_server, headless):
    async with create_component_context(WaitWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "waitType": 'exclude_element',
            "waitElementUri": add_test_web_element(component, '//*[@id="test3Ele"]'),
            "waitTime": '2',
        }
        component.node.outputs = {
            "waitResult": 'r'
        }
        await page.click('//*[@id="test3Button"]')
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_wait_include_text(http_server, headless):
    async with create_component_context(WaitWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "waitType": 'include_text',
            "waitText": escape_string('yqmz'),
            "waitTime": '2',
        }
        component.node.outputs = {
            "waitResult": 'r'
        }
        await page.click('//*[@id="test2Button"]')
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_wait_exclude_text(http_server, headless):
    async with create_component_context(WaitWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "waitType": 'exclude_text',
            "waitText": escape_string('tqhd'),
            "waitTime": '2',
        }
        component.node.outputs = {
            "waitResult": 'r'
        }
        await page.click('//*[@id="test3Button"]')
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_wait_element_is_visible(http_server, headless):
    async with create_component_context(WaitWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "waitType": 'element_is_visible',
            "waitElementUri": add_test_web_element(component, '//*[@id="test1Ele"]'),
            "waitTime": '2',
        }
        component.node.outputs = {
            "waitResult": 'r'
        }
        await page.click('//*[@id="test1Button"]')
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_wait_element_is_invisible(http_server, headless):
    async with create_component_context(WaitWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "waitType": 'element_is_invisible',
            "waitElementUri": add_test_web_element(component, '//*[@id="test4Ele"]'),
            "waitTime": '2',
        }
        component.node.outputs = {
            "waitResult": 'r'
        }
        await page.click('//*[@id="test4Button"]')
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_wait_text_is_visible(http_server, headless):
    async with create_component_context(WaitWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "waitType": 'text_is_visible',
            "waitText": escape_string('jdwk'),
            "waitTime": '2',
        }
        component.node.outputs = {
            "waitResult": 'r'
        }
        await page.click('//*[@id="test1Button"]')
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_wait_text_is_invisible(http_server, headless):
    async with create_component_context(WaitWebContentComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.goto(f'{http_server}/page1.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "waitType": 'text_is_invisible',
            "waitText": escape_string('zfqd'),
            "waitTime": '2',
        }
        component.node.outputs = {
            "waitResult": 'r'
        }
        await page.click('//*[@id="test4Button"]')
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r')
