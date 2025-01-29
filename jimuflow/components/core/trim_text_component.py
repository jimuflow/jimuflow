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


class TrimTextComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        trim_type = flow_node.input('trimType')
        if trim_type == 'both':
            return gettext(
                'Remove blank characters on both sides of ##{originalText}##, and save the result to ##{result}##').format(
                originalText=flow_node.input('originalText'), result=flow_node.output('result'))
        elif trim_type == 'left':
            return gettext(
                'Remove blank characters on the left side of ##{originalText}##, and save the result to ##{result}##').format(
                originalText=flow_node.input('originalText'), result=flow_node.output('result'))
        else:
            return gettext(
                'Remove blank characters on the right side of ##{originalText}##, and save the result to ##{result}##').format(
                originalText=flow_node.input('originalText'), result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        original_text: str = self.read_input('originalText')
        if original_text is None:
            result = None
        else:
            trim_type = self.read_input('trimType')
            if trim_type == 'both':
                result = original_text.strip()
            elif trim_type == 'left':
                result = original_text.lstrip()
            else:
                result = original_text.rstrip()
        await self.write_output('result', result)
        return ControlFlow.NEXT
