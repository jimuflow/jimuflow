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

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class DiffDateTimeComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Calculate the ##{timeUnit}## interval from ##{startingDate}## to ##{endDate}##, and save the result to ##{timeDifference}##').format(
            timeUnit={'seconds': gettext('seconds'), 'minutes': gettext('minutes'), 'hours': gettext('hours'),
                      'days': gettext('days')}[flow_node.input('timeUnit')],
            startingDate=flow_node.input('startingDate'),
            endDate=flow_node.input('endDate'),
            timeDifference=flow_node.output('timeDifference')
        )

    async def execute(self) -> ControlFlow:
        starting_datetime: datetime.datetime = self.read_input('startingDate')
        end_datetime: datetime.datetime = self.read_input('endDate')
        time_unit = self.read_input('timeUnit')
        if time_unit == 'seconds':
            value = int((end_datetime - starting_datetime).total_seconds())
        elif time_unit == 'minutes':
            value = int((end_datetime - starting_datetime).total_seconds() / 60)
        elif time_unit == 'hours':
            value = int((end_datetime - starting_datetime).total_seconds() / 3600)
        elif time_unit == 'days':
            value = int((end_datetime - starting_datetime).total_seconds() / 86400)
        else:
            raise ValueError(gettext('Unknown time unit: {unit}').format(unit=time_unit))
        await self.write_output('timeDifference', value)
        return ControlFlow.NEXT
