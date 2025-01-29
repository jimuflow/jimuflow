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

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class GetRelativeWindowElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        locate_type = flow_node.input("locateType")
        element = describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri'))
        if locate_type == "parent":
            return gettext(
                'Get parent element of ##{element}##, and save to ##{result}##').format(
                element=element, result=flow_node.output('result'))
        elif locate_type == "prev_sibling":
            return gettext(
                'Get previous sibling element of ##{element}##, and save to ##{result}##').format(
                element=element, result=flow_node.output('result'))
        elif locate_type == "next_sibling":
            return gettext(
                'Get next sibling element of ##{element}##, and save to ##{result}##').format(
                element=element, result=flow_node.output('result'))
        elif locate_type == "first_matched_descendant":
            return gettext(
                'Get first matched descendant element of ##{element}## with relative xpath ##{descendantRelativeXpath}##, and save to ##{result}##').format(
                element=element, descendantRelativeXpath=flow_node.input('descendantRelativeXpath'),
                result=flow_node.output('result'))
        elif locate_type == "all_matched_descendants":
            return gettext(
                'Get all matched descendants of ##{element}## with relative xpath ##{descendantRelativeXpath}##, and save to ##{result}##').format(
                element=element, descendantRelativeXpath=flow_node.input('descendantRelativeXpath'),
                result=flow_node.output('result'))
        elif locate_type == "all_children":
            return gettext(
                'Get all children of ##{element}##, and save to ##{result}##').format(
                element=element, result=flow_node.output('result'))
        elif locate_type == "specified_child":
            return gettext(
                'Get ##{childPosition}## child of ##{element}##, and save to ##{result}##').format(
                element=element, result=flow_node.output('result'), childPosition=flow_node.input('childPosition'))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri, find_controls_by_xpath

        element_uri = self.read_input("elementUri")
        wait_time = float(self.read_input("waitTime"))
        control_object = get_element_by_uri(self, element_uri, wait_time)

        locate_type = self.read_input("locateType")
        if locate_type == "parent":
            result = control_object.parent()
        elif locate_type == "prev_sibling":
            siblings = control_object.parent().children()
            idx = siblings.index(control_object)
            result = siblings[idx - 1] if idx > 0 else None
        elif locate_type == "next_sibling":
            siblings = control_object.parent().children()
            idx = siblings.index(control_object)
            result = siblings[idx + 1] if idx < len(siblings) - 1 else None
        elif locate_type == "first_matched_descendant":
            descendant_relative_xpath = self.read_input('descendantRelativeXpath')
            controls = find_controls_by_xpath(control_object, descendant_relative_xpath)
            result = controls[0] if controls else None
        elif locate_type == "all_matched_descendants":
            descendant_relative_xpath = self.read_input('descendantRelativeXpath')
            result = find_controls_by_xpath(control_object, descendant_relative_xpath)
        elif locate_type == "all_children":
            result = control_object.children()
        elif locate_type == "specified_child":
            child_position = int(self.read_input("childPosition"))
            children = control_object.children()
            result = children[child_position] if child_position < len(children) else None
        else:
            raise Exception(gettext("Unsupported locate type: {locate_type}").format(locate_type=locate_type))
        await self.write_output('result', result)
        return ControlFlow.NEXT
