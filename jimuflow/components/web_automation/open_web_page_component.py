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

import functools
import traceback

from playwright.async_api import BrowserContext

from jimuflow.components.web_automation.playwright_utils import close_page, \
    PlaywrightTimeoutError, stop_loading
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class OpenWebPageComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Open url ##{url}## in ##{webBrowser}##, and save to ##{webPage}##').format(
            url=flow_node.input('url'), webBrowser=flow_node.input('webBrowser'), webPage=flow_node.output('webPage'))

    async def execute(self) -> ControlFlow:
        web_browser: BrowserContext = self.read_input('webBrowser')

        # 打开页面
        url = self.read_input("url")
        page = await web_browser.new_page()

        wait_loaded = self.read_input('waitLoaded')

        if wait_loaded:
            timeout = int(self.read_input('loadTimeout'))
            timeout_action = self.read_input('loadTimeoutAction')
            try:
                await page.goto(url, timeout=timeout * 1000)
            except PlaywrightTimeoutError:
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

        await self.write_output('webPage', page, functools.partial(close_page, self.process))
        return ControlFlow.NEXT
