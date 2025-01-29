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
import tempfile
import zipfile

import pytest

from jimuflow.components.core import CompressFileComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_compress_file_to_same_folder():
    component = create_component(CompressFileComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_name = os.path.join(temp_dir, 'file.txt')
        with open(temp_file_name, 'w') as f:
            f.write('123')
        zip_file_name = 'file'
        expected = os.path.join(temp_dir, f'{zip_file_name}.zip')
        await component.process.update_variable('f1', temp_file_name)
        await component.process.update_variable('f2', zip_file_name)
        component.node.inputs = {
            "filePath": 'f1',
            "packageName": 'f2',
            "saveFolderType": 'source'
        }
        component.node.outputs = {
            "packagePath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == expected
        assert os.path.exists(expected)
        assert os.path.exists(temp_file_name)
        extract_to_path = os.path.join(temp_dir, 'extracted')
        with zipfile.ZipFile(expected, 'r') as zip_ref:
            # 解压所有文件到指定目录
            zip_ref.extractall(extract_to_path)
        extracted_file_path = os.path.join(extract_to_path, 'file.txt')
        assert os.path.exists(extracted_file_path)
        assert open(extracted_file_path, 'r').read() == '123'


@pytest.mark.asyncio
async def test_compress_file_to_same_folder_conflict():
    component = create_component(CompressFileComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_name = os.path.join(temp_dir, 'file.txt')
        with open(temp_file_name, 'w') as f:
            f.write('123')
        zip_file_name = 'file'
        expected = os.path.join(temp_dir, f'{zip_file_name}.zip')
        with open(expected, 'w') as f:
            f.write('456')
        await component.process.update_variable('f1', temp_file_name)
        await component.process.update_variable('f2', zip_file_name)
        component.node.inputs = {
            "filePath": 'f1',
            "packageName": 'f2',
            "saveFolderType": 'source'
        }
        component.node.outputs = {
            "packagePath": 'r'
        }
        with pytest.raises(Exception):
            assert (await component.execute()) == ControlFlow.NEXT


@pytest.mark.asyncio
async def test_compress_folder_to_same_folder():
    component = create_component(CompressFileComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = os.path.join(temp_dir, 'folder')
        os.mkdir(folder)
        temp_file_name1 = os.path.join(folder, 'file1.txt')
        with open(temp_file_name1, 'w') as f:
            f.write('123')
        temp_file_name2 = os.path.join(folder, 'file2.txt')
        with open(temp_file_name2, 'w') as f:
            f.write('456')
        zip_file_name = 'folder'
        expected = os.path.join(temp_dir, f'{zip_file_name}.zip')
        await component.process.update_variable('f1', folder)
        await component.process.update_variable('f2', zip_file_name)
        component.node.inputs = {
            "filePath": 'f1',
            "packageName": 'f2',
            "saveFolderType": 'source'
        }
        component.node.outputs = {
            "packagePath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == expected
        assert os.path.exists(expected)
        assert os.path.exists(temp_file_name1)
        assert os.path.exists(temp_file_name2)
        extract_to_path = os.path.join(temp_dir, 'extracted')
        with zipfile.ZipFile(expected, 'r') as zip_ref:
            # 解压所有文件到指定目录
            zip_ref.extractall(extract_to_path)
        extracted_file1_path = os.path.join(extract_to_path, os.path.basename(folder), 'file1.txt')
        assert os.path.exists(extracted_file1_path)
        assert open(extracted_file1_path, 'r').read() == '123'
        extracted_file2_path = os.path.join(extract_to_path, os.path.basename(folder), 'file2.txt')
        assert os.path.exists(extracted_file2_path)
        assert open(extracted_file2_path, 'r').read() == '456'


@pytest.mark.asyncio
async def test_compress_file_to_specified_folder():
    component = create_component(CompressFileComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_name = os.path.join(temp_dir, 'file.txt')
        with open(temp_file_name, 'w') as f:
            f.write('123')
        zip_file_name = 'file'
        expected = os.path.join(temp_dir, 'dest', f'{zip_file_name}.zip')
        await component.process.update_variable('f1', temp_file_name)
        await component.process.update_variable('f2', zip_file_name)
        await component.process.update_variable('f3', os.path.dirname(expected))
        component.node.inputs = {
            "filePath": 'f1',
            "packageName": 'f2',
            "saveFolder": 'f3',
            "saveFolderType": 'specified'
        }
        component.node.outputs = {
            "packagePath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == expected
        assert os.path.exists(expected)
        assert os.path.exists(temp_file_name)
        extract_to_path = os.path.join(temp_dir, 'extracted')
        with zipfile.ZipFile(expected, 'r') as zip_ref:
            # 解压所有文件到指定目录
            zip_ref.extractall(extract_to_path)
        extracted_file_path = os.path.join(extract_to_path, 'file.txt')
        assert os.path.exists(extracted_file_path)
        assert open(extracted_file_path, 'r').read() == '123'


@pytest.mark.asyncio
async def test_compress_file_to_specified_folder_conflict():
    component = create_component(CompressFileComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_name = os.path.join(temp_dir, 'file.txt')
        with open(temp_file_name, 'w') as f:
            f.write('123')
        zip_file_name = 'file'
        expected = os.path.join(temp_dir, 'dest', f'{zip_file_name}.zip')
        os.mkdir(os.path.dirname(expected))
        with open(expected, 'w') as f:
            f.write('456')
        await component.process.update_variable('f1', temp_file_name)
        await component.process.update_variable('f2', zip_file_name)
        await component.process.update_variable('f3', os.path.dirname(expected))
        component.node.inputs = {
            "filePath": 'f1',
            "packageName": 'f2',
            "saveFolder": 'f3',
            "saveFolderType": 'specified'
        }
        component.node.outputs = {
            "packagePath": 'r'
        }
        with pytest.raises(Exception):
            assert (await component.execute()) == ControlFlow.NEXT
