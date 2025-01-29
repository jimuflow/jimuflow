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


class WaitWebContentComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        wait_type = flow_node.input('waitType')
        if wait_type == 'include_element':
            action = gettext("include element")
            target = describe_element_uri(flow_node.process_def.package, flow_node.input('waitElementUri'))
        elif wait_type == 'exclude_element':
            action = gettext("exclude element")
            target = describe_element_uri(flow_node.process_def.package, flow_node.input('waitElementUri'))
        elif wait_type == 'include_text':
            action = gettext("include text")
            target = flow_node.input('waitText')
        elif wait_type == 'exclude_text':
            action = gettext("exclude text")
            target = flow_node.input('waitText')
        elif wait_type == 'element_is_visible':
            action = gettext("can see element")
            target = describe_element_uri(flow_node.process_def.package, flow_node.input('waitElementUri'))
        elif wait_type == 'element_is_invisible':
            action = gettext("cannot see element")
            target = describe_element_uri(flow_node.process_def.package, flow_node.input('waitElementUri'))
        elif wait_type == 'text_is_visible':
            action = gettext("can see text")
            target = flow_node.input('waitText')
        elif wait_type == 'text_is_invisible':
            action = gettext("cannot see text")
            target = flow_node.input('waitText')
        else:
            raise Exception(gettext("Invalid wait type: {wait_type}").format(wait_type=wait_type))
        return gettext(
            'Wait web page ##{webPage}## {action} {target}').format(action=action,
                                                                    target=target,
                                                                    webPage=flow_node.input('webPage'))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input("webPage")
        wait_type = self.read_input('waitType')
        wait_time = float(self.read_input("waitTime"))
        if wait_type == 'include_element' or wait_type == 'element_is_visible':
            wait_element_uri = self.read_input("waitElementUri")
            element = await get_element_by_uri(self, page, wait_element_uri, wait_time)
            await element.wait_for(
                timeout=wait_time * 1000,
                state={'include_element': 'attached', 'element_is_visible': 'visible', }[wait_type])
        elif wait_type == 'exclude_element' or wait_type == 'element_is_invisible':
            wait_element_uri = self.read_input("waitElementUri")
            element = await get_element_by_uri(self, page, wait_element_uri, wait_time, False)
            if element:
                await element.wait_for(
                    timeout=wait_time * 1000,
                    state={'exclude_element': 'detached', 'element_is_invisible': 'hidden'}[wait_type])
        elif (wait_type == 'include_text' or wait_type == 'exclude_text' or wait_type == 'text_is_visible'
              or wait_type == 'text_is_invisible'):
            wait_text = self.read_input("waitText")
            await page.get_by_text(wait_text).nth(0).wait_for(
                timeout=wait_time * 1000,
                state={'include_text': 'attached', 'exclude_text': 'detached', 'text_is_visible': 'visible',
                       'text_is_invisible': 'hidden'}[wait_type])
        else:
            raise Exception(gettext("Invalid wait type: {wait_type}").format(wait_type=wait_type))
        await self.write_output("waitResult", True)
        return ControlFlow.NEXT
