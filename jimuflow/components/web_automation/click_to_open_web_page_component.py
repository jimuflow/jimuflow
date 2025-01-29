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

from playwright.async_api import Page

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.components.web_automation.playwright_utils import close_page, get_element_by_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ClickToOpenWebPageComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Click ##{element}## on web page ##{webPage}##, and save opened web page to ##{newWebPage}##').format(
            element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
            webPage=flow_node.input('webPage'),
            newWebPage=flow_node.output('newWebPage'))

    async def execute(self) -> ControlFlow:
        element_uri = self.read_input("elementUri")
        page: Page = self.read_input("webPage")
        wait_time = float(self.read_input('waitTime'))
        element = await get_element_by_uri(self, page, element_uri, wait_time)
        async with page.context.expect_page(timeout=wait_time * 1000) as page_info:
            await element.click()

        new_page = await page_info.value

        await self.write_output('newWebPage', new_page, functools.partial(close_page, self.process))

        return ControlFlow.NEXT
