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

import pytest

from jimuflow.components.core import MoveFolderComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component, random_string

file1_name = random_string(prefix='file_', suffix='.txt')
file1_content = random_string()


def create_sample_folder(temp_dir):
    folder = os.path.join(temp_dir, 'folder')
    os.mkdir(folder)
    with open(os.path.join(folder, file1_name), 'w') as f1:
        f1.write(file1_content)
    return folder


@pytest.mark.asyncio
async def test_not_conflict():
    component = create_component(MoveFolderComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = create_sample_folder(temp_dir)
        await component.process.update_variable('s', folder)
        dest_folder = os.path.join(temp_dir, 'dest_folder')
        await component.process.update_variable('d', dest_folder)
        component.node.inputs = {
            "folderPath": 's',
            "targetFolder": 'd',
            "actionWhenExists": "error"
        }
        component.node.outputs = {
            "newFolderPath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        expected = os.path.join(dest_folder, os.path.basename(folder))
        assert component.process.get_variable('r') == expected
        assert not os.path.exists(folder)
        assert os.path.exists(expected)
        dest_file1_path = os.path.join(expected, file1_name)
        assert os.path.exists(dest_file1_path)
        with open(dest_file1_path, 'r') as f1:
            assert f1.read() == file1_content


@pytest.mark.asyncio
async def test_conflict_overwrite():
    component = create_component(MoveFolderComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = create_sample_folder(temp_dir)
        await component.process.update_variable('s', folder)
        dest_folder = os.path.join(temp_dir, 'dest_folder')
        os.mkdir(dest_folder)
        expected = os.path.join(dest_folder, os.path.basename(folder))
        os.mkdir(expected)
        await component.process.update_variable('d', dest_folder)
        component.node.inputs = {
            "folderPath": 's',
            "targetFolder": 'd',
            "actionWhenExists": "override"
        }
        component.node.outputs = {
            "newFolderPath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == expected
        assert not os.path.exists(folder)
        assert os.path.exists(expected)
        dest_file1_path = os.path.join(expected, file1_name)
        assert os.path.exists(dest_file1_path)
        with open(dest_file1_path, 'r') as f1:
            assert f1.read() == file1_content


@pytest.mark.asyncio
async def test_conflict_rename():
    component = create_component(MoveFolderComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = create_sample_folder(temp_dir)
        await component.process.update_variable('s', folder)
        dest_folder = os.path.join(temp_dir, 'dest_folder')
        os.mkdir(dest_folder)
        expected = os.path.join(dest_folder, os.path.basename(folder))
        os.mkdir(expected)
        await component.process.update_variable('d', dest_folder)
        component.node.inputs = {
            "folderPath": 's',
            "targetFolder": 'd',
            "actionWhenExists": "rename"
        }
        component.node.outputs = {
            "newFolderPath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        expected = os.path.join(dest_folder, os.path.basename(folder) + '_1')
        assert component.process.get_variable('r') == expected
        assert not os.path.exists(folder)
        assert os.path.exists(expected)
        dest_file1_path = os.path.join(expected, file1_name)
        assert os.path.exists(dest_file1_path)
        with open(dest_file1_path, 'r') as f1:
            assert f1.read() == file1_content


@pytest.mark.asyncio
async def test_conflict_error():
    component = create_component(MoveFolderComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = create_sample_folder(temp_dir)
        await component.process.update_variable('s', folder)
        dest_folder = os.path.join(temp_dir, 'dest_folder')
        os.mkdir(dest_folder)
        expected = os.path.join(dest_folder, os.path.basename(folder))
        os.mkdir(expected)
        await component.process.update_variable('d', dest_folder)
        component.node.inputs = {
            "folderPath": 's',
            "targetFolder": 'd',
            "actionWhenExists": "error"
        }
        component.node.outputs = {
            "newFolderPath": 'r'
        }
        with pytest.raises(Exception):
            await component.execute()
        assert os.path.exists(folder)
        assert os.path.exists(expected)
        src_file1_path = os.path.join(folder, file1_name)
        assert os.path.exists(src_file1_path)
        with open(src_file1_path, 'r') as f1:
            assert f1.read() == file1_content
        dest_file1_path = os.path.join(expected, file1_name)
        assert not os.path.exists(dest_file1_path)
