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


class CheckWebContentComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        check_type = flow_node.input('checkType')
        if check_type == 'include_element':
            action = gettext("include element")
            target = describe_element_uri(flow_node.process_def.package, flow_node.input('checkElementUri'))
        elif check_type == 'exclude_element':
            action = gettext("exclude element")
            target = describe_element_uri(flow_node.process_def.package, flow_node.input('checkElementUri'))
        elif check_type == 'include_text':
            action = gettext("include text")
            target = flow_node.input('checkText')
        elif check_type == 'exclude_text':
            action = gettext("exclude text")
            target = flow_node.input('checkText')
        elif check_type == 'element_is_visible':
            action = gettext("can see element")
            target = describe_element_uri(flow_node.process_def.package, flow_node.input('checkElementUri'))
        elif check_type == 'element_is_invisible':
            action = gettext("cannot see element")
            target = describe_element_uri(flow_node.process_def.package, flow_node.input('checkElementUri'))
        elif check_type == 'text_is_visible':
            action = gettext("can see text")
            target = flow_node.input('checkText')
        elif check_type == 'text_is_invisible':
            action = gettext("cannot see text")
            target = flow_node.input('checkText')
        else:
            raise Exception(gettext("Invalid check type: {check_type}").format(check_type=check_type))
        return gettext(
            'Check if web page ##{webPage}## ##{action}## ##{target}##, save result to ##{checkResult}##').format(
            action=action, target=target, webPage=flow_node.input('webPage'),
            checkResult=flow_node.output('checkResult'))

    async def execute(self) -> ControlFlow:
        page: Page = self.read_input("webPage")
        check_type = self.read_input('checkType')
        if check_type == 'include_element' or check_type == 'exclude_element':
            check_element_uri = self.read_input("checkElementUri")
            element = await get_element_by_uri(self, page, check_element_uri, 0, wait_for_element=False)
            count = (await element.count()) if element else 0
            check_result = count > 0 if check_type == 'include_element' else count == 0
        elif check_type == 'element_is_visible' or check_type == 'element_is_invisible':
            check_element_uri = self.read_input("checkElementUri")
            element = await get_element_by_uri(self, page, check_element_uri, 0, wait_for_element=False)
            visible = (await element.is_visible()) if element else False
            check_result = visible if check_type == 'element_is_visible' else not visible
        elif check_type == 'include_text' or check_type == 'exclude_text':
            check_text = self.read_input("checkText")
            count = await page.get_by_text(check_text).count()
            check_result = count > 0 if check_type == 'include_text' else count == 0
        elif check_type == 'text_is_visible' or check_type == 'text_is_invisible':
            check_text = self.read_input("checkText")
            visible = await page.get_by_text(check_text).is_visible()
            check_result = visible if check_type == 'text_is_visible' else not visible
        else:
            raise Exception(gettext("Invalid check type: {check_type}").format(check_type=check_type))
        await self.write_output("checkResult", check_result)
        return ControlFlow.NEXT
