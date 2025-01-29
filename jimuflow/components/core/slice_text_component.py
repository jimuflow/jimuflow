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


class SliceTextComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        from_where = flow_node.input('fromWhere')
        if from_where == 'first_char':
            from_description = gettext('from the first character')
        elif from_where == 'specified_position':
            from_description = gettext('from the specified location ##{startingPosition}##').format(
                startingPosition=flow_node.input('startingPosition'))
        else:
            from_description = gettext(
                'from the specified text ##{startingText}##').format(startingText=flow_node.input('startingText'))
        to_where = flow_node.input('toWhere')
        if to_where == 'end':
            to_description = gettext('to the end of the text')
        else:
            to_description = gettext(
                'to the specified length ##{slicedLength}##'.format(slicedLength=flow_node.input('slicedLength')))
        return gettext(
            'Slice ##{originalText}## {from_description} {to_description}, and save the result to ##{result}##').format(
            originalText=flow_node.input('originalText'), from_description=from_description,
            to_description=to_description, result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        original_text: str = self.read_input('originalText')
        if original_text is None or original_text == '':
            result = original_text
        else:
            from_where = self.read_input('fromWhere')
            if from_where == 'first_char':
                start = 0
            elif from_where == 'specified_position':
                start = int(self.read_input('startingPosition'))
            else:
                start = original_text.find(self.read_input('startingText'))
                if start == -1:
                    start = len(original_text)
            to_where = self.read_input('toWhere')
            if to_where == 'end':
                end = len(original_text)
            else:
                end = start + int(self.read_input('slicedLength'))
            result = original_text[start:end]
        await self.write_output('result', result)
        return ControlFlow.NEXT
