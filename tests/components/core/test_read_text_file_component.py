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

import tempfile

import pytest

from jimuflow.components.core import ReadTextFileComponent
from jimuflow.runtime.execution_engine import ControlFlow
from tests.utils import create_component


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "readType,fileEncoding,lines", [
        ('whole', 'system_default', ['hello', 'world']),
        ('whole', 'utf-8', ['hello', '中文']),
        ('lines', 'utf-8', ['hello', '中文']),
        ('whole', 'ascii', ['hello', 'world']),
        ('whole', 'latin-1', ['hello', 'world']),
        ('whole', 'utf-8-sig', ['hello', '中文']),
        ('whole', 'utf-16', ['hello', '中文']),
        ('whole', 'utf-32', ['hello', '中文']),
        ('whole', 'gbk', ['hello', '中文']),
        ('whole', 'gb2312', ['hello', '中文']),
        ('whole', 'gb18030', ['hello', '中文']),
    ])
async def test_execute(readType, fileEncoding, lines):
    component = create_component(ReadTextFileComponent)
    # 创建一个临时文件
    whole_text = '\n'.join(lines)
    encoding = fileEncoding if fileEncoding != 'system_default' else None
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding=encoding) as temp_file:
        temp_file.write(whole_text)
        temp_file_name = temp_file.name
    await component.process.update_variable('f', temp_file_name)
    component.node.inputs = {
        "filePath": 'f',
        "fileEncoding": fileEncoding,
        "readType": readType
    }
    component.node.outputs = {
        "result": "r"
    }
    assert (await component.execute()) == ControlFlow.NEXT
    assert component.process.get_variable('r') == whole_text if readType == 'whole' else lines
