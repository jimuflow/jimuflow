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

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ClearCookiesComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        clear_type = flow_node.input('clearType')
        if clear_type == 'all':
            return gettext('Clear all cookies of web page ##{webPage}##').format(webPage=flow_node.input('webPage'))
        elif clear_type == 'specified':
            return gettext('Clear cookie ##{cookieName}## of web page ##{webPage}##').format(
                cookieName=flow_node.input('cookieName'), webPage=flow_node.input('webPage'))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input("webPage")
        clear_type = self.read_input('clearType')
        if clear_type == 'all':
            await page.context.clear_cookies()
        elif clear_type == 'specified':
            cookie_name = self.read_input("cookieName")
            await page.context.clear_cookies(name=cookie_name)
        return ControlFlow.NEXT
