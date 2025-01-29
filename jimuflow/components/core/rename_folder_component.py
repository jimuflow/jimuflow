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
from pathlib import Path

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class RenameFolderComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        action_when_exists = flow_node.input('actionWhenExists')
        if action_when_exists == 'cancel':
            action_when_exists_desc = gettext('and cancel renaming if the new folder exists')
        else:
            action_when_exists_desc = gettext('and overwrite the existing file if the new folder exists')
        return gettext(
            'Rename ##{folderPath}## to ##{newFolderName}##, {action_when_exists_desc}, and save the new folder path to ##{newFolderPath}##').format(
            folderPath=flow_node.input('folderPath'),
            newFolderName=flow_node.input('newFolderName'),
            action_when_exists_desc=action_when_exists_desc,
            newFolderPath=flow_node.output('newFolderPath')
        )

    async def execute(self) -> ControlFlow:
        folder_path: str = self.read_input('folderPath')
        new_folder_name = self.read_input('newFolderName')
        new_folder_path = Path(folder_path).parent / new_folder_name
        action_when_exists = self.read_input('actionWhenExists')
        if new_folder_path.exists() and action_when_exists == 'cancel':
            self.log_info(
                gettext('Folder {folder_path} already exists, cancel renaming'), folder_path=new_folder_path)
            return ControlFlow.NEXT
        if new_folder_path.exists():
            for item in os.listdir(folder_path):
                dest_path = new_folder_path / item
                if dest_path.exists():
                    if dest_path.is_file():
                        os.remove(dest_path)
                    else:
                        shutil.rmtree(dest_path)
                shutil.move(os.path.join(folder_path, item), new_folder_path)
            shutil.rmtree(folder_path)
        else:
            shutil.move(folder_path, new_folder_path)
        await self.write_output('newFolderPath', str(new_folder_path))
        return ControlFlow.NEXT
