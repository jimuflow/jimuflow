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

from playwright.async_api import Page, BrowserContext

from jimuflow.components.web_automation.playwright_utils import close_page, close_web_browser
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class CloseWebPageComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        close_type = flow_node.input("closeType")
        if close_type == 'page':
            return gettext('Close web page ##{webPage}##').format(webPage=flow_node.input('webPage'))
        else:
            return gettext('Close browser ##{webBrowser}##').format(webBrowser=flow_node.input('webBrowser'))

    async def execute(self) -> ControlFlow:
        close_type = self.read_input("closeType")
        if close_type == 'page':
            page: Page = self.read_input("webPage")
            if page:
                await close_page(self.process, page)
                await self.process.remove_variable_by_value(page)
        elif close_type == 'browser':
            web_browser: BrowserContext = self.read_input('webBrowser')
            await close_web_browser(self.process, web_browser)
        else:
            raise ValueError(f"Invalid close type: {close_type}")
        return ControlFlow.NEXT
