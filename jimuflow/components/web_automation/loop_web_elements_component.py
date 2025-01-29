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

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.components.web_automation.playwright_utils import get_element_by_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class LoopWebElementsComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Loop elements ##{elements}## on web page ##{webPage}##, save current element to ##{currentElement}##').format(
            elements=describe_element_uri(flow_node.process_def.package, flow_node.input('elementsUri')),
            webPage=flow_node.input('webPage'),
            currentElement=flow_node.output("currentElement"))

    async def execute(self) -> ControlFlow:
        elements_uri = self.read_input("elementsUri")
        page: Page = self.read_input("webPage")
        wait_time = float(self.read_input("waitTime"))
        reversed_loop = self.read_input("reversedLoop")
        elements_locator = await get_element_by_uri(self, page, elements_uri, wait_time)
        elements = await elements_locator.all()
        if reversed_loop:
            elements = elements[::-1]
        for ele in elements:
            await self.write_output('currentElement', ele)
            control_flow = await self.execute_flow()
            if control_flow == ControlFlow.BREAK:
                break
            elif control_flow == ControlFlow.RETURN or control_flow == ControlFlow.EXIT:
                return control_flow
        return ControlFlow.NEXT
