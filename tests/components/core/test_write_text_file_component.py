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

from jimuflow.components.core import WriteTextFileComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "fileEncoding,actionWhenExists,writeContent", [
        ('system_default', 'append', 'hello'),
        ('utf-8', 'append', 'hello你好'),
        ('utf-8', 'overwrite', 'hello你好'),
        ('ascii', 'append', 'hello'),
        ('latin-1', 'append', 'hello'),
        ('utf-8-sig', 'append', 'hello你好'),
        ('utf-16', 'append', 'hello你好'),
        ('utf-32', 'append', 'hello你好'),
        ('gbk', 'append', 'hello你好'),
        ('gb2312', 'append', 'hello你好'),
        ('gb18030', 'append', 'hello你好'),
    ])
async def test_execute(fileEncoding, actionWhenExists, writeContent):
    component = create_component(WriteTextFileComponent)
    # 创建一个临时文件
    encoding = fileEncoding if fileEncoding != 'system_default' else None
    existing_content = 'abc'
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding=encoding) as temp_file:
        temp_file.write(existing_content)
        temp_file_name = temp_file.name
    try:
        await component.process.update_variable('f', temp_file_name)
        await component.process.update_variable('c', writeContent)

        component.node.inputs = {
            "filePath": 'f',
            "writeContent": 'c',
            "actionWhenExists": actionWhenExists,
            "fileEncoding": fileEncoding,
        }
        assert (await component.execute()) == ControlFlow.NEXT
        with open(temp_file_name, 'r', encoding=encoding) as f:
            whole_text = f.read()
        assert whole_text == existing_content + writeContent if actionWhenExists == 'append' else writeContent
    finally:
        os.remove(temp_file_name)
