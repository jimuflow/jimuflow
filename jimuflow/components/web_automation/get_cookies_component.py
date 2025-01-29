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

import arrow
from playwright.async_api import Page, BrowserContext

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class GetCookiesComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        get_type = flow_node.input('getType')
        if get_type == 'page':
            return gettext(
                'Get cookies from web page ##{webPage}##, and save to ##{cookies}##').format(
                webPage=flow_node.input('webPage'), cookies=flow_node.output('cookies'))
        elif get_type == 'url':
            return gettext(
                'Get cookies for url ##{url}## in ##{webBrowser}##, and save to ##{cookies}##').format(
                url=flow_node.input('url'), webBrowser=flow_node.input('webBrowser'),
                cookies=flow_node.output('cookies'))
        else:
            raise Exception(gettext("Invalid get type: {get_type}").format(get_type=get_type))

    async def execute(self) -> ControlFlow:
        get_type = self.read_input("getType")
        if get_type == 'page':
            page: Page = self.read_input("webPage")
            cookies = await page.context.cookies(page.url)
        elif get_type == 'url':
            web_browser: BrowserContext = self.read_input('webBrowser')
            url = self.read_input("url")
            cookies = await web_browser.cookies(url)
        else:
            raise Exception(gettext("Invalid get type: {get_type}").format(get_type=get_type))
        for cookie in cookies:
            if 'expires' in cookie:
                cookie['expires'] = arrow.get(cookie['expires']).format('YYYY.MM.DDTHH:mm.ss.SSSZZ')
        await self.write_output('cookies', cookies)
        return ControlFlow.NEXT
