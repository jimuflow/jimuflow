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
import uuid

import pytest

from jimuflow.components.core import RenameFileComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_not_conflict():
    component = create_component(RenameFileComponent)
    # 创建一个临时文件
    with tempfile.NamedTemporaryFile(delete=False, prefix="old", suffix=".txt") as temp_file:
        temp_file.write(b'123')
        temp_file_name = temp_file.name
    new_file_name = f'{uuid.uuid4()}.txt'
    expected = os.path.join(os.path.dirname(temp_file_name), new_file_name)
    try:
        await component.process.update_variable('f1', temp_file_name)
        await component.process.update_variable('f2', new_file_name)
        component.node.inputs = {
            "filePath": 'f1',
            "newFilename": 'f2',
            "actionWhenExists": 'cancel'
        }
        component.node.outputs = {
            "newFilePath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == expected
        assert os.path.exists(expected)
        assert not os.path.exists(temp_file_name)
    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)
        if os.path.exists(expected):
            os.remove(expected)


@pytest.mark.asyncio
async def test_conflict_cancel():
    component = create_component(RenameFileComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        file1 = os.path.join(temp_dir, 'file1.txt')
        file2 = os.path.join(temp_dir, 'file2.txt')
        with open(file1, 'w') as f:
            f.write('123')
        with open(file2, 'w') as f:
            f.write('456')
        await component.process.update_variable('f1', file1)
        await component.process.update_variable('f2', os.path.basename(file2))
        component.node.inputs = {
            "filePath": 'f1',
            "newFilename": 'f2',
            "actionWhenExists": 'cancel'
        }
        component.node.outputs = {
            "newFilePath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') is None
        assert os.path.exists(file1)
        assert os.path.exists(file2)
        with open(file2, 'r') as f:
            assert f.read() == '456'


@pytest.mark.asyncio
async def test_conflict_override():
    component = create_component(RenameFileComponent)
    with tempfile.TemporaryDirectory() as temp_dir:
        file1 = os.path.join(temp_dir, 'file1.txt')
        file2 = os.path.join(temp_dir, 'file2.txt')
        with open(file1, 'w') as f:
            f.write('123')
        with open(file2, 'w') as f:
            f.write('456')
        await component.process.update_variable('f1', file1)
        await component.process.update_variable('f2', os.path.basename(file2))
        component.node.inputs = {
            "filePath": 'f1',
            "newFilename": 'f2',
            "actionWhenExists": 'overwrite'
        }
        component.node.outputs = {
            "newFilePath": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert component.process.get_variable('r') == file2
        assert not os.path.exists(file1)
        assert os.path.exists(file2)
        with open(file2, 'r') as f:
            assert f.read() == '123'
