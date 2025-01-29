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

import os

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class CreateFolderComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Create folder ##{newFolderName}## under ##{parentFolder}##, and save the new folder path to ##{newFolderPath}##').format(
            newFolderName=flow_node.input('newFolderName'),
            parentFolder=flow_node.input('parentFolder'),
            newFolderPath=flow_node.output('newFolderPath')
        )

    async def execute(self) -> ControlFlow:
        parent_folder: str = self.read_input('parentFolder')
        new_folder_name = self.read_input('newFolderName')
        new_folder_path = os.path.join(parent_folder, new_folder_name)
        os.makedirs(new_folder_path, exist_ok=True)
        await self.write_output('newFolderPath', new_folder_path)
        return ControlFlow.NEXT
