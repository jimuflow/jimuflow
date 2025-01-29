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
import re

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class SetComboBoxValueComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        select_type = flow_node.input('selectType')
        if select_type == 'by_content':
            match_content = flow_node.input("optionContent")
            match_type = flow_node.input('matchType')
            if match_type == 'equals':
                return gettext(
                    'Select option in combo box ##{element}## with content ##{content}##').format(
                    element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                    content=match_content)
            elif match_type == 'contains':
                return gettext(
                    'Select option in combo box ##{element}## with content containing ##{content}##').format(
                    element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                    content=match_content)
            else:
                return gettext(
                    'Select option in combo box ##{element}## with content matching regex ##{content}##').format(
                    element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                    content=match_content)
        else:
            return gettext(
                'Select the option indexed as ##{index}## in the combo box ##{element}##').format(
                index=flow_node.input('optionIndex'),
                element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri

        element_uri = self.read_input("elementUri")
        wait_time = float(self.read_input("waitTime"))
        control_object = get_element_by_uri(self, element_uri, wait_time)
        select_type = self.read_input('selectType')
        delay_after_action = float(self.read_input("delayAfterAction"))
        if select_type == 'by_content':
            match_content = self.read_input("optionContent")
            match_type = self.read_input('matchType')
            if match_type == 'equals':
                control_object.select(match_content)
            else:
                found_option = None
                options = control_object.texts()
                for option in options:
                    if match_type == 'contains' and match_content in option:
                        found_option = option
                        break
                    elif match_type == 'regex' and re.search(match_content, option):
                        found_option = option
                        break
                if found_option:
                    control_object.select(found_option)
                else:
                    raise IndexError("item '{0}' not found or can't be accessed".format(match_content))
        else:
            option_index = int(self.read_input("optionIndex"))
            control_object.select(option_index)
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
