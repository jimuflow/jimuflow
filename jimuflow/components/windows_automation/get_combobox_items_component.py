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


class GetComboBoxItemsComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        extract_type = flow_node.input('extractType')
        if extract_type == 'selected':
            return gettext(
                'Get selected items of the combo box ##{element}##, and save to ##{result}##').format(
                element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                result=flow_node.output('result'))
        else:
            return gettext(
                'Get all items of the combo box ##{element}##, and save to ##{result}##').format(
                element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri

        element_uri = self.read_input("elementUri")
        wait_time = float(self.read_input("waitTime"))
        control_object = get_element_by_uri(self, element_uri, wait_time)

        expand_before_obtaining = self.read_input('expandBeforeObtaining')
        if expand_before_obtaining:
            control_object.expand()
            control_object.collapse()

        extract_type = self.read_input("extractType")
        if extract_type == "selected":
            selection = control_object.get_selection()
            result = [item.name for item in selection]
        else:
            result = control_object.texts()

        await self.write_output('result', result)
        return ControlFlow.NEXT
