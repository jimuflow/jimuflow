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


class ClickWindowElementComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        action = gettext('Single click') if flow_node.input('clickType') == 'single_click' else gettext(
            'Double click')
        return gettext(
            '{action} ##{element}##').format(
            action=action,
            element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')))

    async def execute(self) -> ControlFlow:
        import pywinauto.base_wrapper
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri

        element_uri = self.read_input("elementUri")
        wait_time = float(self.read_input("waitTime"))
        control_object = get_element_by_uri(self, element_uri, wait_time)
        window_object: pywinauto.base_wrapper.BaseWrapper = control_object.top_level_parent()

        click_type = self.read_input('clickType')
        mouse_button = self.read_input('mouseButton')
        modifier_key = self.read_input('modifierKey')
        delay_after_action = float(self.read_input("delayAfterAction"))
        click_kwargs = {
            "button": mouse_button,
            "double": click_type == 'double_click'
        }
        if modifier_key != 'none':
            click_kwargs["pressed"] = modifier_key
        window_object.set_focus()
        control_object.click_input(**click_kwargs)
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
