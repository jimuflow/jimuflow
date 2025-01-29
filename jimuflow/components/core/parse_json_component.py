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

import json

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ParseJsonComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Parse json text ##{jsonText}##, and save the result to ##{result}##').format(
            jsonText=flow_node.input('jsonText'),
            result=flow_node.output('result')
        )

    async def execute(self) -> ControlFlow:
        json_text: str = self.read_input('jsonText')
        if json_text is None:
            result = None
        else:
            result = json.loads(json_text)
        await self.write_output('result', result)
        return ControlFlow.NEXT
