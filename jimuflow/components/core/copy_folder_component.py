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

from jimuflow.common.fs import copy_folder_overwrite
from jimuflow.components.core.os_utils import rename_file_if_exists
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow

actions_when_exists = {
    'overwrite': gettext('overwrite existing folder'),
    'rename': gettext('automatically rename folder when target folder exist'),
    'error': gettext('execute error handling when target folder exists')
}


class CopyFolderComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Copy ##{folderPath}## to ##{targetFolder}##, {actionWhenExists}, and save the new folder path to ##{newFolderPath}##').format(
            folderPath=flow_node.input('folderPath'),
            targetFolder=flow_node.input('targetFolder'),
            actionWhenExists=actions_when_exists[flow_node.input('actionWhenExists')],
            newFolderPath=flow_node.output('newFolderPath')
        )

    async def execute(self) -> ControlFlow:
        folder_path: str = self.read_input('folderPath')
        target_folder = self.read_input('targetFolder')
        action_when_exists = self.read_input('actionWhenExists')
        new_folder_path = os.path.join(target_folder, os.path.basename(folder_path))
        if os.path.exists(new_folder_path):
            if action_when_exists == 'rename':
                new_folder_path = rename_file_if_exists(new_folder_path)
                shutil.copytree(folder_path, new_folder_path)
            elif action_when_exists == 'error':
                raise Exception(gettext('Folder {file_path} already exists').format(file_path=new_folder_path))
            else:
                copy_folder_overwrite(folder_path, new_folder_path)
        else:
            os.makedirs(target_folder, exist_ok=True)
            shutil.copytree(folder_path, new_folder_path)
        await self.write_output('newFolderPath', new_folder_path)
        return ControlFlow.NEXT
