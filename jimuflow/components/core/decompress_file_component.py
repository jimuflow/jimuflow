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

import zipfile
from pathlib import Path

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class DecompressFileComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Decompress ##{filePath}##, and save the result folder to ##{result}##').format(
            filePath=flow_node.input('filePath'),
            result=flow_node.output('result')
        )

    async def execute(self) -> ControlFlow:
        file_path: str = self.read_input('filePath')
        decompress_to = self.read_input('decompressTo')
        if decompress_to == 'source':
            save_folder = Path(file_path).parent
        else:
            save_folder = Path(self.read_input('saveFolder'))
            if not save_folder.exists():
                save_folder.mkdir(parents=True)
        create_folder = self.read_input('createFolder')
        if create_folder:
            dest_folder = save_folder / Path(file_path).stem
            if not dest_folder.exists():
                dest_folder.mkdir()
        else:
            dest_folder = save_folder
        password: str = self.read_input('password')
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(dest_folder, pwd=password.encode() if password else None)
        await self.write_output('result', str(dest_folder))
        return ControlFlow.NEXT
