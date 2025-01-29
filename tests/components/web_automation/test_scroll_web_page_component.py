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

import asyncio

import pytest

from jimuflow.components.web_automation import ScrollWebPageComponent
from jimuflow.components.web_automation.playwright_utils import open_web_browser
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component_context, add_test_web_element


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_bottom_smooth(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page2.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": False,
            "scrollType": 'bottom',
            "scrollBehavior": 'smooth',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await asyncio.sleep(1)
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 1700


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_bottom_instant(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page2.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": False,
            "scrollType": 'bottom',
            "scrollBehavior": 'instant',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 1700


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_top_smooth(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page2.html')
        await page.evaluate("window.scrollTo(0, 700)")
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 700
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": False,
            "scrollType": 'top',
            "scrollBehavior": 'smooth',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await asyncio.sleep(1)
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_top_instant(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page2.html')
        await page.evaluate("window.scrollTo(0, 700)")
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 700
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": False,
            "scrollType": 'top',
            "scrollBehavior": 'instant',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_page_down_smooth(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page2.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": False,
            "scrollType": 'page',
            "scrollTimes": '"2"',
            "scrollInterval": '"1"',
            "scrollBehavior": 'smooth',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await asyncio.sleep(1)
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 600


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_page_down_instant(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page2.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": False,
            "scrollType": 'page',
            "scrollTimes": '"2"',
            "scrollInterval": '"0.1"',
            "scrollBehavior": 'instant',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 600


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_page_up_smooth(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page2.html')
        await page.evaluate("window.scrollTo(0, 1000)")
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": False,
            "scrollType": 'page',
            "scrollTimes": '"-2"',
            "scrollInterval": '"1"',
            "scrollBehavior": 'smooth',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await asyncio.sleep(1)
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_page_up_instant(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page2.html')
        await page.evaluate("window.scrollTo(0, 1000)")
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": False,
            "scrollType": 'page',
            "scrollTimes": '"-2"',
            "scrollInterval": '"0.1"',
            "scrollBehavior": 'instant',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 400


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_to_element_smooth(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page2.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": False,
            "scrollType": 'element',
            "scrollToElement": add_test_web_element(component, '//*[@id="div2"]'),
            "scrollBehavior": 'smooth',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await asyncio.sleep(1)
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 1000


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_to_element_instant(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page2.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": False,
            "scrollType": 'element',
            "scrollToElement": add_test_web_element(component, '//*[@id="div2"]'),
            "scrollBehavior": 'instant',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        scroll_y = await page.evaluate("window.scrollY")
        assert scroll_y == 1000


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_element_bottom_smooth(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page3.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": True,
            "scrollElement": add_test_web_element(component, '//*[@id="scrollContainer"]'),
            "scrollType": 'bottom',
            "scrollBehavior": 'smooth',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await asyncio.sleep(1)
        scroll_top = await page.locator('xpath=//*[@id="scrollContainer"]').evaluate("ele=>ele.scrollTop")
        assert scroll_top == 1700


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_element_bottom_instant(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page3.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": True,
            "scrollElement": add_test_web_element(component, '//*[@id="scrollContainer"]'),
            "scrollType": 'bottom',
            "scrollBehavior": 'instant',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        scroll_top = await page.locator('xpath=//*[@id="scrollContainer"]').evaluate("ele=>ele.scrollTop")
        assert scroll_top == 1700


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_element_top_smooth(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page3.html')
        scroll_container = page.locator('xpath=//*[@id="scrollContainer"]')
        await scroll_container.evaluate("ele=>ele.scrollTop=1700")
        scroll_top = await scroll_container.evaluate("ele=>ele.scrollTop")
        assert scroll_top == 1700
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": True,
            "scrollElement": add_test_web_element(component, '//*[@id="scrollContainer"]'),
            "scrollType": 'top',
            "scrollBehavior": 'smooth',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await asyncio.sleep(1)
        scroll_top = await scroll_container.evaluate("ele=>ele.scrollTop")
        assert scroll_top == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_element_top_instant(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page3.html')
        scroll_container = page.locator('xpath=//*[@id="scrollContainer"]')
        await scroll_container.evaluate("ele=>ele.scrollTop=1700")
        scroll_top = await scroll_container.evaluate("ele=>ele.scrollTop")
        assert scroll_top == 1700
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": True,
            "scrollElement": add_test_web_element(component, '//*[@id="scrollContainer"]'),
            "scrollType": 'top',
            "scrollBehavior": 'instant',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        scroll_top = await scroll_container.evaluate("ele=>ele.scrollTop")
        assert scroll_top == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_element_page_down_smooth(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page3.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": True,
            "scrollElement": add_test_web_element(component, '//*[@id="scrollContainer"]'),
            "scrollType": 'page',
            "scrollTimes": '"2"',
            "scrollInterval": '"1"',
            "scrollBehavior": 'smooth',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await asyncio.sleep(1)
        scroll_top = await page.locator('xpath=//*[@id="scrollContainer"]').evaluate("ele=>ele.scrollTop")
        assert scroll_top == 600


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_element_page_down_instant(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page3.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": True,
            "scrollElement": add_test_web_element(component, '//*[@id="scrollContainer"]'),
            "scrollType": 'page',
            "scrollTimes": '"2"',
            "scrollInterval": '"0.1"',
            "scrollBehavior": 'instant',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        scroll_top = await page.locator('xpath=//*[@id="scrollContainer"]').evaluate("ele=>ele.scrollTop")
        assert scroll_top == 600


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_element_page_up_smooth(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page3.html')
        scroll_container = page.locator('xpath=//*[@id="scrollContainer"]')
        await scroll_container.evaluate("ele=>ele.scrollTop=1700")
        scroll_top = await scroll_container.evaluate("ele=>ele.scrollTop")
        assert scroll_top == 1700
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": True,
            "scrollElement": add_test_web_element(component, '//*[@id="scrollContainer"]'),
            "scrollType": 'page',
            "scrollTimes": '"-2"',
            "scrollInterval": '"1"',
            "scrollBehavior": 'smooth',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await asyncio.sleep(1)
        scroll_top = await scroll_container.evaluate("ele=>ele.scrollTop")
        assert scroll_top == 1100


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_element_page_up_instant(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page3.html')
        scroll_container = page.locator('xpath=//*[@id="scrollContainer"]')
        await scroll_container.evaluate("ele=>ele.scrollTop=1700")
        scroll_top = await scroll_container.evaluate("ele=>ele.scrollTop")
        assert scroll_top == 1700
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": True,
            "scrollElement": add_test_web_element(component, '//*[@id="scrollContainer"]'),
            "scrollType": 'page',
            "scrollTimes": '"-2"',
            "scrollInterval": '"0.1"',
            "scrollBehavior": 'instant',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        scroll_top = await scroll_container.evaluate("ele=>ele.scrollTop")
        assert scroll_top == 1100


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_element_to_element_smooth(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page3.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": True,
            "scrollElement": add_test_web_element(component, '//*[@id="scrollContainer"]'),
            "scrollType": 'element',
            "scrollToElement": add_test_web_element(component, '//*[@id="div2"]'),
            "scrollBehavior": 'smooth',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        await asyncio.sleep(1)
        scroll_top = await page.locator('xpath=//*[@id="scrollContainer"]').evaluate("ele=>ele.scrollTop")
        assert scroll_top == 1000


@pytest.mark.asyncio
@pytest.mark.parametrize("headless", [True, False])
async def test_scroll_element_to_element_instant(http_server, headless):
    async with create_component_context(ScrollWebPageComponent) as component:
        browser_context = await open_web_browser(component.process, headless=headless)
        page = await browser_context.new_page()
        await page.set_viewport_size({"width": 500, "height": 300})
        await page.goto(f'{http_server}/page3.html')
        await component.process.update_variable('wp', page)
        component.node.inputs = {
            "webPage": 'wp',
            "scrollOnElement": True,
            "scrollElement": add_test_web_element(component, '//*[@id="scrollContainer"]'),
            "scrollType": 'element',
            "scrollToElement": add_test_web_element(component, '//*[@id="div2"]'),
            "scrollBehavior": 'instant',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        scroll_top = await page.locator('xpath=//*[@id="scrollContainer"]').evaluate("ele=>ele.scrollTop")
        assert scroll_top == 1000
