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

from jimuflow.components.core import DeleteFileComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
async def test_delete_existing_file():
    component = create_component(DeleteFileComponent)
    # 创建一个临时文件
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b'123')
        temp_file_name = temp_file.name
    try:
        assert os.path.exists(temp_file_name)
        await component.process.update_variable('f', temp_file_name)

        component.node.inputs = {
            "filePath": 'f',
        }
        assert (await component.execute()) == ControlFlow.NEXT
        assert not os.path.exists(temp_file_name)
    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)


@pytest.mark.asyncio
async def test_delete_not_existing_file():
    component = create_component(DeleteFileComponent)
    # 创建一个临时文件
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(b'123')
        temp_file_name = temp_file.name
    assert not os.path.exists(temp_file_name)
    await component.process.update_variable('f', temp_file_name)

    component.node.inputs = {
        "filePath": 'f',
    }
    assert (await component.execute()) == ControlFlow.NEXT
