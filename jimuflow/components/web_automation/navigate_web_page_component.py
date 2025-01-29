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

import traceback

from playwright.async_api import Page

from jimuflow.components.web_automation.playwright_utils import PlaywrightTimeoutError, stop_loading
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class NavigateWebPageComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        navigate_type = flow_node.input('navigateType')
        if navigate_type == 'goto':
            return gettext(
                'Navigate web page ##{webPage}## to ##{url}##').format(
                url=flow_node.input('url'), webPage=flow_node.input('webPage'))
        else:
            action = {
                "go_back": gettext("Go back"),
                "go_forward": gettext("Go forward"),
                "reload": gettext("Reload")
            }
            return gettext('{action} web page ##{webPage}##').format(action=action[navigate_type],
                                                                     webPage=flow_node.input('webPage'))

    async def execute(self) -> ControlFlow:
        navigate_type = self.read_input('navigateType')
        page: Page = self.read_input('webPage')
        if navigate_type == 'goto':
            url = self.read_input("url")
            await page.goto(url, wait_until='commit')
        elif navigate_type == 'go_back':
            await page.go_back(wait_until='commit')
        elif navigate_type == 'go_forward':
            await page.go_forward(wait_until='commit')
        elif navigate_type == 'reload':
            await page.reload(wait_until='commit')

        wait_loaded = self.read_input('waitLoaded')
        if wait_loaded:
            timeout = int(self.read_input('loadTimeout'))
            timeout_action = self.read_input('loadTimeoutAction')
            try:
                await page.wait_for_load_state(timeout=timeout * 1000)
            except PlaywrightTimeoutError:
                if timeout_action == 'throw_error':
                    raise
                else:
                    print('stop loading for error: {}'.format(traceback.format_exc()))
                    await stop_loading(page)

        return ControlFlow.NEXT
