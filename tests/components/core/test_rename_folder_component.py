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

from jimuflow.components.core import RenameFolderComponent
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
    component = create_component(RenameFolderComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = create_sample_folder(temp_dir)
        await component.process.update_variable('f1', folder)
        new_folder_name = random_string(prefix='new_folder_')
        await component.process.update_variable('f2', new_folder_name)
        component.node.inputs = {
            "folderPath": 'f1',
            "newFolderName": 'f2',
            "actionWhenExists": 'cancel'
        }
        component.node.outputs = {
            "newFolderPath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        new_folder = os.path.join(temp_dir, new_folder_name)
        assert component.process.get_variable('r') == new_folder
        assert os.path.exists(new_folder)
        assert not os.path.exists(folder)
        file_path = os.path.join(new_folder, file1_name)
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            assert f.read() == file1_content


@pytest.mark.asyncio
async def test_conflict_cancel():
    component = create_component(RenameFolderComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = create_sample_folder(temp_dir)
        await component.process.update_variable('f1', folder)
        new_folder_name = random_string(prefix='new_folder_')
        new_folder = os.path.join(temp_dir, new_folder_name)
        os.mkdir(new_folder)
        await component.process.update_variable('f2', new_folder_name)
        component.node.inputs = {
            "folderPath": 'f1',
            "newFolderName": 'f2',
            "actionWhenExists": 'cancel'
        }
        component.node.outputs = {
            "newFolderPath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') is None
        assert os.path.exists(folder)
        assert os.path.exists(new_folder)
        assert not os.path.exists(os.path.join(new_folder, os.path.basename(file1_name)))


@pytest.mark.asyncio
async def test_conflict_override():
    component = create_component(RenameFolderComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        folder = create_sample_folder(temp_dir)
        await component.process.update_variable('f1', folder)
        new_folder_name = random_string(prefix='new_folder_')
        new_folder = os.path.join(temp_dir, new_folder_name)
        os.mkdir(new_folder)
        with open(os.path.join(new_folder, file1_name), 'w') as f:
            f.write(random_string())
        await component.process.update_variable('f2', new_folder_name)
        component.node.inputs = {
            "folderPath": 'f1',
            "newFolderName": 'f2',
            "actionWhenExists": 'override'
        }
        component.node.outputs = {
            "newFolderPath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        new_folder = os.path.join(temp_dir, new_folder_name)
        assert component.process.get_variable('r') == new_folder
        assert os.path.exists(new_folder)
        assert not os.path.exists(folder)
        file_path = os.path.join(new_folder, file1_name)
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            assert f.read() == file1_content
