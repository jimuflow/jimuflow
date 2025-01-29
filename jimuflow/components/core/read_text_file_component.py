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

from jimuflow.components.core.os_utils import get_file_encoding_title
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ReadTextFileComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Read ##{filePath}## using encoding ##{fileEncoding}##, and save the result to ##{result}##').format(
            filePath=flow_node.input('filePath'),
            fileEncoding=get_file_encoding_title(flow_node.input('fileEncoding')),
            result=flow_node.output('result')
        )

    async def execute(self) -> ControlFlow:
        file_path: str = self.read_input('filePath')
        file_encoding = self.read_input('fileEncoding')
        with open(file_path, 'r', encoding=file_encoding if file_encoding != 'system_default' else None) as f:
            read_type = self.read_input('readType')
            if read_type == 'whole':
                result = f.read()
            else:
                result = f.readlines()
        await self.write_output('result', result)
        return ControlFlow.NEXT
