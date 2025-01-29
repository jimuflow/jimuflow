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

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class DictLoopComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Loop through each item in the dictionary ##{dict}##, saving the current item to ##{loopItem}##').format(
            dict=flow_node.input('dict'), loopItem=flow_node.output('loopItem'))

    async def execute(self) -> ControlFlow:
        items: dict = self.read_input('dict')
        for item in items.items():
            await self.write_output('loopItem', item)
            control_flow = await self.execute_flow()
            if control_flow == ControlFlow.BREAK:
                break
            elif control_flow == ControlFlow.RETURN or control_flow == ControlFlow.EXIT:
                return control_flow
        return ControlFlow.NEXT
