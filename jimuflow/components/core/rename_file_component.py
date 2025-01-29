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

import shutil
from pathlib import Path

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class RenameFileComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        action_when_exists = flow_node.input('actionWhenExists')
        if action_when_exists == 'cancel':
            action_when_exists_desc = gettext('and cancel renaming if the new file exists')
        else:
            action_when_exists_desc = gettext('and overwrite the existing file if the new file exists')
        return gettext(
            'Rename ##{filePath}## to ##{newFilename}##, {action_when_exists_desc}, and save the new file path to ##{newFilePath}##').format(
            filePath=flow_node.input('filePath'),
            newFilename=flow_node.input('newFilename'),
            action_when_exists_desc=action_when_exists_desc,
            newFilePath=flow_node.output('newFilePath')
        )

    async def execute(self) -> ControlFlow:
        file_path: str = self.read_input('filePath')
        new_filename = self.read_input('newFilename')
        new_file_path = Path(file_path).parent / new_filename
        action_when_exists = self.read_input('actionWhenExists')
        if new_file_path.exists() and action_when_exists == 'cancel':
            self.log_info(gettext('File {file_path} already exists, cancel renaming'), file_path=file_path)
            return ControlFlow.NEXT
        shutil.move(file_path, new_file_path)
        await self.write_output('newFilePath', str(new_file_path))
        return ControlFlow.NEXT
