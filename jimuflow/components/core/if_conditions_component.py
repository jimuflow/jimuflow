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

from jimuflow.components.core.condition_utils import is_binary_op, evaluate_condition
from jimuflow.components.core.if_component import op_i18n
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class IfConditionsComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        conditions = flow_node.input('conditions')
        conditions_descriptions = []
        for condition in conditions:
            if is_binary_op(condition['op']):
                conditions_descriptions.append(gettext('##{operand1}## ##{op}## ##{operand2}##').format(
                    operand1=condition['operand1'],
                    op=op_i18n[condition['op']],
                    operand2=condition['operand2']))
            else:
                conditions_descriptions.append(gettext('##{operand1}## ##{op}##').format(
                    operand1=condition['operand1'],
                    op=op_i18n[condition['op']]))
        relation = flow_node.input('relation')
        if relation == 'all':
            return gettext('If satisfy all conditions of [{conditions}], perform the following actions').format(
                conditions=', '.join(conditions_descriptions))
        else:
            return gettext('If satisfy any condition of [{conditions}], perform the following actions').format(
                conditions=', '.join(conditions_descriptions))

    async def execute(self) -> ControlFlow:
        relation = self.read_input('relation')
        conditions = self.read_input('conditions')
        result = True if relation == 'all' else False
        for condition in conditions:
            operand1 = self.evaluate_expression_in_process(condition['operand1'])
            op = condition['op']
            operand2 = self.evaluate_expression_in_process(condition['operand2']) if is_binary_op(op) else None
            matched = evaluate_condition(operand1, op, operand2)
            if relation == 'all' and not matched:
                result = False
                break
            elif relation == 'any' and matched:
                result = True
                break
        self.log_debug(gettext('Condition matched: {matched}'), matched=result)
        if result:
            control_flow = await self.execute_flow()
            return ControlFlow.SKIP_ELSE_IF if control_flow == ControlFlow.NEXT else control_flow
        return ControlFlow.NEXT
