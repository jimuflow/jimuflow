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

from jimuflow.components.core.condition_utils import op_i18n, evaluate_condition, is_binary_op
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class WhileComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        if is_binary_op(flow_node.input('op')):
            return gettext('If ##{operand1}## ##{op}## ##{operand2}##, perform the following actions').format(
                operand1=flow_node.input('operand1'),
                op=op_i18n[flow_node.input('op')],
                operand2=flow_node.input('operand2'))
        else:
            return gettext('If ##{operand1}## ##{op}##, perform the following actions').format(
                operand1=flow_node.input('operand1'),
                op=op_i18n[flow_node.input('op')])

    async def execute(self) -> ControlFlow:
        while True:
            operand1 = self.read_input('operand1')
            op = self.read_input('op')
            operand2 = self.read_input('operand2')
            matched = evaluate_condition(operand1, op, operand2)
            self.log_debug(gettext('Condition matched: {matched}'), matched=matched)
            if matched:
                control_flow = await self.execute_flow()
                if control_flow == ControlFlow.BREAK:
                    break
                elif control_flow == ControlFlow.RETURN or control_flow == ControlFlow.EXIT:
                    return control_flow
            else:
                break
        return ControlFlow.NEXT
