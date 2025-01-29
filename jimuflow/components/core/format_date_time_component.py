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


class FormatDateTimeComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Format ##{datetime}## to a string using format ##{datetimeFormat}##, and save the result to ##{result}##').format(
            datetime=flow_node.input('datetime'),
            datetimeFormat=flow_node.input('datetimeFormat'),
            result=flow_node.output('result')
        )

    async def execute(self) -> ControlFlow:
        dt: datetime.datetime = self.read_input('datetime')
        fmt_str: str = self.read_input('datetimeFormat')
        result = custom_arrow.get(dt).format(fmt_str)
        await self.write_output('result', result)
        return ControlFlow.NEXT
