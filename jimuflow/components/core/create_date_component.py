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


class CreateDateComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        init_type = flow_node.input('initType')
        if init_type == 'today':
            return gettext('Create Date today, and save the result to ##{result}##').format(
                result=flow_node.output('result'))
        elif init_type == 'timestamp':
            timestamp = flow_node.input('timestamp')
            return gettext('Create Date from timestamp ##{timestamp}##, and save the result to ##{result}##').format(
                timestamp=timestamp, result=flow_node.output('result'))
        else:
            date_string = flow_node.input('dateString')
            date_format = flow_node.input('dateFormat')
            return gettext(
                'Create Date from string ##{date_string}## with format ##{date_format}##, and save the result to ##{result}##').format(
                date_string=date_string, date_format=date_format, result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        init_type = self.read_input('initType')
        if init_type == 'today':
            value = datetime.date.today()
        elif init_type == 'timestamp':
            timestamp = float(self.read_input('timestamp'))
            value = datetime.date.fromtimestamp(timestamp)
        else:
            date_string = self.read_input('dateString')
            date_format = self.read_input('dateFormat')
            value = custom_arrow.get(date_string, date_format).date()
        await self.write_output('result', value)
        return ControlFlow.NEXT
