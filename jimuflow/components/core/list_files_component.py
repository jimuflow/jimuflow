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

from pathlib import Path

from jimuflow.components.core.os_utils import is_hidden
from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class ListFilesComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Find files under ##{folder}## that match the ##{filenamePattern}## naming rule and save the results in ##{result}##').format(
            folder=flow_node.input('folder'),
            filenamePattern=flow_node.input('filenamePattern'),
            result=flow_node.output('result')
        )

    async def execute(self) -> ControlFlow:
        folder: str = self.read_input('folder')
        filename_pattern = self.read_input('filenamePattern')
        find_sub_folders = self.read_input('findSubFolders')
        if find_sub_folders:
            files = Path(folder).rglob(filename_pattern)
        else:
            files = Path(folder).glob(filename_pattern)
        ignore_hidden_files = self.read_input('ignoreHiddenFiles')
        if ignore_hidden_files:
            files = [f for f in files if f.is_file() and not is_hidden(f)]
        else:
            files = [f for f in files if f.is_file()]
        sorting_files = self.read_input('sortingFiles')
        if sorting_files:
            sorting_factor = self.read_input('sortingFactor')
            sort_order = self.read_input('sortOrder')
            if sorting_factor == 'name':
                files = sorted(files, key=lambda f: f.name, reverse=sort_order == 'desc')
            elif sorting_factor == 'size':
                files = sorted(files, key=lambda f: f.stat().st_size, reverse=sort_order == 'desc')
            elif sorting_factor == 'creationTime':
                files = sorted(files, key=lambda f: f.stat().st_ctime, reverse=sort_order == 'desc')
            else:
                files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=sort_order == 'desc')
        files = [str(f) for f in files]
        await self.write_output('result', files)
        return ControlFlow.NEXT
