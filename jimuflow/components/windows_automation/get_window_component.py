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


class GetWindowComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        get_window_method = flow_node.input('getWindowMethod')
        if get_window_method == 'current_active':
            return gettext('Get the current active window, and save to ##{windowObject}##').format(
                windowObject=flow_node.output('windowObject'))
        elif get_window_method == 'title':
            title = flow_node.input('title')
            use_class_name = flow_node.input('useClassName')
            if use_class_name:
                return gettext(
                    'Get the window with the title ##{title}## and type ##{className}##, and save to ##{windowObject}##').format(
                    title=title, className=flow_node.input('className'), windowObject=flow_node.output('windowObject'))
            else:
                return gettext('Get the window with the title ##{title}##, and save to ##{windowObject}##').format(
                    title=title, windowObject=flow_node.output('windowObject'))
        else:
            return gettext('Get the window of ##{element}##, and save to ##{windowObject}##').format(
                element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                windowObject=flow_node.output('windowObject'))

    async def execute(self) -> ControlFlow:
        import pywinauto
        from jimuflow.components.windows_automation.pywinauto_utill import get_element_by_uri, timeout_context_manager
        get_window_method = self.read_input('getWindowMethod')
        wait_time = float(self.read_input("waitTime"))
        if get_window_method == 'current_active':
            with timeout_context_manager(wait_time):
                window_object = pywinauto.Desktop(backend="uia").window(active_only=True).wrapper_object()
        elif get_window_method == 'title':
            title = self.read_input('title')
            kwargs = {}
            use_regex_matching = self.read_input('useRegexMatching')
            if use_regex_matching:
                kwargs['title_re'] = title
            else:
                kwargs['title'] = title
            use_class_name = self.read_input('useClassName')
            if use_class_name:
                kwargs['class_name'] = self.read_input('className')
            with timeout_context_manager(wait_time):
                window_object = pywinauto.Desktop(backend="uia").window(**kwargs).wrapper_object()
        else:
            element_uri = self.read_input("elementUri")
            control_object = get_element_by_uri(self, element_uri, wait_time)
            window_object = control_object.top_level_parent()

        await self.write_output('windowObject', window_object)
        return ControlFlow.NEXT
