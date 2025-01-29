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


class NumberToTextComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        use_thousands_separator = flow_node.input('useThousandsSeparator')
        if use_thousands_separator:
            return gettext(
                'Convert ##{value}## to a string, retain ##{scale}## decimal places, add a thousand separator, and save the result to ##{result}##').format(
                value=flow_node.input('value'), scale=flow_node.input('scale'), result=flow_node.output('result'))
        else:
            return gettext(
                'Convert ##{value}## to a string, retain ##{scale}## decimal places, and save the result to ##{result}##').format(
                value=flow_node.input('value'), scale=flow_node.input('scale'), result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        value: int | float = self.read_input('value')
        if value is None:
            result = None
        else:
            scale = int(self.read_input('scale'))
            use_thousands_separator = self.read_input('useThousandsSeparator')
            # 对数值进行格式化，保留小数点后2位，并添加千位分隔符
            result = f"{{:{',' if use_thousands_separator else ''}.{scale}f}}".format(value)
        await self.write_output('result', result)
        return ControlFlow.NEXT
