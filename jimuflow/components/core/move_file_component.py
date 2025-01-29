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
import shutil

from jimuflow.components.core.os_utils import rename_file_if_exists
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow

actions_when_exists = {
    'overwrite': gettext('overwrite existing files'),
    'rename': gettext('automatically rename file when target file exist'),
    'error': gettext('execute error handling when target file exists')
}


class MoveFileComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Move ##{filePath}## to ##{targetFolder}##, {actionWhenExists}, and save the new file path to ##{newFilePath}##').format(
            filePath=flow_node.input('filePath'),
            targetFolder=flow_node.input('targetFolder'),
            actionWhenExists=actions_when_exists[flow_node.input('actionWhenExists')],
            newFilePath=flow_node.output('newFilePath')
        )

    async def execute(self) -> ControlFlow:
        file_path: str = self.read_input('filePath')
        target_folder = self.read_input('targetFolder')
        action_when_exists = self.read_input('actionWhenExists')
        new_file_path = os.path.join(target_folder, os.path.basename(file_path))
        if os.path.exists(new_file_path):
            if action_when_exists == 'rename':
                new_file_path = rename_file_if_exists(new_file_path)
            elif action_when_exists == 'error':
                raise Exception(gettext('File {file_path} already exists').format(file_path=new_file_path))
        os.makedirs(target_folder, exist_ok=True)
        shutil.move(file_path, new_file_path)
        await self.write_output('newFilePath', new_file_path)
        return ControlFlow.NEXT
