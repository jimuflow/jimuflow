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

from jimuflow.datatypes import FilePathInfo
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class GetFilePathInfoComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Get file path info of ##{filePath}##, and save the result to ##{filePathInfo}##').format(
            filePath=flow_node.input('filePath'),
            filePathInfo=flow_node.output('filePathInfo')
        )

    async def execute(self) -> ControlFlow:
        file_path: str = self.read_input('filePath')
        file_path_info = FilePathInfo(file_path)
        await self.write_output('filePathInfo', file_path_info)
        return ControlFlow.NEXT
