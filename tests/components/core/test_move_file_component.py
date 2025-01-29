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

from jimuflow.components.core import MoveFileComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_not_conflict():
    component = create_component(MoveFileComponent)
    # 创建一个临时文件
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b'123')
        temp_file_name = temp_file.name
    with tempfile.TemporaryDirectory() as temp_dir:
        expected = os.path.join(temp_dir, os.path.basename(temp_file_name))
        try:
            await component.process.update_variable('s', temp_file_name)
            await component.process.update_variable('d', str(temp_dir))
            component.node.inputs = {
                "filePath": 's',
                "targetFolder": 'd',
                "actionWhenExists": "error"
            }
            component.node.outputs = {
                "newFilePath": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            assert component.process.get_variable('r') == expected
            assert not os.path.exists(temp_file_name)
        finally:
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)
            if os.path.exists(expected):
                os.remove(expected)


@pytest.mark.asyncio
async def test_conflict_overwrite():
    component = create_component(MoveFileComponent)
    # 创建一个临时文件
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b'123')
        temp_file_name = temp_file.name
    with tempfile.TemporaryDirectory() as temp_dir:
        expected = os.path.join(temp_dir, os.path.basename(temp_file_name))
        try:
            with open(expected, 'w+b') as f:
                f.write(b'456')
            await component.process.update_variable('s', temp_file_name)
            await component.process.update_variable('d', str(temp_dir))
            component.node.inputs = {
                "filePath": 's',
                "targetFolder": 'd',
                "actionWhenExists": "overwrite"
            }
            component.node.outputs = {
                "newFilePath": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            assert component.process.get_variable('r') == expected
            assert not os.path.exists(temp_file_name)
            with open(expected, 'rb') as f:
                assert f.read() == b'123'
        finally:
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)


@pytest.mark.asyncio
async def test_conflict_rename():
    component = create_component(MoveFileComponent)
    # 创建一个临时文件
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b'123')
        temp_file_name = temp_file.name
    with tempfile.TemporaryDirectory() as temp_dir:
        dest_file = os.path.join(temp_dir, os.path.basename(temp_file_name))
        try:
            with open(dest_file, 'w+b') as f:
                f.write(b'456')
            await component.process.update_variable('s', temp_file_name)
            await component.process.update_variable('d', str(temp_dir))
            component.node.inputs = {
                "filePath": 's',
                "targetFolder": 'd',
                "actionWhenExists": "rename"
            }
            component.node.outputs = {
                "newFilePath": 'r'
            }
            assert (await component.execute()) == ControlFlow.NEXT
            assert component.process.get_variable('r') != dest_file
            assert not os.path.exists(temp_file_name)
            with open(dest_file, 'rb') as f:
                assert f.read() == b'456'
            with open(component.process.get_variable('r'), 'rb') as f:
                assert f.read() == b'123'
        finally:
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)


@pytest.mark.asyncio
async def test_conflict_error():
    component = create_component(MoveFileComponent)
    # 创建一个临时文件
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b'123')
        temp_file_name = temp_file.name
    with tempfile.TemporaryDirectory() as temp_dir:
        dest_file = os.path.join(temp_dir, os.path.basename(temp_file_name))
        try:
            with open(dest_file, 'w+b') as f:
                f.write(b'456')
            await component.process.update_variable('s', temp_file_name)
            await component.process.update_variable('d', str(temp_dir))
            component.node.inputs = {
                "filePath": 's',
                "targetFolder": 'd',
                "actionWhenExists": "error"
            }
            component.node.outputs = {
                "newFilePath": 'r'
            }
            with pytest.raises(Exception):
                await component.execute()
            assert os.path.exists(temp_file_name)
        finally:
            if os.path.exists(temp_file_name):
                os.remove(temp_file_name)
