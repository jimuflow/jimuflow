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

import asyncio

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class SetCheckboxValueComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        check_type = flow_node.input('checkType')
        element = describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri'))
        if check_type == 'check':
            return gettext(
                'Check checkbox ##{element}##').format(element=element)
        elif check_type == 'uncheck':
            return gettext(
                'Uncheck checkbox ##{element}##').format(element=element)
        else:
            return gettext(
                'Toggle checkbox ##{element}##').format(element=element)

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri

        element_uri = self.read_input("elementUri")
        wait_time = float(self.read_input("waitTime"))
        control_object = get_element_by_uri(self, element_uri, wait_time)

        check_type = self.read_input('checkType')
        delay_after_action = float(self.read_input("delayAfterAction"))
        toggle_state = control_object.get_toggle_state()  # 0 - unchecked, 1 - checked, 2 - indeterminate
        if check_type == 'check':
            if toggle_state != 1:
                control_object.toggle()
        elif check_type == 'uncheck':
            if toggle_state != 0:
                control_object.toggle()
        elif check_type == 'toggle':
            control_object.toggle()
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
