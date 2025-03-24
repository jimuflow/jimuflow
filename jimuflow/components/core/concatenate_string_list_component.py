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


class ConcatenateStringListComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext('Concatenate string list ##{stringList}## with delimiter ##{delimiter}##, saving result to ##{result}##').format(
            stringList=flow_node.input('stringList'), delimiter=flow_node.input('delimiter'),
            result=flow_node.output('result'))

    async def execute(self) -> ControlFlow:
        string_list = self.read_input('stringList')
        delimiter = self.read_input('delimiter')
        ignore_empty_item = self.read_input('ignoreEmptyItem')
        
        # 当 string_list 为 None 时，返回空字符串
        if string_list is None:
            await self.write_output('result', '')
            return ControlFlow.NEXT

        if delimiter is None:
            delimiter = ''
        
        # Convert all elements to string to ensure they can be joined
        string_list = [str(item) for item in string_list if not ignore_empty_item or item != '' and item is not None]
        
        # Join the list elements with the specified delimiter
        result = delimiter.join(string_list)
        
        await self.write_output('result', result)
        return ControlFlow.NEXT
