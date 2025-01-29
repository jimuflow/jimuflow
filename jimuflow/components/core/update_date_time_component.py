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

from dateutil.relativedelta import relativedelta

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class UpdateDateTimeComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Update ##{originalDateTime}##, {adjustmentType} ##{adjustmentValue}## ##{adjustmentUnit}##, and save the result to ##{result}##').format(
            originalDateTime=flow_node.input('originalDateTime'),
            adjustmentType=gettext('increment') if flow_node.input('adjustmentType') == 'increment' else gettext(
                'decrement'),
            adjustmentValue=flow_node.input('adjustmentValue'),
            adjustmentUnit={'microseconds': gettext('microseconds'), 'milliseconds': gettext('milliseconds'),
                            'seconds': gettext('seconds'), 'minutes': gettext('minutes'), 'hours': gettext('hours'),
                            'days': gettext('days'), 'weeks': gettext('weeks'), 'months': gettext('months'),
                            'years': gettext('years')}[flow_node.input('adjustmentUnit')],
            result=flow_node.output('result')
        )

    async def execute(self) -> ControlFlow:
        original_datetime: datetime.datetime = self.read_input('originalDateTime')
        adjustment_type = self.read_input('adjustmentType')
        adjustment_value = int(self.read_input('adjustmentValue'))
        if adjustment_type == 'decrement':
            adjustment_value = -adjustment_value
        adjustment_unit = self.read_input('adjustmentUnit')
        if adjustment_unit == 'microseconds':
            value = original_datetime + datetime.timedelta(microseconds=adjustment_value)
        elif adjustment_unit == 'milliseconds':
            value = original_datetime + datetime.timedelta(milliseconds=adjustment_value)
        elif adjustment_unit == 'seconds':
            value = original_datetime + datetime.timedelta(seconds=adjustment_value)
        elif adjustment_unit == 'minutes':
            value = original_datetime + datetime.timedelta(minutes=adjustment_value)
        elif adjustment_unit == 'hours':
            value = original_datetime + datetime.timedelta(hours=adjustment_value)
        elif adjustment_unit == 'days':
            value = original_datetime + datetime.timedelta(days=adjustment_value)
        elif adjustment_unit == 'weeks':
            value = original_datetime + datetime.timedelta(weeks=adjustment_value)
        elif adjustment_unit == 'months':
            value = original_datetime + relativedelta(months=adjustment_value)
        elif adjustment_unit == 'years':
            value = original_datetime + relativedelta(years=adjustment_value)
        else:
            raise ValueError(gettext('Unknown adjustment unit: {unit}').format(unit=adjustment_unit))
        await self.write_output('result', value)
        return ControlFlow.NEXT
