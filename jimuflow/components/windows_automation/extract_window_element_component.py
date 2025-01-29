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


class ExtractWindowElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        extract_type = flow_node.input('extractType')
        if extract_type == 'text':
            extract_data = gettext('text')
        elif extract_type == 'value':
            extract_data = gettext('value')
        elif extract_type == 'attribute_value':
            extract_data = gettext('attribute value')
        elif extract_type == 'position':
            extract_data = gettext('position')
        else:
            extract_data = gettext('?')
        return gettext(
            'Extract the ##{extractData}## of element ##{element}##, and save to ##{result}##').format(
            extractData=extract_data,
            element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
            result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        from pywinauto.controls.uia_controls import EditWrapper, ButtonWrapper, ComboBoxWrapper, SliderWrapper
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri

        element_uri = self.read_input("elementUri")
        wait_time = float(self.read_input("waitTime"))
        control_object = get_element_by_uri(self, element_uri, wait_time)

        extract_type = self.read_input("extractType")
        result = None
        if extract_type == "text":
            result = control_object.window_text()
        elif extract_type == "value":
            if isinstance(control_object, EditWrapper):
                result = control_object.get_value()
            elif isinstance(control_object, ButtonWrapper):
                result = control_object.get_toggle_state()
            elif isinstance(control_object, ComboBoxWrapper):
                result = control_object.selected_text()
            elif isinstance(control_object, SliderWrapper):
                result = control_object.value()
            elif control_object.iface_value:
                return control_object.iface_range_value.CurrentValue
        elif extract_type == "attribute_value":
            attribute_name = self.read_input("attributeName")
            result = control_object.get_properties().get(attribute_name, None)
        elif extract_type == "position":
            rect = control_object.rectangle()
            result = {
                "x": rect.left,
                "y": rect.top,
            }
        else:
            raise Exception("Unsupported extract type: " + extract_type)
        await self.write_output('result', result)
        return ControlFlow.NEXT
