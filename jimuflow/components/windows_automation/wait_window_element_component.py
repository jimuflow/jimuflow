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


class WaitWindowElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        wait_type = flow_node.input('waitType')
        target = describe_element_uri(flow_node.process_def.package, flow_node.input('waitElementUri'))
        if wait_type == 'include_element':
            action = gettext("include element")
        elif wait_type == 'exclude_element':
            action = gettext("exclude element")
        else:
            raise Exception(gettext("Invalid wait type: {wait_type}").format(wait_type=wait_type))
        return gettext(
            'Waiting to ##{action}## ##{target}##, and save to ##{waitResult}##').format(
            action=action, target=target, waitResult=flow_node.output('waitResult'))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri
        from pywinauto.timings import wait_until, TimeoutError
        element_uri = self.read_input("waitElementUri")
        wait_type = self.read_input("waitType")
        with_timeout = self.read_input("withTimeout")
        if with_timeout:
            timeout = float(self.read_input("timeout"))
        else:
            timeout = 0

        def is_element_exist():
            element = get_element_by_uri(self, element_uri, 0, False)
            return element is not None and element.element_info.control_type is not None

        if wait_type == 'include_element':
            if timeout == 0:
                await self.write_output('waitResult', is_element_exist())
            else:
                try:
                    wait_until(timeout, 0.1, is_element_exist)
                    await self.write_output('waitResult', True)
                except TimeoutError:
                    await self.write_output('waitResult', False)
        else:
            if timeout == 0:
                await self.write_output('waitResult', not is_element_exist())
            else:
                try:
                    wait_until(timeout, 0.1, is_element_exist, value=False)
                    await self.write_output('waitResult', True)
                except TimeoutError:
                    await self.write_output('waitResult', False)

        return ControlFlow.NEXT
