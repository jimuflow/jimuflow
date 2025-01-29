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

import datetime

from jimuflow.components.core.datetime_utils import custom_arrow
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class CreateTimeComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        init_type = flow_node.input('initType')
        if init_type == 'now':
            return gettext('Create Time now, and save the result to ##{result}##').format(
                result=flow_node.output('result'))
        else:
            time_string = flow_node.input('timeString')
            time_format = flow_node.input('timeFormat')
            return gettext(
                'Create Time from string ##{time_string}## with format ##{time_format}##, and save the result to ##{result}##').format(
                time_string=time_string, time_format=time_format, result=flow_node.output)

    async def execute(self) -> ControlFlow:
        init_type = self.read_input('initType')
        if init_type == 'now':
            value = datetime.datetime.now().time()
        else:
            time_string = self.read_input('timeString')
            time_format = self.read_input('timeFormat')
            value = custom_arrow.get(time_string, time_format).time()
        await self.write_output('result', value)
        return ControlFlow.NEXT
