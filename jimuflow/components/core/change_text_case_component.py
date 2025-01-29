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

change_types = {
    'upper': gettext('uppercase'),
    'lower': gettext('lowercase'),
    'capitalize': gettext('capitalized')
}


class ChangeTextCaseComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        original_text: str = flow_node.input('originalText')
        change_type = flow_node.input('changeType')
        return gettext('Convert ##{original_text}## to ##{change_type}##, and save the result to ##{result}##').format(
            original_text=original_text, change_type=change_types[change_type], result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        original_text: str = self.read_input('originalText')
        if original_text is None or original_text == '':
            result = original_text
        else:
            change_type = self.read_input('changeType')
            if change_type == 'upper':
                result = original_text.upper()
            elif change_type == 'lower':
                result = original_text.lower()
            elif change_type == 'capitalize':
                result = original_text.capitalize()
            else:
                raise Exception(gettext('Unknown case change type: {change_type}').format(change_type=change_type))
        await self.write_output('result', result)
        return ControlFlow.NEXT
