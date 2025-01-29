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


class ExtractWebElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        extract_type = flow_node.input('extractType')
        if extract_type == 'text':
            extract_data = gettext('text content')
        elif extract_type == 'html':
            extract_data = gettext('html content')
        elif extract_type == 'input_value':
            extract_data = gettext('input value')
        elif extract_type == 'attribute_value':
            extract_data = gettext('attribute value')
        elif extract_type == 'position':
            extract_data = gettext('position')
        else:
            extract_data = gettext('?')
        return gettext(
            'Extract the ##{extractData}## of element ##{element}## on web page ##{webPage}##, and save to ##{result}##').format(
            element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
            extractData=extract_data,
            webPage=flow_node.input('webPage'), result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        element_uri = self.read_input("elementUri")
        page: Page = self.read_input("webPage")
        extract_type = self.read_input("extractType")
        wait_time = int(self.read_input("waitTime"))
        locator = await get_element_by_uri(self, page, element_uri, wait_time)
        if extract_type == "text":
            result = await locator.inner_text(timeout=wait_time * 1000)
        elif extract_type == "html":
            result = await locator.inner_html(timeout=wait_time * 1000)
        elif extract_type == "input_value":
            result = await locator.input_value(timeout=wait_time * 1000)
        elif extract_type == "link_href":
            result = await locator.get_attribute("href", timeout=wait_time * 1000)
        elif extract_type == "attribute_value":
            attribute_name = self.read_input("attributeName")
            result = await locator.get_attribute(attribute_name, timeout=wait_time * 1000)
        elif extract_type == "position":
            bounding_box = await locator.bounding_box(timeout=wait_time * 1000)
            result = {
                "x": bounding_box["x"],
                "y": bounding_box["y"],
            }
        else:
            raise Exception("Unsupported extract type: " + extract_type)
        await self.write_output('result', result)
        return ControlFlow.NEXT
