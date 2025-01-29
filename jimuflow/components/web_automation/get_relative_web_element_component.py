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


class GetRelativeWebElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        locate_type = flow_node.input("locateType")
        element = describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri'))
        if locate_type == "parent":
            return gettext(
                'Get parent element of ##{element}## on web page ##{webPage}##, and save to ##{result}##').format(
                element=element, webPage=flow_node.input('webPage'), result=flow_node.output('result'))
        elif locate_type == "prev_sibling":
            return gettext(
                'Get previous sibling element of ##{element}## on web page ##{webPage}##, and save to ##{result}##').format(
                element=element, webPage=flow_node.input('webPage'), result=flow_node.output('result'))
        elif locate_type == "next_sibling":
            return gettext(
                'Get next sibling element of ##{element}## on web page ##{webPage}##, and save to ##{result}##').format(
                element=element, webPage=flow_node.input('webPage'), result=flow_node.output('result'))
        elif locate_type == "first_matched_descendant":
            return gettext(
                'Get first matched descendant element of ##{element}## on web page ##{webPage}## with relative xpath ##{descendantRelativeXpath}##, and save to ##{result}##').format(
                element=element, webPage=flow_node.input('webPage'),
                descendantRelativeXpath=flow_node.input('descendantRelativeXpath'), result=flow_node.output('result'))
        elif locate_type == "all_matched_descendants":
            return gettext(
                'Get all matched descendants of ##{element}## on web page ##{webPage}## with relative xpath ##{descendantRelativeXpath}##, and save to ##{result}##').format(
                element=element, webPage=flow_node.input('webPage'),
                descendantRelativeXpath=flow_node.input('descendantRelativeXpath'), result=flow_node.output('result'))
        elif locate_type == "all_children":
            return gettext(
                'Get all children of ##{element}## on web page ##{webPage}##, and save to ##{result}##').format(
                element=element, webPage=flow_node.input('webPage'), result=flow_node.output('result'))
        elif locate_type == "specified_child":
            return gettext(
                'Get ##{childPosition}## child of ##{element}## on web page ##{webPage}##, and save to ##{result}##').format(
                element=element, webPage=flow_node.input('webPage'), result=flow_node.output('result'),
                childPosition=flow_node.input('childPosition'))

    async def execute(self) -> ControlFlow:
        element_uri = self.read_input("elementUri")
        page: Page = self.read_input("webPage")
        locate_type = self.read_input("locateType")
        wait_time = float(self.read_input("waitTime"))
        locator = await get_element_by_uri(self, page, element_uri, wait_time)
        if locate_type == "parent":
            result = locator.locator("xpath=..")
        elif locate_type == "prev_sibling":
            result = locator.locator("xpath=preceding-sibling::*[1]")
        elif locate_type == "next_sibling":
            result = locator.locator("xpath=following-sibling::*[1]")
        elif locate_type == "first_matched_descendant":
            descendant_relative_xpath = self.read_input('descendantRelativeXpath')
            result = locator.locator("xpath=" + descendant_relative_xpath).nth(0)
        elif locate_type == "all_matched_descendants":
            descendant_relative_xpath = self.read_input('descendantRelativeXpath')
            result = locator.locator("xpath=" + descendant_relative_xpath)
        elif locate_type == "all_children":
            result = locator.locator("xpath=*")
        elif locate_type == "specified_child":
            child_position = int(self.read_input("childPosition"))
            result = locator.locator("xpath=*").nth(child_position)
        else:
            raise Exception(gettext("Unsupported locate type: {locate_type}").format(locate_type=locate_type))
        await self.write_output('result', result)
        return ControlFlow.NEXT
