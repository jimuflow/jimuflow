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


class SetWindowStateComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        get_window_method = flow_node.input('getWindowMethod')
        window_state = flow_node.input('windowState')
        if get_window_method == 'window_object':
            if window_state == 'restore':
                return gettext('Restore the window ##{windowObject}##').format(
                    windowObject=flow_node.input('windowObject'))
            elif window_state == 'maximize':
                return gettext('Maximize the window ##{windowObject}##').format(
                    windowObject=flow_node.input('windowObject'))
            else:
                return gettext('Minimize the window ##{windowObject}##').format(
                    windowObject=flow_node.input('windowObject'))
        elif get_window_method == 'title':
            title = flow_node.input('title')
            use_class_name = flow_node.input('useClassName')
            if use_class_name:
                if window_state == 'restore':
                    return gettext(
                        'Restore the window with the title ##{title}## and type ##{className}##').format(
                        title=title, className=flow_node.input('className'))
                elif window_state == 'maximize':
                    return gettext(
                        'Maximize the window with the title ##{title}## and type ##{className}##').format(
                        title=title, className=flow_node.input('className'))
                else:
                    return gettext(
                        'Minimize the window with the title ##{title}## and type ##{className}##').format(
                        title=title, className=flow_node.input('className'))
            else:
                if window_state == 'restore':
                    return gettext('Restore the window with the title ##{title}##').format(title=title)
                elif window_state == 'maximize':
                    return gettext('Maximize the window with the title ##{title}##').format(title=title)
                else:
                    return gettext('Minimize the window with the title ##{title}##').format(title=title)
        else:
            if window_state == 'restore':
                return gettext('Restore the window of ##{element}##').format(
                    element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')))
            elif window_state == 'maximize':
                return gettext('Maximize the window of ##{element}##').format(
                    element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')))
            else:
                return gettext('Minimize the window of ##{element}##').format(
                    element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_window_for_component

        window_object = get_window_for_component(self)
        window_state = self.read_input('windowState')
        if window_state == 'restore':
            window_object.restore()
        elif window_state == 'maximize':
            window_object.maximize()
        else:
            window_object.minimize()
        return ControlFlow.NEXT
