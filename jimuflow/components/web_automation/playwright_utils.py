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
import os
import platform
import time

from playwright.async_api import async_playwright, Playwright, Page, Locator, \
    TimeoutError as PlaywrightTimeoutError, BrowserContext

import jimuflow
from jimuflow.common import get_resource_file
from jimuflow.common.uri_utils import parse_variable_uri, parse_web_element_uri
from jimuflow.common.web_element_utils import parse_xpath
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.common import ProcessVar, ProcessVarScope
from jimuflow.runtime.execution_engine import Process


async def start_playwright():
    return await async_playwright().start()


async def stop_playwright(playwright):
    await playwright.stop()


playwright_var = ProcessVar("playwright")


async def close_page(process: Process, page: Page):
    if not page.is_closed():
        await page.close()
        await process.remove_variable_by_value(page)


async def init_playwright_for_process(process: Process):
    """
    初始化Playwright相关环境
    """
    # 检查Playwright是否已经初始化，如果没有，则先初始化
    playwright: Playwright = process.get_process_var(playwright_var, ProcessVarScope.GLOBAL)
    if playwright is None:
        playwright = await start_playwright()
        await process.set_process_var(playwright_var, playwright, stop_playwright, ProcessVarScope.GLOBAL)

    return playwright


def get_browser_data_dir(browser_type):
    platform_name = platform.system()
    if platform_name == 'Windows':
        local_appdata_dir = os.getenv('LOCALAPPDATA')  # 获取 LocalAppData 路径
        browser_data_dir = os.path.join(local_appdata_dir, jimuflow.__project_name__, browser_type)
        os.makedirs(browser_data_dir, exist_ok=True)  # 确保目录存在
        return browser_data_dir
    elif platform_name == 'Linux':
        home_dir = os.path.expanduser("~")
        browser_data_dir = os.path.join(home_dir, ".local", "share", jimuflow.__project_name__, browser_type)
        os.makedirs(browser_data_dir, exist_ok=True)  # 确保目录存在
        return browser_data_dir
    elif platform_name == 'Darwin':
        home_dir = os.path.expanduser("~")
        browser_data_dir = os.path.join(home_dir, "Library", "Application Support", jimuflow.__project_name__,
                                        browser_type)
        os.makedirs(browser_data_dir, exist_ok=True)  # 确保目录存在
        return browser_data_dir


async def open_web_browser(process: Process, *args, headless=False, incognito=False, **kwargs):
    playwright = await init_playwright_for_process(process)
    if incognito:
        browser = await playwright.chromium.launch(headless=headless)
        web_browser = await browser.new_context(*args, **kwargs)
    else:
        web_browser = await playwright.chromium.launch_persistent_context(get_browser_data_dir('chromium'), *args,
                                                                          headless=headless, **kwargs)
    path = get_resource_file("stealth.min.js")
    await web_browser.add_init_script(path=path.__str__())
    return web_browser


async def close_web_browser(process: Process, web_browser: BrowserContext):
    for page in web_browser.pages:
        await close_page(process, page)
    await web_browser.close()
    if web_browser.browser and len(web_browser.browser.contexts) == 0:
        await web_browser.browser.close()


async def stop_loading(page: Page):
    client = await page.context.new_cdp_session(page)
    try:
        await client.send('Page.stopLoading')
    finally:
        await client.detach()


async def get_element_xpath(element: Locator, timeout: float | None = None) -> str:
    return await element.evaluate("""
        (ele)=>{
            function getXPath(element) {
                if (element === document.body) {
                    return '/html/body';
                }
                let ix = 0;
                let siblings = element.parentNode.childNodes;
                for (let i = 0; i < siblings.length; i++) {
                    let sibling = siblings[i];
                    if (sibling === element) {
                        return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    }
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                        ix++;
                    }
                }
            }
            return getXPath(ele);
        }
        """, timeout=timeout)


async def get_element_by_uri(component: "Component", page: Page, element_uri: str, timeout: float,
                             wait_for_element=True):
    try:
        element_var = parse_variable_uri(element_uri)
        if element_var:
            element = component.process.get_variable(element_var)
        else:
            element_id = parse_web_element_uri(element_uri)
            element_info = component.process.component_def.package.get_web_element_by_id(element_id)
            if element_info['inIframe']:
                frame_locator = await get_frame_locator(page, element_info['iframeXPath'],
                                                        timeout * 1000 if wait_for_element else 0, wait_for_element)
                element = frame_locator.locator("xpath=" + element_info['elementXPath'])
            else:
                element = page.locator("xpath=" + element_info['elementXPath'])
        return element
    except PlaywrightTimeoutError:
        if wait_for_element:
            raise
        else:
            return None


async def get_frame_locator(page: Page, iframe_xpath: str, timeout: float, wait_for_element=True):
    start = time.time()
    xpath_steps = parse_xpath(iframe_xpath)
    context_locator = page
    merged_steps = []
    parent_locator = page
    is_iframe = False
    while xpath_steps:
        step = xpath_steps.pop(0)
        timeout = timeout - (time.time() - start) * 1000
        if timeout <= 0:
            raise Exception(gettext("Timeout to get the element"))
        current_locator = context_locator.locator("xpath=" + step)
        await current_locator.wait_for(state='attached', timeout=timeout if wait_for_element else 0)
        merged_steps.append(step)
        is_iframe = await current_locator.evaluate_all("(nodes)=>nodes.length===1&&nodes[0].tagName==='IFRAME'")
        if is_iframe:
            context_locator = parent_locator.frame_locator("xpath=" + ''.join(merged_steps))
            parent_locator = context_locator
            merged_steps.clear()
        else:
            context_locator = current_locator
    if is_iframe:
        return context_locator
    else:
        raise Exception(gettext("The element is not an iframe"))
