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

import json

import arrow
from playwright.async_api import Page

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class SetCookiesComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Set cookies ##{cookies}## to web page ##{webPage}##').format(cookies=flow_node.input('cookies'),
                                                                          webPage=flow_node.input('webPage'))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input("webPage")
        cookies = self.read_input("cookies")
        if isinstance(cookies, str):
            cookies = json.loads(cookies)
        for cookie in cookies:
            if 'expires' in cookie:
                cookie['expires'] = arrow.get(cookie['expires']).timestamp()
        reload_page = self.read_input('reloadPage')
        await page.context.add_cookies(cookies)
        if reload_page:
            await page.reload()
        return ControlFlow.NEXT
