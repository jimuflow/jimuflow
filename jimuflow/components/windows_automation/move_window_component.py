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


class MoveWindowComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        get_window_method = flow_node.input('getWindowMethod')
        window_position = flow_node.input('windowPosition')
        x = window_position[0]
        y = window_position[1]
        if get_window_method == 'window_object':
            return (gettext('Move the window ##{windowObject}## to (##{x}##, ##{y}##)')
                    .format(windowObject=flow_node.input('windowObject'), x=x, y=y))
        elif get_window_method == 'title':
            title = flow_node.input('title')
            use_class_name = flow_node.input('useClassName')
            if use_class_name:
                return (
                    gettext(
                        'Move the window with the title ##{title}## and type ##{className}## to (##{x}##, ##{y}##)')
                    .format(title=title, className=flow_node.input('className'), x=x, y=y))
            else:
                return (
                    gettext(
                        'Move the window with the title ##{title}## to (##{x}##, ##{y}##)')
                    .format(title=title, x=x, y=y))
        else:
            return (
                gettext(
                    'Move the window of ##{element}## to (##{x}##, ##{y}##)')
                .format(element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                        x=x, y=y))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_window_for_component, move_window

        window_object = get_window_for_component(self)
        window_position = self.read_input('windowPosition')
        x = int(self.evaluate_expression_in_process(window_position[0]))
        y = int(self.evaluate_expression_in_process(window_position[1]))
        move_window(window_object, x=x, y=y)
        return ControlFlow.NEXT
