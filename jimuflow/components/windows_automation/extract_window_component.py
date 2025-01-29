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

import psutil

from jimuflow.common.uri_utils import describe_element_uri
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ExtractWindowComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        get_window_method = flow_node.input('getWindowMethod')
        extract_type = flow_node.input('extractType')
        if extract_type == 'title':
            extract_data = gettext('title')
        else:
            extract_data = gettext('process name')
        result = flow_node.output('result')
        if get_window_method == 'window_object':
            return (gettext('Extract the ##{extractData}## of the window ##{windowObject}##, and save to ##{result}##')
                    .format(windowObject=flow_node.input('windowObject'), extractData=extract_data, result=result))
        elif get_window_method == 'title':
            title = flow_node.input('title')
            use_class_name = flow_node.input('useClassName')
            if use_class_name:
                return (
                    gettext(
                        'Extract the ##{extractData}## of the window with the title ##{title}##, and save to ##{result}##')
                    .format(title=title, className=flow_node.input('className'), extractData=extract_data,
                            result=result))
            else:
                return (
                    gettext(
                        'Extract the ##{extractData}## of the window with the title ##{title}##, and save to ##{result}##')
                    .format(title=title, extractData=extract_data, result=result))
        else:
            return (
                gettext(
                    'Extract the ##{extractData}## of the window of ##{element}##, and save to ##{result}##')
                .format(element=describe_element_uri(flow_node.process_def.package, flow_node.input('elementUri')),
                        extractData=extract_data, result=result))

    async def execute(self) -> ControlFlow:
        from jimuflow.components.windows_automation.pywinauto_utill import get_window_for_component

        window_object = get_window_for_component(self)
        extract_type = self.read_input('extractType')
        if extract_type == 'title':
            result = window_object.window_text()
        else:
            pid = window_object.process_id()
            process_name = psutil.Process(pid).name()
            if process_name.lower().endswith(".exe"):
                process_name = process_name[:-4]
            result = process_name
        await self.write_output('result', result)
        return ControlFlow.NEXT
