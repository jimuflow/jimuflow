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

import re
import traceback

from playwright.async_api import Page, BrowserContext

from jimuflow.components.web_automation.playwright_utils import close_page, stop_loading
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class GetWebPageComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Get web page ##{matchType}## from ##{webBrowser}##, and save to ##{webPage}##').format(
            matchType=flow_node.input('matchType'), webBrowser=flow_node.input('webBrowser'),
            webPage=flow_node.output('webPage'))

    async def execute(self) -> ControlFlow:
        web_browser: BrowserContext = self.read_input('webBrowser')

        # 查找网页
        match_type = self.read_input('matchType')
        if match_type == 'by_title':
            match_text = self.read_input('matchText')
            use_regex_match = self.read_input('useRegexMatch')

            async def match_by_title(page: Page):
                page_title = await page.title()
                if use_regex_match:
                    return re.search(match_text, page_title, re.IGNORECASE)
                return match_text.lower() in page_title.lower()

            match_function = match_by_title
        elif match_type == 'by_url':
            match_text = self.read_input('matchText')
            use_regex_match = self.read_input('useRegexMatch')

            async def match_by_url(page: Page):
                page_url = page.url
                if use_regex_match:
                    return re.search(match_text, page_url, re.IGNORECASE)
                return match_text.lower() in page_url.lower()

            match_function = match_by_url
        elif match_type == 'active':
            active_page = web_browser.pages[-1] if len(web_browser.pages) > 0 else None

            async def match_by_active(page: Page):
                return page is active_page

            match_function = match_by_active
        else:
            raise Exception(f"Invalid match type: {match_type}")

        found_page = None
        for page in web_browser.pages:
            if await match_function(page):
                found_page = page
                break
        open_new_page = self.read_input('openNewPageWhenMatchFailed')
        if found_page:
            wait_loaded = self.read_input('waitLoaded')
            if wait_loaded:
                timeout = int(self.read_input('loadTimeout'))
                timeout_action = self.read_input('loadTimeoutAction')
                try:
                    await found_page.wait_for_load_state(timeout=timeout * 1000)
                except:
                    if timeout_action == 'throw_error':
                        raise
                    else:
                        print('stop loading for error: {}'.format(traceback.format_exc()))
                        await stop_loading(found_page)
        elif open_new_page:
            # 打开页面
            url = self.read_input("url")
            page = await web_browser.new_page()

            wait_loaded = self.read_input('waitLoaded')

            if wait_loaded:
                timeout = int(self.read_input('loadTimeout'))
                timeout_action = self.read_input('loadTimeoutAction')
                try:
                    await page.goto(url, timeout=timeout * 1000)
                except:
                    if timeout_action == 'throw_error':
                        await close_page(self.process, page)
                        raise
                    else:
                        print('stop loading for error: {}'.format(traceback.format_exc()))
                        await stop_loading(page)
            else:
                try:
                    await page.goto(url, wait_until='commit')
                except:
                    await close_page(self.process, page)
                    raise
            found_page = page
        else:
            raise Exception("No page found")

        await self.write_output("webPage", found_page)
        return ControlFlow.NEXT
