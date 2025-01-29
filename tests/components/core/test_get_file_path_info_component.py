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
import time
from pathlib import Path

import pytest

from jimuflow.components.core import GetFilePathInfoComponent
from jimuflow.datatypes import FilePathInfo
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_existing_file():
    component = create_component(GetFilePathInfoComponent)
    # 创建一个临时文件
    start_time = time.time()
    time.sleep(0.01) # 在ubuntu中，临时文件的创建时间会比start_time小一点点，可能是因为文件系统的时间精度问题，所以这里加个sleep
    with tempfile.NamedTemporaryFile(delete=False, prefix="abc.efg", suffix=".txt") as temp_file:
        temp_file.write(b'123')
        temp_file_name = temp_file.name
    try:
        await component.process.update_variable('f', temp_file_name)
        component.node.inputs = {
            "filePath": 'f',
        }
        component.node.outputs = {
            "filePathInfo": 'r'
        }
        assert (await component.execute()) == ControlFlow.NEXT
        result: FilePathInfo = component.process.get_variable('r')
        assert result.exists
        assert result.name == os.path.basename(temp_file_name)
        assert result.name.startswith('abc.efg')
        assert result.isFile
        assert not result.isDirectory
        assert result.extension == '.txt'
        assert result.parent == os.path.dirname(temp_file_name)
        assert result.root == str(Path(temp_file_name).anchor)
        assert result.nameWithoutExtension == os.path.basename(temp_file_name).rsplit('.', 1)[0]
        assert result.nameWithoutExtension.split('abc.efg')
        assert result.size == 3
        assert result.ctime > start_time
        assert result.mtime > start_time
    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)


@pytest.mark.asyncio
async def test_not_existing_file():
    component = create_component(GetFilePathInfoComponent)
    # 创建一个临时文件
    with tempfile.NamedTemporaryFile(prefix="abc.efg", suffix=".txt") as temp_file:
        temp_file.write(b'123')
        temp_file_name = temp_file.name
    await component.process.update_variable('f', temp_file_name)
    component.node.inputs = {
        "filePath": 'f',
    }
    component.node.outputs = {
        "filePathInfo": 'r'
    }
    assert (await component.execute()) == ControlFlow.NEXT
    result: FilePathInfo = component.process.get_variable('r')
    assert not result.exists
    assert not result.isFile
    assert not result.isDirectory
