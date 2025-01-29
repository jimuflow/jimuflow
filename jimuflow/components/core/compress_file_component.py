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
import zipfile
from pathlib import Path

from jimuflow.definition import FlowNode
from jimuflow.locales.i18n import gettext
from jimuflow.runtime.execution_engine import PrimitiveComponent, ControlFlow


class CompressFileComponent(PrimitiveComponent):

    @classmethod
    def display_description(cls, flow_node: FlowNode):
        return gettext(
            'Compress ##{filePath}## to ##{packageName}##, and save the compressed package path to ##{packagePath}##').format(
            filePath=flow_node.input('filePath'),
            packageName=flow_node.input('packageName'),
            packagePath=flow_node.output('packagePath')
        )

    async def execute(self) -> ControlFlow:
        file_path: str = self.read_input('filePath')
        package_name = self.read_input('packageName')
        save_folder_type = self.read_input('saveFolderType')
        if save_folder_type == 'source':
            package_path = Path(file_path).parent / f'{package_name}.zip'
        else:
            save_folder = self.read_input('saveFolder')
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)
            package_path = Path(save_folder) / f'{package_name}.zip'
        if os.path.exists(package_path):
            raise Exception(gettext('File {file} already exists').format(file=package_path))
        CompressFileComponent.zip_file_or_directory(file_path, package_path)
        await self.write_output('packagePath', str(package_path))
        return ControlFlow.NEXT

    @staticmethod
    def zip_file_or_directory(source_path, zip_path):
        # 创建一个zip文件对象
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 如果是文件
            if os.path.isfile(source_path):
                zip_file.write(source_path, os.path.basename(source_path))
            # 如果是目录
            elif os.path.isdir(source_path):
                for root, dirs, files in os.walk(source_path):
                    for file in files:
                        # 将文件压缩到zip包中，并保留相对路径
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.join(source_path, '..'))
                        zip_file.write(file_path, arcname)
            else:
                raise ValueError(
                    gettext("{source_path} is not a valid file or directory.").format(source_path=source_path))
