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

from playwright.async_api import Page

from jimuflow.components.web_automation.playwright_utils import PlaywrightTimeoutError, stop_loading
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class WaitWebPageLoadComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Wait web page ##{webPage}## to load').format(webPage=flow_node.input('webPage'))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input('webPage')
        timeout = float(self.read_input('loadTimeout'))
        timeout_action = self.read_input('loadTimeoutAction')
        try:
            await page.wait_for_load_state(timeout=timeout * 1000)
        except PlaywrightTimeoutError as e:
            if timeout_action == 'throw_error':
                raise
            else:
                self.log_warn(gettext('Loading timeout'), exception=e)
                await stop_loading(page)

        return ControlFlow.NEXT
