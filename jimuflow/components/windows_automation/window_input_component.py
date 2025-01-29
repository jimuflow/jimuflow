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


class WindowInputComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Input ##{content}## into element ##{element}##').format(
            content=flow_node.input('content'),
            element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri, type_text, \
            move_text_cursor_to_end

        element_uri = self.read_input("elementUri")
        wait_time = float(self.read_input("waitTime"))
        control_object = get_element_by_uri(self, element_uri, wait_time)

        content = self.read_input("content")
        append = self.read_input("append")

        input_method = self.read_input('inputMethod')
        delay_after_focus = float(self.read_input("delayAfterFocus"))
        delay_after_action = float(self.read_input("delayAfterAction"))
        press_enter_after_input = self.read_input("pressEnterAfterInput")
        press_tab_after_input = self.read_input("pressTabAfterInput")

        control_object.set_focus()
        if delay_after_focus > 0:
            await asyncio.sleep(delay_after_focus)

        if input_method == 'simulate':
            include_shortcut_keys = self.read_input("includeShortcutKeys")
            click_before_input = self.read_input("clickBeforeInput")
            input_interval = float(self.read_input('inputInterval')) / 1000
            if click_before_input:
                control_object.click_input()
            if not append:
                control_object.type_keys("^a{BACKSPACE}", pause=input_interval, set_foreground=False)
                if control_object.window_text():
                    control_object.set_text("")
            else:
                move_text_cursor_to_end(control_object)
            if include_shortcut_keys:
                control_object.type_keys(content, pause=input_interval, set_foreground=False, with_spaces=True,
                                         with_tabs=True, with_newlines=True)
            else:
                type_text(control_object, content, pause=input_interval, set_foreground=False)
        else:
            if append:
                content = control_object.window_text() + content
            control_object.set_text(content)
            move_text_cursor_to_end(control_object)
        if press_enter_after_input:
            control_object.type_keys("{ENTER}", set_foreground=False)
        if press_tab_after_input:
            control_object.type_keys("{TAB}", set_foreground=False)
        if delay_after_action > 0:
            await asyncio.sleep(delay_after_action)
        return ControlFlow.NEXT
