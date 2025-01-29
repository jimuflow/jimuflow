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


class ResizeWindowComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        get_window_method = flow_node.input('getWindowMethod')
        window_size = flow_node.input('windowSize')
        width = window_size[0] if window_size else '?'
        height = window_size[1] if window_size else '?'
        if get_window_method == 'window_object':
            return (gettext('Set the width of window ##{windowObject}## to ##{width}## and the height to ##{height}##')
                    .format(windowObject=flow_node.input('windowObject'), width=width, height=height))
        elif get_window_method == 'title':
            title = flow_node.input('title')
            use_class_name = flow_node.input('useClassName')
            if use_class_name:
                return (
                    gettext(
                        'Set the width of window with the title ##{title}## and type ##{className}## to ##{width}## and the height to ##{height}##')
                    .format(title=title, className=flow_node.input('className'), width=width, height=height))
            else:
                return (
                    gettext(
                        'Set the width of window with the title ##{title}## to ##{width}## and the height to ##{height}##')
                    .format(title=title, width=width, height=height))
        else:
            return (
                gettext(
                    'Set the width of window of ##{element}## to ##{width}## and the height to ##{height}##')
                .format(element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                        width=width, height=height))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_window_for_component, move_window

        window_object = get_window_for_component(self)
        window_size = self.read_input('windowSize')
        width = int(self.evaluate_expression_in_process(window_size[0]))
        height = int(self.evaluate_expression_in_process(window_size[1]))
        move_window(window_object, width=width, height=height)
        return ControlFlow.NEXT
